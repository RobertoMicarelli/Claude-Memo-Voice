"""Genera il Comando Rapido "Memo AI" (file .shortcut non firmato).

Uso:
  python3 shortcut/genera_shortcut.py [modello_pulizia]
  shortcuts sign --mode anyone --input shortcut/Memo_AI_unsigned.shortcut --output shortcut/Memo_AI.shortcut

Le azioni "Crea nota" NON sono generate: la cartella di Note si può scegliere
solo a mano (parametro entità senza input da variabile, verificato in
Notes.app/Contents/Resources/Metadata.appintents). Il file mette un commento
in ogni ramo del menu dove aggiungerle.
"""
import json
import plistlib
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELLO = sys.argv[1] if len(sys.argv) > 1 else "gpt-4.1-mini"
TRASCRIZIONE = "gpt-4o-transcribe"
CARTELLE = ["Casa", "Lavoro", "Tempo Libero", "Idee", "Varie"]

azioni = []


def uid():
    return str(uuid.uuid4()).upper()


def add(ident, params, out_uuid=None):
    if out_uuid:
        params = {"UUID": out_uuid, **params}
    azioni.append({"WFWorkflowActionIdentifier": ident, "WFWorkflowActionParameters": params})
    return len(azioni) - 1


def NV(nome):
    """Variabile con nome (Imposta variabile) o magica (es. "Repeat Item")."""
    return ("__VAR__", nome)


def rif(u, nome):
    if u == "__VAR__":
        return {"Type": "Variable", "VariableName": nome}
    return {"OutputUUID": u, "OutputName": nome, "Type": "ActionOutput"}


def var(u, nome):
    return {"Value": rif(u, nome), "WFSerializationType": "WFTextTokenAttachment"}


def testo(*pezzi):
    """Testo con variabili: pezzi = stringhe o tuple (uuid, nome)."""
    s, att = "", {}
    for p in pezzi:
        if isinstance(p, str):
            s += p
        else:
            pos = len(s.encode("utf-16-le")) // 2
            att[f"{{{pos}, 1}}"] = rif(*p)
            s += "￼"
    return {"Value": {"string": s, "attachmentsByRange": att}, "WFSerializationType": "WFTextTokenString"}


def campi(voci):
    """voci = lista di (chiave, valore, tipo) con tipo 0 testo, 5 file."""
    items = []
    for k, v, t in voci:
        items.append({"WFItemType": t, "WFKey": testo(k), "WFValue": {"Value": v, "WFSerializationType": "WFTokenAttachmentParameterState"} if t == 5 else (testo(*v) if isinstance(v, tuple) else testo(v))})
    return {"Value": {"WFDictionaryFieldValueItems": items}, "WFSerializationType": "WFDictionaryFieldValue"}


def commento(t):
    add("is.workflow.actions.comment", {"WFCommentActionText": t})


def valore(da_uuid, da_nome, chiave, nome_out):
    u = uid()
    add("is.workflow.actions.getvalueforkey", {
        "WFInput": var(da_uuid, da_nome), "WFDictionaryKey": chiave,
        "WFGetDictionaryValueType": "Value", "CustomOutputName": nome_out}, u)
    return u, nome_out


def elemento(da, quale, nome_out):
    u = uid()
    add("is.workflow.actions.getitemfromlist", {
        "WFInput": var(*da), "WFItemSpecifier": quale, "CustomOutputName": nome_out}, u)
    return u, nome_out


def se_vuoto_mostra_ed_esci(controllo, da_mostrare, messaggio):
    g = uid()
    add("is.workflow.actions.conditional", {
        "GroupingIdentifier": g, "WFControlFlowMode": 0, "WFCondition": 101,
        "WFInput": {"Type": "Variable", "Variable": var(*controllo)}})
    add("is.workflow.actions.showresult", {"Text": testo(messaggio + "\n\n", da_mostrare)})
    add("is.workflow.actions.exit", {})
    add("is.workflow.actions.conditional", {"GroupingIdentifier": g, "WFControlFlowMode": 2})


# --- Configurazione -----------------------------------------------------------
commento("MEMO AI — registra, trascrive (OpenAI), pulisce e salva in Note.\n"
         "Configurazione: chiave API e indirizzo del visualizzatore mappe qui sotto.")
K = (uid(), "Chiave API")
i_chiave = add("is.workflow.actions.gettext", {"WFTextActionText": "", "CustomOutputName": K[1]}, K[0])
V = (uid(), "Visualizzatore")
i_viewer = add("is.workflow.actions.gettext", {"WFTextActionText": "https://robertomicarelli.github.io/Claude-Memo-Voice/viewer/", "CustomOutputName": V[1]}, V[0])

# --- 1. Registrazione -----------------------------------------------------------
A = (uid(), "Audio")
add("is.workflow.actions.recordaudio", {
    "WFRecordingCompression": "Normal", "WFRecordingStart": "Immediately", "CustomOutputName": A[1]}, A[0])

# --- 2. Trascrizione --------------------------------------------------------------
T1 = (uid(), "Risposta trascrizione")
add("is.workflow.actions.downloadurl", {
    "WFURL": "https://api.openai.com/v1/audio/transcriptions",
    "WFHTTPMethod": "POST",
    "WFHTTPHeaders": campi([("Authorization", ("Bearer ", K), 0)]),
    "WFHTTPBodyType": "Form",
    "WFFormValues": campi([("model", TRASCRIZIONE, 0), ("language", "it", 0),
                           ("chunking_strategy", "auto", 0),
                           ("prompt", (ROOT / "prompt/vocabolario_trascrizione.txt").read_text().strip(), 0),
                           ("file", var(*A), 5)]),
    "CustomOutputName": T1[1]}, T1[0])
TR = valore(*T1, "text", "Trascrizione")
se_vuoto_mostra_ed_esci(TR, T1, "Trascrizione non riuscita. Risposta di OpenAI:")

# --- 3. Pulizia a blocchi + struttura ------------------------------------------
SOGLIA_PAROLE = 300  # stesso valore di test/prova_api.py


def template(nome):
    corpo = {"model": MODELLO, **json.loads((ROOT / "prompt" / nome).read_text())}
    if MODELLO.startswith(("gpt-5", "o")):
        corpo["reasoning"] = {"effort": "minimal"}
    return json.dumps(corpo, ensure_ascii=False)


def chiama_responses(nome_template, ingresso, etichetta):
    """Template JSON -> dizionario -> input -> POST -> output[-1].content[0].text"""
    rt = (uid(), f"Modello {etichetta}")
    add("is.workflow.actions.gettext", {"WFTextActionText": template(nome_template), "CustomOutputName": rt[1]}, rt[0])
    d = (uid(), f"Richiesta {etichetta}")
    add("is.workflow.actions.detect.dictionary", {"WFInput": var(*rt), "CustomOutputName": d[1]}, d[0])
    d2 = (uid(), f"Richiesta {etichetta} completa")
    add("is.workflow.actions.setvalueforkey", {
        "WFDictionary": var(*d), "WFDictionaryKey": "input",
        "WFDictionaryValue": testo(ingresso), "CustomOutputName": d2[1]}, d2[0])
    r = (uid(), f"Risposta {etichetta}")
    add("is.workflow.actions.downloadurl", {
        "WFURL": "https://api.openai.com/v1/responses",
        "WFHTTPMethod": "POST",
        "WFHTTPHeaders": campi([("Authorization", ("Bearer ", K), 0), ("Content-Type", "application/json", 0)]),
        "WFHTTPBodyType": "File",
        "WFRequestVariable": var(*d2),
        "CustomOutputName": r[1]}, r[0])
    o = valore(*r, "output", f"Output {etichetta}")
    ol = elemento(o, "Last Item", f"Messaggio {etichetta}")
    c = valore(*ol, "content", f"Contenuto {etichetta}")
    c0 = elemento(c, "First Item", f"Parte {etichetta}")
    t = valore(*c0, "text", f"Testo {etichetta}")
    se_vuoto_mostra_ed_esci(t, r, f"Errore OpenAI ({etichetta}). Risposta:")
    return t


def imposta(nome, *pezzi):
    u = (uid(), f"Valore {nome}")
    add("is.workflow.actions.gettext", {"WFTextActionText": testo(*pezzi) if pezzi else "", "CustomOutputName": u[1]}, u[0])
    add("is.workflow.actions.setvariable", {"WFVariableName": nome, "WFInput": var(*u)})


def pulisci_blocco_e_accoda():
    pb = chiama_responses("request_pulizia_blocco.json", NV("Blocco"), "pulizia")
    imposta("Pulito", NV("Pulito"), "\n\n", pb)
    imposta("Blocco")


commento(f"Pulizia a blocchi: le righe della trascrizione si accumulano finché il blocco supera "
         f"{SOGLIA_PAROLE} parole, poi il blocco viene ripulito con una chiamata a parte. "
         "Così il testo pulito resta completo anche nei memo lunghi.")
imposta("Pulito")
imposta("Blocco")
RIGHE = (uid(), "Righe")
add("is.workflow.actions.text.split", {
    "text": testo(TR), "WFTextSeparator": "New Lines", "CustomOutputName": RIGHE[1]}, RIGHE[0])
gr = uid()
add("is.workflow.actions.repeat.each", {"GroupingIdentifier": gr, "WFControlFlowMode": 0, "WFInput": var(*RIGHE)})
imposta("Blocco", NV("Blocco"), "\n", NV("Repeat Item"))
N = (uid(), "Parole blocco")
add("is.workflow.actions.count", {"WFCountType": "Words", "Input": var(*NV("Blocco")), "CustomOutputName": N[1]}, N[0])
gs = uid()
add("is.workflow.actions.conditional", {
    "GroupingIdentifier": gs, "WFControlFlowMode": 0, "WFCondition": 2, "WFNumberValue": SOGLIA_PAROLE - 1,
    "WFInput": {"Type": "Variable", "Variable": var(*N)}})
pulisci_blocco_e_accoda()
add("is.workflow.actions.conditional", {"GroupingIdentifier": gs, "WFControlFlowMode": 2})
add("is.workflow.actions.repeat.each", {"GroupingIdentifier": gr, "WFControlFlowMode": 2})
# ultimo blocco rimasto
gu = uid()
add("is.workflow.actions.conditional", {
    "GroupingIdentifier": gu, "WFControlFlowMode": 0, "WFCondition": 100,
    "WFInput": {"Type": "Variable", "Variable": var(*NV("Blocco"))}})
pulisci_blocco_e_accoda()
add("is.workflow.actions.conditional", {"GroupingIdentifier": gu, "WFControlFlowMode": 2})

JT = chiama_responses("request_struttura.json", NV("Pulito"), "struttura")
RES = (uid(), "Risultato")
add("is.workflow.actions.detect.dictionary", {"WFInput": var(*JT), "CustomOutputName": RES[1]}, RES[0])
TIT = valore(*RES, "titolo", "Titolo")
ST = valore(*RES, "struttura", "Struttura")
MM = valore(*RES, "mappa_markdown", "Mappa")
TP = NV("Pulito")

# --- 4. Link alla mappa (markdown in base64 nel frammento #) ---------------------
B64 = (uid(), "Mappa base64")
add("is.workflow.actions.base64encode", {
    "WFInput": var(*MM), "WFEncodeMode": "Encode", "WFBase64LineBreakMode": "None",
    "CustomOutputName": B64[1]}, B64[0])
# La nota è rich text costruito da HTML: il link alla mappa è un vero <a href>.
# In testo semplice Note riconosceva solo "https://.../viewer" e perdeva il "#...".


def sostituisci(ingresso, cerca, con, nome, regex=False):
    u = (uid(), nome)
    add("is.workflow.actions.text.replace", {
        "WFInput": testo(ingresso), "WFReplaceTextFind": cerca,
        "WFReplaceTextReplace": testo(con) if isinstance(con, tuple) else con,
        "WFReplaceTextRegularExpression": regex, "WFReplaceTextCaseSensitive": True,
        "CustomOutputName": nome}, u[0])
    return u


SEGNAPOSTO = "§MAPPA§"
P = (uid(), "Testo semplice")
add("is.workflow.actions.gettext", {
    "WFTextActionText": testo(TIT, "\n\n", ST, f"\n\n{SEGNAPOSTO}\n\nTESTO COMPLETO\n", TP),
    "CustomOutputName": P[1]}, P[0])
P1 = sostituisci(P, "&", "&amp;", "Testo html 1")
P2 = sostituisci(P1, "<", "&lt;", "Testo html 2")
P3 = sostituisci(P2, ">", "&gt;", "Testo html 3")
P4 = sostituisci(P3, "\n", "<br>", "Testo html 4")
VC = sostituisci(V, r"\s+", "", "Indirizzo pulito", regex=True)
BC = sostituisci(B64, r"\s+", "", "Mappa base64 pulita", regex=True)
LINK = (uid(), "Link mappa")
add("is.workflow.actions.gettext", {
    "WFTextActionText": testo('<b>MAPPA MENTALE</b><br><a href="', VC, "#", BC,
                              '">Apri la mappa mentale</a>'),
    "CustomOutputName": LINK[1]}, LINK[0])
P5 = sostituisci(P4, SEGNAPOSTO, LINK, "Testo html 5")
H = (uid(), "HTML nota")
add("is.workflow.actions.gettext", {
    "WFTextActionText": testo('<html><head><meta charset="utf-8"></head><body>', P5, "</body></html>"),
    "CustomOutputName": H[1]}, H[0])
NB = (uid(), "Testo nota")
add("is.workflow.actions.getrichtextfromhtml", {"WFHTML": testo(H), "CustomOutputName": NB[1]}, NB[0])

# --- 5. Menu cartella --------------------------------------------------------------
g = uid()
voci = CARTELLE + ["Non salvare"]
add("is.workflow.actions.choosefrommenu", {
    "GroupingIdentifier": g, "WFControlFlowMode": 0,
    "WFMenuPrompt": "Dove salvo il memo?", "WFMenuItems": voci})
for v in voci:
    add("is.workflow.actions.choosefrommenu", {
        "GroupingIdentifier": g, "WFControlFlowMode": 1, "WFMenuItemTitle": v})
    if v == "Non salvare":
        add("is.workflow.actions.showresult", {"Text": testo(NB)})
    else:
        commento(f"AGGIUNGI QUI: «Crea nota» → Contenuto: variabile «Testo nota» → Cartella: {v}")
add("is.workflow.actions.choosefrommenu", {"GroupingIdentifier": g, "WFControlFlowMode": 2})

workflow = {
    "WFWorkflowClientVersion": "2605.0.5",
    "WFWorkflowMinimumClientVersion": 900,
    "WFWorkflowMinimumClientVersionString": "900",
    "WFWorkflowIcon": {"WFWorkflowIconStartColor": 4282601983, "WFWorkflowIconGlyphNumber": 61440},
    "WFWorkflowTypes": [],
    "WFWorkflowInputContentItemClasses": [],
    "WFWorkflowOutputContentItemClasses": [],
    "WFWorkflowHasShortcutInputVariables": False,
    "WFWorkflowImportQuestions": [
        {"ActionIndex": i_chiave, "Category": "Parameter", "ParameterKey": "WFTextActionText",
         "Text": "Incolla la tua API key di OpenAI", "DefaultValue": ""},
        {"ActionIndex": i_viewer, "Category": "Parameter", "ParameterKey": "WFTextActionText",
         "Text": "Indirizzo del visualizzatore mappe (lascia così)",
         "DefaultValue": "https://robertomicarelli.github.io/Claude-Memo-Voice/viewer/"},
    ],
    "WFWorkflowActions": azioni,
}

out = ROOT / "shortcut/Memo_AI_unsigned.shortcut"
with open(out, "wb") as f:
    plistlib.dump(workflow, f, fmt=plistlib.FMT_BINARY)
print(f"scritto {out} ({len(azioni)} azioni, modello {MODELLO})")
