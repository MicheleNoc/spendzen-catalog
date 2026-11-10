"""Genera i catalog*.json che l'app scarica, da services.json + countries/XX.json.

I catalog*.json non si modificano a mano: si cambia la sorgente e si rilancia `python3 build.py`.
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def load(path):
    return json.load(open(os.path.join(ROOT, path), encoding="utf-8"))


base = load("services.json")
for path in sorted(glob.glob(os.path.join(ROOT, "countries", "*.json"))):
    code = os.path.basename(path)[:-5]
    c = load(path)
    country = None if code == "global" else code
    services = []
    for s in base["services"]:
        # Senza `countries` il servizio è internazionale; altrimenti vale solo nei paesi elencati.
        if "countries" in s and country not in s["countries"]:
            continue
        out = {}
        for k, v in s.items():
            if k == "countries":
                continue
            out[k] = v
            if k == "aliases":
                out.update(c["prices"].get(s["id"], {}))
        services.append(out)
    unknown = set(c["prices"]) - {s["id"] for s in services}
    if unknown:
        raise SystemExit(f"{code}: prezzi per servizi che non esistono in questo paese: {sorted(unknown)}")
    name = {"IT": "catalog.json", "global": "catalog-global.json"}.get(code, f"catalog-{code}.json")
    catalog = {
        "schema": 1,
        "version": c["version"],
        "updated": c["updated"],
        "currency": c["currency"],
        "country": country,
        "popular": c["popular"],
        "services": services,
        "templates": base["templates"],
    }
    with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
        f.write(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    print(f"{name}: versione {c['version']}, {len(services)} servizi, {len(c['prices'])} con prezzi")
