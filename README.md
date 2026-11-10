# SpendZen catalog

Listino pubblico dei servizi che l'app SpendZen propone quando aggiungi una spesa: nome, logo, alias e, dove verificati, piani e prezzi.

## File per paese

| File | Per chi | Prezzi |
|---|---|---|
| `catalog.json` | Italia (regione del dispositivo IT) | sì, in EUR |
| `catalog-XX.json` | paese con codice ISO `XX` (es. `catalog-DE.json`), quando esiste | sì, nella valuta del paese |
| `catalog-global.json` | tutti gli altri paesi | no: solo marchi internazionali, l'importo lo scrive l'utente |

L'app scarica solo il file della regione del dispositivo: `catalog.json` per l'Italia, altrimenti prova `catalog-XX.json` e, se non c'è, usa `catalog-global.json`. I prezzi si mostrano solo se la valuta scelta nell'app coincide con `currency` del file. Le versioni dell'app precedenti leggono solo `catalog.json`.

Indirizzo: `https://cdn.jsdelivr.net/gh/MicheleNoc/spendzen-catalog@main/<file>`. La richiesta non contiene dati dell'utente, e l'app la fa al massimo una volta a settimana. L'app ha una copia inclusa e usa quella scaricata solo se `version` è più alta.

## Sorgenti

I `catalog*.json` sono **generati** da `build.py` e non si modificano a mano. Le sorgenti sono:

- `services.json`: i servizi (nome, logo, alias, categoria) e i modelli, una volta sola per tutti i paesi. Un servizio con `"countries": ["IT"]` esiste solo in quei paesi; senza, è internazionale.
- `countries/XX.json`: per ogni paese `version`, `updated`, `currency`, `popular` e i `prices` (per id del servizio: `source`, `typicalPlan`, `plans`). `countries/global.json` non ha prezzi.

Aggiungere un paese = aggiungere `countries/XX.json` con i soli prezzi verificati.

## Aggiornare

1. Modifica la sorgente. Per un prezzo: `countries/XX.json`, con `source.checked` di oggi e `version` + 1. Se cambi `services.json`, aumenta `version` in tutti i file di `countries/`.
2. `python3 build.py && python3 check.py` (lo fa anche GitHub a ogni push e su ogni PR, e fallisce se i file generati non corrispondono alle sorgenti).
3. Meglio una PR che un push su `main`: sulle PR `check.py --base` confronta i prezzi con `main` e fallisce se uno cambia oltre il 30%, così una lettura sbagliata non arriva alle app senza una revisione. Le app vedono `main` entro circa 12 ore (cache di jsDelivr).

Una routine mensile rilegge ogni `source.url` e apre una PR con i prezzi cambiati e le date di verifica aggiornate. L'app non propone un prezzo verificato da più di 6 mesi: se la routine si ferma, torna a chiedere l'importo.

Regole (controllate da `check.py`):
- Un prezzo si pubblica solo con `source.url` (pagina ufficiale) e `source.checked`. Se non è verificato, il servizio resta senza `plans` e l'app chiede l'importo. Mai prezzi "a partire da".
- Un file con prezzi dichiara `currency`.
- `category` è obbligatoria e usa i nomi delle categorie dell'app (elenco in `check.py`, da allineare se l'app ne aggiunge). Se l'app ha la categoria del marchio (Netflix, Spotify...), si usa quella: è lei a dare il logo.
- `schema` cambia solo se cambia il formato e l'app è già stata aggiornata per leggerlo: le versioni vecchie dell'app ignorano i file con uno `schema` che non conoscono.
- `icon` è la chiave del logo dentro l'app. Un servizio nuovo senza logo nell'app usa `null`.
- `type` e `cadence` sul servizio sono facoltativi (`subscription`, `monthly`) e valgono quando non ci sono `plans`: per esempio `bill` e `bimonthly` per i fornitori di energia.

Valori ammessi: `cadence` = `monthly`, `bimonthly`, `quarterly`, `semiannual`, `yearly`; `type` = `subscription`, `bill`, `installment`, `trial`, `one_off`.
