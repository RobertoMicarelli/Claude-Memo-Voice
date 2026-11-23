"""Controllo strutturale di un .shortcut non firmato: blocchi chiusi,
output e variabili definiti prima dell'uso, JSON validi nei Testo."""
import json, plistlib, sys

def controlla(path):
    w = plistlib.load(open(path, 'rb'))
    A = w['WFWorkflowActions']; definiti = set(); varnomi = {'Repeat Item'}; stack = []; err = []
    def refs(o):
        if isinstance(o, dict):
            if o.get('Type') == 'ActionOutput': yield ('out', o['OutputUUID'])
            if o.get('Type') == 'Variable' and 'VariableName' in o: yield ('var', o['VariableName'])
            for v in o.values(): yield from refs(v)
        elif isinstance(o, list):
            for v in o: yield from refs(v)
    for i, a in enumerate(A):
        p = a['WFWorkflowActionParameters']; ident = a['WFWorkflowActionIdentifier']
        for k, r in refs(p):
            if k == 'out' and r not in definiti: err.append(f'{i} {ident}: output non definito')
            if k == 'var' and r not in varnomi: err.append(f'{i} {ident}: variabile {r}')
        if 'GroupingIdentifier' in p:
            m = p['WFControlFlowMode']
            if m == 0: stack.append(p['GroupingIdentifier'])
            elif m == 2 and (not stack or stack.pop() != p['GroupingIdentifier']): err.append(f'{i}: chiusura')
        if 'UUID' in p: definiti.add(p['UUID'])
        if ident.endswith('setvariable'): varnomi.add(p['WFVariableName'])
        t = p.get('WFTextActionText')
        if isinstance(t, str) and t.startswith('{'): json.loads(t)
    if stack: err.append(f'blocchi aperti: {len(stack)}')
    for q in w['WFWorkflowImportQuestions']:
        if A[q['ActionIndex']]['WFWorkflowActionIdentifier'] != 'is.workflow.actions.gettext': err.append('domanda import su azione sbagliata')
    return len(A), err

for f in sys.argv[1:]:
    n, err = controlla(f)
    print(f"{f}: {n} azioni, {'ok' if not err else err}")
