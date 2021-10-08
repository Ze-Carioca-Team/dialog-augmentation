import json
import string
import random

augmented = {}
random.seed(42)

def gen_placa():
    value = ""
    for i in range(3): value += string.ascii_letters[random.randint(0, len(string.ascii_letters)-1)].upper()
    for i in range(4): value += str(random.randint(0, 9))
    prob = random.random()
    if (prob <= 0.6):
        if (prob <= 0.2): value = value[:3]+" "+value[3:]
        elif (prob <= 0.4): value = value[:3]+"-"+value[3:]
    else: value = value[:4]+string.ascii_letters[random.randint(0, len(string.ascii_letters)-1)].upper()+value[5:]
    return value

def gen_cpf():
    value = ""
    for i in range(11): value += str(random.randint(0, 9))
    prob = random.randint(0,3)
    if (prob==0): value = value[:3]+"."+value[3:6]+"."+value[6:9]+"-"+value[9:]
    elif (prob==1): value = value[:3]+" "+value[3:6]+" "+value[6:9]+" "+value[9:]
    elif (prob==2): value = value[:3]+""+value[3:6]+""+value[6:9]+"-"+value[9:]
    return value

def gen_valor():
    valueint = random.randint(0, 2000)
    valuefloat = random.randint(0, 99)
    if (valuefloat < 10): valuefloat = "0"+str(valuefloat)
    else: valuefloat = str(valuefloat)
    prob = random.random()
    if (prob > 0.2): value = str(valueint)+" reais"
    elif (prob > 0.4): value = "R$"+str(valueint)
    elif (prob > 0.6): value = "R$"+str(valueint)+","+valuefloat
    elif (prob > 0.8): value = str(valueint)+","+valuefloat+" reais"
    else: value = str(valueint)
    return value

with open("synthetic_anotado.json") as fin:
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
    with open("synthetic.augmented.json", "w") as fout:
        json.dump(augmented, fout, indent=2, sort_keys=True)
