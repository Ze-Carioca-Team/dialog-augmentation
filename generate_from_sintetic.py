import json

data = {}
data["ontology"] = {
    "actions": [
      "req_cpf",
      "cumprimento",
      "info_valor",
      "req_mais",
      "req_placa",
      "despedida",
      "agradecimento"
    ],
    "intents": [
      "cumprimento",
      "consulta_saldo",
      "info_placa",
      "info_cpf",
      "confimacao",
      "agradecimento",
      "negacao"
    ],
    "slot-values":{}}
data["dialogs"] = []

with open("synthetic.txt") as fin:
    dialogues = fin.read().split("\n\n")
    for index, dialog in enumerate(dialogues):
        turns = []
        strip_split = dialog.lstrip("\n").rstrip("\n").split("\n")
        for t, turn in enumerate(strip_split):
            tdata = {}
            tdata["utterance"] = turn
            tdata["utterance_delex"] = turn
            tdata["turn-num"] = t
            tdata["slot-values"] = {}
            if t % 2 == 0:
                tdata["speaker"] = "client"
                tdata["intent"] = None
            else:
                tdata["speaker"] = "agent"
                tdata["action"] = None
            turns.append(tdata)
        ddata = {}
        ddata["turns"] = turns
        ddata["id"] = index+10000
        ddata["dialog_domain"] = "consulta_saldo"
        data["dialogs"].append(ddata)
    with open("synthetic.json", "w") as fout:
        json.dump(data, fout, indent=2, sort_keys=True)
