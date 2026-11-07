"""Controlla catalog.json prima che arrivi alle app: un file rotto verrebbe scartato da tutti."""
import json
import re
import sys

CADENCES = {"monthly", "bimonthly", "quarterly", "semiannual", "yearly"}
TYPES = {"subscription", "bill", "installment", "trial", "one_off"}

c = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "catalog.json", encoding="utf-8"))
errors = []
err = errors.append

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

for s in c["services"]:
    where = f"servizio {s.get('id')}"
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", s.get("color", "")):
        err(f"{where}: color non valido")
    if not s.get("aliases"):
        err(f"{where}: servono gli alias")
    if not s.get("category"):
        err(f"{where}: serve la categoria")
    if s.get("type", "subscription") not in TYPES or s.get("cadence", "monthly") not in CADENCES:
        err(f"{where}: type o cadence non validi")
    plans = s.get("plans")
    if plans is None:
        continue
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

for t in c["templates"]:
    if t.get("type") not in TYPES or t.get("cadence") not in CADENCES:
        err(f"modello {t.get('id')}: type o cadence non validi")

print("\n".join(errors) or f"OK: versione {c['version']}, {len(ids)} servizi")
sys.exit(1 if errors else 0)
