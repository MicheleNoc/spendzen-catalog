# SpendZen catalog

Listino pubblico dei servizi che l'app SpendZen propone quando aggiungi una spesa: nome, logo, alias e, dove verificati, piani e prezzi in Italia.

L'app lo scarica da:

```
https://cdn.jsdelivr.net/gh/MicheleNoc/spendzen-catalog@main/catalog.json
```

La richiesta non contiene dati dell'utente. L'app ha una copia inclusa e usa quella scaricata solo se `version` è più alta.

## Aggiornare un prezzo

1. Modifica `catalog.json`: prezzo, `source.checked` con la data di oggi, e `version` + 1.
2. `python3 check.py` (lo fa anche GitHub a ogni push).
3. Commit su `main`. Le app lo vedono entro circa 12 ore (cache di jsDelivr).

Regole:
- Un prezzo si pubblica solo con `source.url` (pagina ufficiale) e `source.checked`. Se non è verificato, il servizio resta senza `plans` e l'app chiede l'importo.
- `schema` cambia solo se cambia il formato e l'app è già stata aggiornata per leggerlo: le versioni vecchie dell'app ignorano i file con uno `schema` che non conoscono.
- `icon` è la chiave del logo dentro l'app. Un servizio nuovo senza logo nell'app usa `null`.
- `category` usa gli stessi nomi delle categorie dell'app.

Valori ammessi: `cadence` = `monthly`, `bimonthly`, `quarterly`, `semiannual`, `yearly`; `type` = `subscription`, `bill`, `installment`, `trial`, `one_off`.
