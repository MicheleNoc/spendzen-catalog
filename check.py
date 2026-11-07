"""Controlla i cataloghi prima che arrivino alle app: un file rotto verrebbe scartato da tutti.

Uso:
  python3 check.py                      # tutti i catalog*.json
  python3 check.py --base DIR           # in più, confronta i prezzi con i file in DIR (la versione su main)

Con --base una variazione di prezzo oltre il 30% fa fallire il controllo: la PR non si unisce da sola
e serve una revisione a mano.
"""
import glob
import json
import os
import re
import sys

CADENCES = {"monthly", "bimonthly", "quarterly", "semiannual", "yearly"}
TYPES = {"subscription", "bill", "installment", "trial", "one_off"}
MAX_CHANGE = 0.30

# Categorie dell'app (lib/utils/category_icons_mapper.dart). Se l'app ne aggiunge, vanno aggiunte qui.
APP_CATEGORIES = {
    "Adobe", "Affitto", "Altro", "Amazon Prime", "Apple", "Apple Music", "Apple TV+", "Assicurazione",
    "Canva", "Casa e Utenze", "ChatGPT", "Cibo", "Claude", "Condominio", "Crunchyroll", "DAZN",
    "Da classificare", "Discord", "Disney+", "Dropbox", "EA", "Elettronica", "Epic Games", "Figma",
    "Finanza", "GitHub Copilot", "Google", "Google Drive", "Google Gemini", "HBO", "Internet",
    "Istruzione", "Klarna", "Max", "Medicinali", "Monzo", "Mubi", "Mutuo", "N26", "NOW TV", "Netflix",
    "Notion", "Paramount+", "PayPal", "PlayStation", "Prestiti", "Revolut", "Salute", "Samsung",
    "Servizi Cloud", "Shopping", "Sky", "Slack", "Sony", "Spesa Alimentare", "Sport e Benessere",
    "Spotify", "Steam", "Streaming Musica", "Streaming Video", "Svago", "Tasse", "Tecnologia",
    "Telefonia", "Telegram", "Tidal", "Trasporti", "Twitch", "Ubisoft", "Utenze Domestiche",
    "Vacanze e Viaggi", "Veicolo Personale", "Vodafone", "WhatsApp", "Wise", "YouTube", "Zoom", "iCloud+",
}


def check(path, errors):
    def err(msg):
        errors.append(f"{os.path.basename(path)}: {msg}")

    try:
        c = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        err(f"JSON non valido ({e})")
        return None
    if c.get("schema") != 1:
        err("schema deve essere 1 (cambialo solo se l'app sa leggere il nuovo formato)")
    if not isinstance(c.get("version"), int):
        err("version deve essere un intero, da aumentare a ogni modifica")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(c.get("updated", ""))):
        err("updated deve essere AAAA-MM-GG")

    ids = [s["id"] for s in c["services"]]
    if len(ids) != len(set(ids)):
        err("id dei servizi duplicati")
    for p in c["popular"]:
        if p not in ids:
            err(f"popular: {p} non è nei servizi")

    has_prices = False
    for s in c["services"]:
        where = f"servizio {s.get('id')}"
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", s.get("color", "")):
            err(f"{where}: color non valido")
        if not s.get("aliases"):
            err(f"{where}: servono gli alias")
        if s.get("category") not in APP_CATEGORIES:
            err(f"{where}: categoria «{s.get('category')}» non esiste nell'app")
        if s.get("type", "subscription") not in TYPES or s.get("cadence", "monthly") not in CADENCES:
            err(f"{where}: type o cadence non validi")
        plans = s.get("plans")
        if plans is None:
            continue
        has_prices = True
        if not s.get("source", {}).get("url") or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", s["source"].get("checked", "")):
            err(f"{where}: un prezzo senza fonte e data di verifica non si pubblica")
        if s.get("typicalPlan") not in {p["id"] for p in plans}:
            err(f"{where}: typicalPlan non è tra i piani")
        for p in plans:
            if not isinstance(p.get("price"), (int, float)) or not 0 < p["price"] < 1000:
                err(f"{where}/{p.get('id')}: prezzo non valido")
            if p.get("cadence") not in CADENCES:
                err(f"{where}/{p.get('id')}: cadence non valida")
            if not p.get("name", {}).get("it") or not p["name"].get("en"):
                err(f"{where}/{p.get('id')}: serve il nome in it ed en")

    if has_prices and not c.get("currency"):
        err("un catalogo con prezzi deve dichiarare currency")

    for t in c["templates"]:
        if t.get("type") not in TYPES or t.get("cadence") not in CADENCES:
            err(f"modello {t.get('id')}: type o cadence non validi")
        if t.get("category") not in APP_CATEGORIES:
            err(f"modello {t.get('id')}: categoria «{t.get('category')}» non esiste nell'app")
    return c


def prices(c):
    return {(s["id"], p["id"]): p["price"] for s in c["services"] for p in s.get("plans") or []}


def compare(path, new, base_dir, errors):
    old_path = os.path.join(base_dir, os.path.basename(path))
    if not os.path.exists(old_path):
        return
    old = json.load(open(old_path, encoding="utf-8"))
    name = os.path.basename(path)
    if new != old and new.get("version", 0) <= old.get("version", 0):
        errors.append(f"{name}: il file è cambiato ma version non è aumentata ({old.get('version')})")
    before, after = prices(old), prices(new)
    for key, price in after.items():
        if key in before and abs(price - before[key]) / before[key] > MAX_CHANGE:
            errors.append(f"{name}: {key[0]}/{key[1]} passa da {before[key]} a {price} (oltre il "
                          f"{int(MAX_CHANGE * 100)}%): serve una revisione a mano")


def main():
    args = sys.argv[1:]
    base = args[args.index("--base") + 1] if "--base" in args else None
    files = sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "catalog*.json")))
    errors = []
    for f in files:
        c = check(f, errors)
        if c is not None and base:
            compare(f, c, base, errors)
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print("OK: " + ", ".join(os.path.basename(f) for f in files))


if __name__ == "__main__":
    main()
