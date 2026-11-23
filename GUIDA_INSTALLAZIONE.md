# Memo AI — installazione sull'iPhone

## 1. Importa il Comando Rapido
1. Manda `shortcut/Memo_AI.shortcut` all'iPhone (AirDrop, oppure iCloud Drive → app File → tocca il file).
2. Tocca **Aggiungi comando rapido**. Ti chiede:
   - **API key di OpenAI**: incollala qui. Resta solo dentro il Comando Rapido.
   - **Indirizzo del visualizzatore mappe**: lascia il valore proposto (`https://robertomicarelli.github.io/Claude-Memo-Voice/viewer/`).

## 2. Aggiungi le 5 azioni «Crea nota» (una volta sola)
iOS non permette di scegliere la cartella di Note da una variabile, quindi va fatto a mano.
Apri il Comando Rapido. In fondo c'è il menu «Dove salvo il memo?». In ognuno dei rami Casa, Lavoro, Tempo Libero, Idee e Varie c'è un commento «AGGIUNGI QUI».
**Primo ramo (Lavoro):**
1. Tocca **Cerca azioni**, in basso, e scrivi `Crea nota`.
2. Tieni premuto il risultato **Crea nota** (icona gialla di Note) e, senza staccare il dito, trascinalo subito sotto il commento giallo del ramo **Lavoro**, prima della riga «Tempo Libero». Se lo tocchi soltanto, finisce in fondo al comando: in quel caso tienilo premuto e trascinalo su.
3. Nell'azione tocca il campo blu del contenuto (il testo della nota), poi **Seleziona variabile**, poi tocca più in alto l'azione **Testo nota**, quella che inizia con Titolo e Struttura.
4. Tocca la freccia **>** dell'azione per vedere tutti i campi. Tocca **Cartella** e scegli **Lavoro**. Lascia **Nome** vuoto (il titolo è la prima riga della nota) e disattiva **Apri in caso di esecuzione**.
5. Facoltativo: elimina il commento giallo con la **X**.

**Gli altri 4 rami, più in fretta:** tieni premuta l'azione «Crea nota» appena fatta → **Duplica**. Trascina la copia sotto il commento di **Tempo Libero** e cambia solo la cartella. Ripeti per **Idee**, **Varie** e **Casa**.

Le 5 cartelle devono esistere già in Note. Se sono sottocartelle, come quelle dentro NOTE-PEBBLE, all'inizio il selettore mostra solo le cartelle principali: usa il campo **Cerca** in alto e scrivi il nome, per esempio `IDEE`.

## 3. Pulsante sulla schermata di blocco (iOS 18 o successivi)
Tieni premuto sulla schermata di blocco → **Personalizza** → **Schermata di blocco**. Tocca uno dei due pulsanti in basso → **Comandi Rapidi** → **Memo AI**.

## 4. Primo avvio
- Concedi il **microfono** e l'accesso a **api.openai.com** quando te li chiede, scegliendo «Consenti sempre».
- La registrazione parte subito. Per fermarla tocca lo schermo.
- Compare il menu delle cartelle: dopo 5–10 secondi per un memo breve, circa 1 minuto per un memo di 15 minuti. Il tempo dipende dai blocchi da ripulire. «Non salvare» mostra solo il risultato.

## Cosa contiene la nota
Titolo, poi la struttura (sintesi, punti chiave, cose da fare, domande aperte), poi il link alla mappa mentale (lungo, con dei punti: è normale) e infine il testo completo ripulito. Il link apre la mappa interattiva in Safari.
