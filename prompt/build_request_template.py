"""Genera i due corpi di richiesta alla Responses API di OpenAI:

- request_pulizia_blocco.json: pulisce un blocco di trascrizione (output testo);
- request_struttura.json: dal testo pulito produce titolo, struttura e mappa
  (output JSON con schema strict).

Senza "model" e "input": li aggiunge chi chiama (Comando Rapido o script di test).
Il vocabolario dei nomi propri viene da vocabolario_trascrizione.txt.
Rilanciare dopo ogni modifica ai prompt o al vocabolario.
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
VOCAB = (HERE / "vocabolario_trascrizione.txt").read_text(encoding="utf-8").strip()


def prompt(nome):
    return (HERE / nome).read_text(encoding="utf-8").strip().replace("{{VOCABOLARIO}}", VOCAB)


schema = {
    "type": "object",
    "additionalProperties": False,
    "required": ["titolo", "struttura", "mappa_markdown"],
    "properties": {
        "titolo": {"type": "string"},
        "struttura": {"type": "string"},
        "mappa_markdown": {"type": "string"},
    },
}

richieste = {
    "request_pulizia_blocco.json": {"instructions": prompt("prompt_pulizia_blocco.md")},
    "request_struttura.json": {
        "instructions": prompt("prompt_struttura.md"),
        "text": {"format": {"type": "json_schema", "name": "memo_vocale", "strict": True, "schema": schema}},
    },
}

for nome, corpo in richieste.items():
    (HERE / nome).write_text(json.dumps(corpo, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"scritto {HERE / nome}")
