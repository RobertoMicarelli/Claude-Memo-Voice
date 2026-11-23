# AGENTE-VOCE — Memo AI per iPhone

## Contesto e obiettivo
Un Comando Rapido iOS che, avviato dalla schermata di blocco, fa queste cose:
- registra la voce;
- la trascrive con OpenAI;
- la fa ripulire da un modello GPT a blocchi di circa 300 parole, poi ne ricava la struttura da memo e la mappa mentale markmap;
- se lo scegli dal menu finale, salva la nota in una cartella di Note (Lavoro, Tempo Libero, Idee o Varie).

## Cronologia del lavoro (2026-11-23)
1. **Richiesta iniziale.** App iPhone attivata con volume giù + tasto laterale. Registra con Memo Vocali, passa la trascrizione a ChatGPT e produce testo pulito, struttura e mappa markmap. Salva in Note per cartella.
2. **Verifica di fattibilità.** Tre vincoli di iOS cambiano il progetto:
   - la combinazione di tasti è riservata al sistema;
   - Memo Vocali non ha API;
   - le app non possono scrivere in Note.

   Scelte confermate da Roberto: Comando Rapido, pulsante sulla schermata di blocco, trascrizione OpenAI, menu delle cartelle a fine registrazione.
3. **Primi componenti:**
   - prompt unico con schema JSON;
   - visualizzatore markmap con il markdown nel frammento `#`, testato nel browser;
   - script di test API;
   - audio sintetico (`say -v Alice`).
4. **Comando Rapido generato in Python e firmato** con `shortcuts sign`. Dai metadati di Note.app risulta che la cartella di «Crea nota» non accetta variabili: per questo ci sono 4 rami da completare a mano.
5. **Test sull'audio sintetico**, gpt-5-mini contro gpt-4.1-mini: entrambi fedeli. Scelto **gpt-4.1-mini**.
6. **Test su un memo reale di 14 minuti.** Ha fatto emergere tre problemi:
   - trascrizione troncata, risolta con `chunking_strategy=auto`;
   - testo pulito riassunto, tra il 38% e il 57% delle parole con tutti i modelli provati;
   - DA FARE con voci dedotte e nomi propri sbagliati.

   Correzioni: regola esplicita nel prompt e vocabolario dei nomi.
7. **Pulizia a blocchi**, cioè blocchi di circa 300 parole più una chiamata finale per la struttura. Il testo pulito arriva all'89%. Il Comando Rapido è stato rigenerato (90 azioni) e controllato strutturalmente.
8. **Salvataggio** nella repo `RobertoMicarelli/Claude-Memo-Voice`, creata privata e poi resa pubblica su richiesta. Controllo preliminare: nessuna chiave e nessun audio, email dei commit noreply.
9. **GitHub Pages** attivato su `main`. Il visualizzatore è online e l'indirizzo è aggiornato nel Comando Rapido.
10. **Crash all'import:** Comandi Rapidi si apriva e si chiudeva subito, sia su iPhone sia su Mac. Corretto il formato del campo `file` nella chiamata di trascrizione.

## Decisioni (2026-11-23)
- **Comando Rapido e non app nativa.** Le app di terze parti non possono scrivere in Note. In più il Mac è Intel e un account sviluppatore costerebbe 99 $ l'anno.
- **Avvio dal pulsante sulla schermata di blocco.** Volume giù + tasto laterale è riservato a iOS: nessuna app lo può intercettare.
- **Trascrizione OpenAI (`gpt-4o-transcribe`) e non Memo Vocali.** Memo Vocali non espone la trascrizione a nessuna API.
- **Cartella scelta da un menu a fine registrazione.** In «Crea nota» la cartella è un'entità che non accetta variabili, verificato in `Notes.app/.../extract.actionsdata`. Per questo ci sono 4 rami con l'azione aggiunta a mano.
- **Mappa mentale tramite pagina statica `viewer/index.html`.** Il markdown viaggia in base64 nel frammento `#` dell'URL, che non viene mai inviato al server. Le Note non possono mostrare markmap.
- **Modello di pulizia da scegliere con `test/prova_api.py`.** Scelto `gpt-4.1-mini` (2026-11-23): costo pari a gpt-5-mini, mappe più gerarchiche.
- **Pulizia a blocchi (2026-11-23).** Le righe della trascrizione si accumulano finché superano 300 parole; ogni blocco si ripulisce con una chiamata a parte. Poi una chiamata finale ricava titolo, struttura e mappa dal testo pulito. Così la completezza è garantita dalla logica e non dal prompt.
- **`chunking_strategy=auto` nella trascrizione.** Senza questo parametro i memo lunghi vengono troncati.

## Struttura
| Path | Cosa |
|---|---|
| `prompt/prompt_pulizia_blocco.md` | Prompt di pulizia del singolo blocco (output testo) |
| `prompt/prompt_struttura.md` | Prompt per titolo, struttura e mappa (output JSON strict) |
| `prompt/vocabolario_trascrizione.txt` | Nomi propri, usati sia nella trascrizione (`prompt`) sia nei due prompt |
| `prompt/build_request_template.py` → `request_pulizia_blocco.json`, `request_struttura.json` | Corpi delle chiamate alla Responses API |
| `viewer/index.html` | Visualizzatore markmap (d3 7.9.0, markmap 0.18.12) |
| `test/prova_api.py` | Test end-to-end con la stessa logica a blocchi del Comando Rapido; legge la chiave da `.env`; `--riusa` salta la trascrizione già salvata |
| `test/audio/prova1.m4a` | Audio sintetico di prova con intercalari (escluso da git) |
| `shortcut/genera_shortcut.py` | Genera `Memo_AI_unsigned.shortcut` |
| `shortcut/Memo_AI.shortcut` | Versione firmata (`shortcuts sign --mode anyone`) da importare |
| `GUIDA_INSTALLAZIONE.md` | Passi sull'iPhone |

Rigenerazione dopo una modifica al prompt o al modello:
```
python3 prompt/build_request_template.py
python3 shortcut/genera_shortcut.py gpt-4.1-mini
shortcuts sign --mode anyone --input shortcut/Memo_AI_unsigned.shortcut --output shortcut/Memo_AI.shortcut
```

## Stato e verifiche
- Verificato: il visualizzatore disegna la mappa da un link base64, accenti compresi, in un browser desktop.
- Verificato: il generatore produce 90 azioni e il file firmato ha la firma `AEA1`. Un controllo strutturale non trova errori: blocchi If, Ripeti e Menu chiusi, ogni variabile definita prima dell'uso, JSON validi.
- **Non verificato:** l'import sull'iPhone e l'esecuzione reale del Comando Rapido. Il file è generato a mano, fuori dall'editor di Apple: gli identificativi delle azioni vengono dal formato noto, non da un export.
- Verificato (2026-11-23): le chiamate API funzionano end-to-end su `test/audio/prova1.m4a`, un audio sintetico di circa 30 secondi.
  - **Trascrizione:** 4 secondi. Il refuso «grutti» è stato corretto in «gruppi» da entrambi i modelli.
  - **Pulizia:** entrambi i modelli sono fedeli alla trascrizione, senza aggiunte inventate, e gestiscono l'autocorrezione «anzi no».
  - **gpt-5-mini:** 7,2 s, 639 token in ingresso e 376 in uscita.
  - **gpt-4.1-mini:** 7,4 s, 641 token in ingresso e 337 in uscita, con una mappa più gerarchica.
  - Risultati completi in `test/risultati/`.
  - Manca ancora la prova su una registrazione reale.
- **Visualizzatore online** su GitHub Pages: `https://robertomicarelli.github.io/Claude-Memo-Voice/viewer/`, già impostato come valore predefinito nel Comando Rapido.

### Test sul memo reale
- **Memo reale di 14 minuti (2026-11-23, registrazione di Memo Vocali in `test/audio/`, esclusa dal repo; dialogo dimostrativo).**
  - **Trascrizione troncata.** Senza parametri gpt-4o-transcribe si è fermato a metà frase e ha perso l'ultimo minuto. Risolto con `chunking_strategy=auto`, ora sia nello script sia nel Comando Rapido: 1.827 parole, arriva fino alla fine.
  - **Testo pulito riassunto invece che riscritto.**

    | Modello | Parole del testo pulito | % della trascrizione |
    |---|---|---|
    | gpt-4.1-mini | 503–863 | 28–47% |
    | gpt-4.1 | 697 | 38% |
    | gpt-5-mini | 1.047 | 57% |

    Rafforzare il prompt non basta. **Risolto con la pulizia a blocchi:** gpt-4.1-mini arriva a 1.634 parole su 1.827 (89%), con 7 chiamate in 41 s e circa 7.600 token in ingresso e 3.000 in uscita. Il finale dell'audio è presente e fedele. Sul memo breve: 75%, 2 chiamate, 6,7 s.
  - **DA FARE e DOMANDE APERTE gonfiate con cose dedotte.** Ridotte con una regola esplicita nel prompt. gpt-4.1 a volte scrive «(nessuna azione…)» invece di omettere la sezione.
  - **Nomi propri** («Cloud Code» al posto di Claude Code, «Whisperflow» al posto di Wispr Flow).
    - Il vocabolario passato alla trascrizione (`prompt/vocabolario_trascrizione.txt`) aiuta solo in parte.
    - Il glossario nel prompt di pulizia veniva ignorato con il prompt unico. Con i blocchi funziona quasi sempre: resta 1 «Cloud Code».
  - **Ancora aperto:** la struttura a volte scrive «DOMANDE APERTE • (nessuna)» invece di omettere la sezione, ed è un difetto estetico. In un punto attribuisce il «+20-30%» a produttività e qualità insieme, mentre nell'audio si riferisce solo alla qualità.

## Moduli di dominio caricati
Programmazione (`~/.claude/moduli/Programmazione.md`).

## Modifiche alla memoria persistente
Nessuna.

## Revisioni e incidenti
- Il pannello browser di Claude apre i file locali come `data:` e perde il frammento `#`. Il visualizzatore si testa con `python3 -m http.server 8765` dentro `viewer/`.
- `shortcuts sign` stampa righe «ERROR: Unrecognized attribute string flag». Sono innocue: il file firmato viene prodotto lo stesso.
- **Crash all'import del Comando Rapido (2026-11-23).** Comandi Rapidi si apriva e si chiudeva subito.
  - **Causa:** il log del Mac (`log show --predicate 'process == "Shortcuts"'`) riporta `State for WFPropertyListParameterValue is not of the expected class` in `WFDictionaryParameterKeyValuePair`. Il campo `file` del modulo (WFItemType 5) era serializzato come semplice `WFTextTokenAttachment`.
  - **Correzione:** va avvolto in `{"Value": …, "WFSerializationType": "WFTokenAttachmentParameterState"}`.
  - **Verifica:** il Mac riapre il file senza crash. Come verificare in futuro: `open shortcut/Memo_AI.shortcut` sul Mac e controllare il log, perché sul Mac il problema si riproduce come sull'iPhone.
- Il database dei Comandi Rapidi (`~/Library/Shortcuts`) non è leggibile dal terminale per via della protezione TCC. Gli identificativi di Note sono stati presi dai metadati App Intents di Note.app.

## Cosa NON è stato toccato
La libreria dei Comandi Rapidi e le Note: non è stato importato né creato nulla. Il Comando Rapido a blocchi non è mai stato eseguito su un dispositivo. Nessun servizio esterno oltre a OpenAI (test) e GitHub (repo pubblica + Pages). Audio, trascrizioni e risultati dei test restano solo in locale (`test/audio/`, `test/risultati/`, in `.gitignore`).
