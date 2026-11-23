# Memo AI — installazione sull'iPhone

## 1. Importa il Comando Rapido
1. Manda `shortcut/Memo_AI.shortcut` all'iPhone (AirDrop, oppure iCloud Drive → app File → tocca il file).
2. Tocca **Aggiungi comando rapido**. Ti chiede:
   - **API key di OpenAI**: incollala qui. Resta solo dentro il Comando Rapido.
   - **Indirizzo del visualizzatore mappe**: lascia il valore proposto (`https://robertomicarelli.github.io/Claude-Memo-Voice/viewer/`).

## 2. Aggiungi le 4 azioni «Crea nota» (una volta sola)
iOS non permette di scegliere la cartella di Note da una variabile, quindi va fatto a mano.
Apri il Comando Rapido. In fondo c'è il menu «Dove salvo il memo?». In ognuno dei rami Lavoro, Tempo Libero, Idee e Varie c'è un commento «AGGIUNGI QUI».
1. Cerca l'azione **Crea nota** (app Note) e trascinala sotto il commento.
2. Nel campo del contenuto metti la variabile **Testo nota**.
3. Tocca **Cartella** e scegli la cartella del ramo.
4. Cancella il commento (facoltativo).

Le 4 cartelle devono esistere già in Note.

## 3. Pulsante sulla schermata di blocco (iOS 18 o successivi)
Tieni premuto sulla schermata di blocco → **Personalizza** → **Schermata di blocco**. Tocca uno dei due pulsanti in basso → **Comandi Rapidi** → **Memo AI**.

## 4. Primo avvio
- Concedi il **microfono** e l'accesso a **api.openai.com** quando te li chiede, scegliendo «Consenti sempre».
- La registrazione parte subito. Per fermarla tocca lo schermo.
- Compare il menu delle cartelle: dopo 5–10 secondi per un memo breve, circa 1 minuto per un memo di 15 minuti. Il tempo dipende dai blocchi da ripulire. «Non salvare» mostra solo il risultato.

## Cosa contiene la nota
Titolo, poi la struttura (sintesi, punti chiave, cose da fare, domande aperte), poi il link alla mappa mentale e infine il testo completo ripulito.
