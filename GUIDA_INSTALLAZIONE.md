# Memo AI — installazione

Due Comandi Rapidi, sincronizzati tra Mac e iPhone tramite iCloud:

| Comando | Cosa fa | Quando si reimporta |
|---|---|---|
| **Memo_AI_Motore** | Riceve l'audio, lo trascrive, lo pulisce e restituisce il testo della nota con il link alla mappa | A ogni correzione. Si fa sul Mac: **Sostituisci** e poi incolla la chiave API |
| **Memo_AI** | Registra, chiama il Motore, mostra il menu delle cartelle e salva in Note | Una volta sola |

## 1. Motore (sul Mac)
1. Apri `shortcut/Memo_AI_Motore.shortcut` e scegli **Aggiungi comando rapido**, oppure **Sostituisci** se esiste già.
2. Incolla la **API key di OpenAI** e lascia l'indirizzo del visualizzatore così com'è.
3. Test da Terminale:
   ```
   shortcuts run Memo_AI_Motore --input-path test/audio/prova1.m4a --output-path nota.txt
   ```

## 2. Comando principale (una volta sola, comodo sul Mac)
1. Apri `shortcut/Memo_AI.shortcut`. Se esiste già un Memo_AI, scegli **Sostituisci**.
2. Controlla l'azione **Esegui comando rapido**: deve indicare **Memo_AI_Motore**. Se è vuota, cliccaci sopra e sceglilo.
3. Nel menu «Dove salvo il memo?» ogni ramo (Casa, Lavoro, Tempo Libero, Idee, Varie) ha un commento «AGGIUNGI QUI». Sotto ciascun commento:
   - aggiungi **Crea nota** (app Note);
   - **Contenuto:** la variabile **Testo nota**, cioè l'output di «Esegui comando rapido»;
   - **Nome:** vuoto, perché il titolo è la prima riga della nota;
   - **Cartella:** scegli la cartella del ramo. Per le sottocartelle di NOTE-PEBBLE usa il campo **Cerca** nel selettore;
   - **Apri in caso di esecuzione:** disattivato.

   Fai la prima a mano e le altre con **Duplica**, cambiando solo la cartella.

## 3. Pulsante sulla schermata di blocco (iPhone, iOS 18 o successivi)
Tieni premuto sulla schermata di blocco → **Personalizza** → **Schermata di blocco** → tocca un pulsante in basso → **Comandi Rapidi** → **Memo_AI**.

## 4. Uso
- Alla prima esecuzione concedi il **microfono** e l'accesso a **api.openai.com**, scegliendo «Consenti sempre».
- La registrazione parte subito. Per fermarla tocca lo schermo.
- Dopo 5–10 secondi per un memo breve, circa 1 minuto per un memo di 15 minuti, compare il menu delle cartelle. «Non salvare» mostra solo il risultato.
- Se qualcosa va storto compare un messaggio che inizia con **ERRORE:**, per esempio «nessuna voce riconosciuta nella registrazione».

## Cosa contiene la nota
Titolo, poi la struttura (sintesi, punti chiave, cose da fare, domande aperte), poi il link alla mappa mentale e infine il testo completo ripulito. Il link è lungo e pieno di punti, ed è normale. La mappa si apre in Safari, sempre su sfondo bianco.
