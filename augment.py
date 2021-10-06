import json
import random

augmented = {}
random.seed(42)

def gen_placa():
    return "jgm-1234"

def gen_cpf():
    return "031941345-79"

def gen_valor():
    return "32 reais"

with open("sintetic.json") as fin:
    data = json.load(fin)
    augmented["ontology"] = data["ontology"]
    augmented["ontology"]["slot-values"] = ["[valor_saldo]"]
    augmented["dialogs"] = []
    for dialog in data["dialogs"]:
        for i in range(random.randint(4, 20)):
            new_dialog = dialog.copy()
            new_dialog["id"] += i*100
            for turn in new_dialog["turns"]:
                utt = turn["utterance"]
                turn["slot-values"] = {}
                if "_CPF" in turn["utterance"]:
                    cpf = gen_cpf()
                    turn["utterance"] = utt.replace("_CPF", cpf)
                    turn["slot-values"]["cpf"] = cpf
                if "_PLACA" in turn["utterance"]:
                    placa = gen_placa()
                    turn["utterance"] = utt.replace("_PLACA", placa)
                    turn["slot-values"]["placa"] = placa
                if "_VALOR" in turn["utterance"]:
                    turn["utterance_delex"] = utt.replace("_VALOR", "[valor_saldo]")
            augmented["dialogs"].append(new_dialog)
    with open("sintetic.augmented.json", "w") as fout:
        json.dump(augmented, fout, indent=2, sort_keys=True)
