"""Prova end-to-end delle due chiamate che farà il Comando Rapido.

Uso:
  python3 test/prova_api.py AUDIO.m4a [modello_pulizia ...] [--riusa]

Esempio:
  python3 test/prova_api.py test/audio/prova1.m4a gpt-5-mini gpt-4.1-mini

1) trascrive AUDIO con OpenAI (stesso endpoint del Comando Rapido);
2) per ogni modello pulisce la trascrizione a blocchi (request_pulizia_blocco.json)
   e poi produce titolo, struttura e mappa (request_struttura.json);
   --riusa salta la trascrizione se è già salvata in test/risultati/;
3) salva i risultati in test/risultati/ e stampa token e tempi.

La chiave si legge da .env (OPENAI_API_KEY), mai da riga di comando.
Solo libreria standard: niente pip install.
"""
import json
import sys
import time
import uuid
import base64
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRASCRIZIONE_MODELLO = "gpt-4o-transcribe"


def chiave():
    for riga in (ROOT / ".env").read_text().splitlines():
        if riga.startswith("OPENAI_API_KEY="):
            k = riga.split("=", 1)[1].strip().strip('"')
            if k and not k.startswith("sk-xxx"):
                return k
    sys.exit("Manca OPENAI_API_KEY in .env")


def chiama(url, corpo, tipo, key):
    req = urllib.request.Request(url, data=corpo, method="POST", headers={
        "Authorization": f"Bearer {key}", "Content-Type": tipo})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Errore {e.code} da {url}:\n{e.read().decode()}")


def trascrivi(audio, key, modello=TRASCRIZIONE_MODELLO, extra=None):
    confine = uuid.uuid4().hex
    # chunking_strategy=auto: senza, i memo lunghi (>~10 min) vengono troncati
    vocab = (ROOT / "prompt/vocabolario_trascrizione.txt").read_text().strip()
    campi = {"model": modello, "language": "it", "chunking_strategy": "auto", "prompt": vocab, **(extra or {})}
    parti = [
        f'--{confine}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
        for k, v in campi.items()
    ] + [
        f'--{confine}\r\nContent-Disposition: form-data; name="file"; filename="{audio.name}"\r\n'
        f'Content-Type: audio/mp4\r\n\r\n'.encode() + audio.read_bytes() + b"\r\n",
        f"--{confine}--\r\n".encode(),
    ]
    r = chiama("https://api.openai.com/v1/audio/transcriptions", b"".join(parti),
               f"multipart/form-data; boundary={confine}", key)
    return r["text"]


SOGLIA_PAROLE = 300  # stesso valore del Comando Rapido


def responses(template, testo, modello, key):
    corpo = json.loads((ROOT / "prompt" / template).read_text())
    corpo["model"] = modello
    corpo["input"] = testo
    if modello.startswith(("gpt-5", "o")):
        corpo["reasoning"] = {"effort": "minimal"}
    r = chiama("https://api.openai.com/v1/responses", json.dumps(corpo).encode(),
               "application/json", key)
    # Stessa logica del Comando Rapido: ultimo elemento di output -> content[0].text
    return r["output"][-1]["content"][0]["text"], r.get("usage", {})


def blocchi(trascrizione):
    """Stessa logica del Comando Rapido: accumula righe finché il blocco
    supera SOGLIA_PAROLE, poi lo chiude. L'ultimo blocco esce a fine ciclo."""
    blocco = ""
    for riga in trascrizione.split("\n"):
        blocco = f"{blocco}\n{riga}"
        if len(blocco.split()) > SOGLIA_PAROLE - 1:
            yield blocco.strip()
            blocco = ""
    if blocco.strip():
        yield blocco.strip()


def dividi_struttura(t):
    """Stessa logica del Comando Rapido: divide sul separatore @@@ e
    pretende esattamente tre parti (titolo, struttura, mappa)."""
    parti = [x.strip() for x in t.split("@@@")]
    if len(parti) != 3 or not all(parti):
        raise ValueError(f"risposta struttura non in 3 parti: {t[:300]!r}")
    return {"titolo": parti[0], "struttura": parti[1], "mappa_markdown": parti[2]}


def pulisci(trascrizione, modello, key):
    uso = {"input_tokens": 0, "output_tokens": 0, "chiamate": 0}
    pulito = []
    for b in blocchi(trascrizione):
        t, u = responses("request_pulizia_blocco.json", b, modello, key)
        pulito.append(t.strip())
        uso["input_tokens"] += u.get("input_tokens", 0)
        uso["output_tokens"] += u.get("output_tokens", 0)
        uso["chiamate"] += 1
    testo_pulito = "\n\n".join(pulito)
    t, u = responses("request_struttura.json", testo_pulito, modello, key)
    uso["input_tokens"] += u.get("input_tokens", 0)
    uso["output_tokens"] += u.get("output_tokens", 0)
    uso["chiamate"] += 1
    dati = dividi_struttura(t)
    dati["testo_pulito"] = testo_pulito
    return dati, uso


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    audio = Path(sys.argv[1])
    modelli = sys.argv[2:] or ["gpt-4.1-mini"]
    key = chiave()
    out = ROOT / "test/risultati"
    out.mkdir(exist_ok=True)
    salvata = out / f"{audio.stem}__trascrizione.txt"

    if "--riusa" in modelli and salvata.exists():
        modelli.remove("--riusa")
        trascrizione = salvata.read_text()
        print(f"== TRASCRIZIONE riusata da {salvata.name}")
    else:
        modelli = [m for m in modelli if m != "--riusa"]
        t = time.time()
        trascrizione = trascrivi(audio, key)
        print(f"\n== TRASCRIZIONE ({time.time()-t:.1f}s) ==\n{trascrizione}\n")
        salvata.write_text(trascrizione)
    n_tr = len(trascrizione.split())

    for m in modelli or ["gpt-4.1-mini"]:
        t = time.time()
        dati, uso = pulisci(trascrizione, m, key)
        durata = time.time() - t
        mappa = base64.b64encode(dati["mappa_markdown"].encode()).decode()
        dati["_link_mappa_locale"] = f"http://localhost:8765/index.html#{mappa}"
        dati["_uso"] = uso
        dati["_secondi"] = round(durata, 1)
        n_pu = len(dati["testo_pulito"].split())
        (out / f"{audio.stem}__{m}.json").write_text(json.dumps(dati, ensure_ascii=False, indent=2))
        print(f"== {m} ({durata:.1f}s, {uso['chiamate']} chiamate, input {uso['input_tokens']} tok, "
              f"output {uso['output_tokens']} tok, testo pulito {n_pu}/{n_tr} parole = {100*n_pu//n_tr}%) ==")
        print(f"TITOLO: {dati['titolo']}\n\n{dati['struttura']}\n")


if __name__ == "__main__":
    main()
