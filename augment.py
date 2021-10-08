import json
import string
import random

augmented = {}
random.seed(42)

arquivo = open("/content/names_pt-br_new.json", "r", encoding='utf-8')
names = json.load(arquivo)
arquivo.close()

def default(o): # to save custom format in json=
    if type(o) is datetime.datetime:
        return o.isoformat()

def gen_nome(old_name):
    value = old_name[-1]
    while (value in old_name):
        gender = names[1][names[0].index(old_name[-1])]
        index = random.randint(0, len(names[0])-1)
        while(int(names[1][index]) != gender): index = random.randint(0, len(names[0])-1)
        value = names[0][index]
    return value

def gen_placa(old_plate):
    value = old_plate[-1]
    while (value in old_plate):
        value = ""
        for i in range(3): value += string.ascii_letters[random.randint(0, len(string.ascii_letters)-1)].upper()
        for i in range(4): value += str(random.randint(0, 9))
        prob = random.random()
        if (prob <= 0.6):
            if (prob <= 0.2): value = value[:3]+" "+value[3:]
            elif (prob <= 0.4): value = value[:3]+"-"+value[3:]
        else: value = value[:4]+string.ascii_letters[random.randint(0, len(string.ascii_letters)-1)].upper()+value[5:]
    return value

def gen_cpf(old_cpf):
    value = old_cpf[-1]
    while (value in old_cpf):
        value = ""
        for i in range(11): value += str(random.randint(0, 9))
        prob = random.randint(0,3)
        if (prob==0): value = value[:3]+"."+value[3:6]+"."+value[6:9]+"-"+value[9:]
        elif (prob==1): value = value[:3]+" "+value[3:6]+" "+value[6:9]+" "+value[9:]
        elif (prob==2): value = value[:3]+""+value[3:6]+""+value[6:9]+"-"+value[9:]
    return value

def gen_valor(old_value):
    value = old_value[-1]
    while (value in old_value):
        valueint = random.randint(0, 999)
        valuefloat = random.randint(0, 99)
        if (valuefloat < 10): valuefloat = "0"+str(valuefloat)
        else: valuefloat = str(valuefloat)
        prob = random.random()
        if (prob > 0.25): value = str(valueint)+" reais"
        elif (prob > 0.5): value = "R$"+str(valueint)
        elif (prob > 0.75): value = "R$"+str(valueint)+","+valuefloat
        else: value = str(valueint)+","+valuefloat+" reais"
    return value

def order_dialog(dialog):
    result = {}
    result["id"] = dialog["id"]
    result["dialog_domain"] = dialog["dialog_domain"]
    result["turns"] = []

    for turn in dialog["turns"]:
        new_turn = {}
        new_turn["speaker"] = turn["speaker"]
        new_turn["utterance"] = turn["utterance"]
        new_turn["utterance_delex"] = turn["utterance_delex"]
        if ("intent" in turn.keys()): new_turn["intent"] = turn["intent"]
        if ("action" in turn.keys()): new_turn["action"] = turn["action"]
        new_turn["slot-values"] = turn["slot-values"]
        new_turn["turn-num"] = turn["turn-num"]
        result["turns"].append(new_turn)
    return result

with open("synthetic_anotado.json", 'r', encoding='utf-8') as fin:
    data = json.load(fin)
    augmented["ontology"] = data["ontology"]
    augmented["dialogs"] = []
    for dialog in data["dialogs"]:
        selected_values = {"cpf": [], "placa": [], "valor": [], "nome": []}
        for i in range(random.randint(4, 20)):
            new_dialog = dialog.copy()
            new_dialog["id"] += i*100
            new_dialog["turns"] = new_dialog["turns"].copy()
            nome = None
            for turn in new_dialog["turns"]:
                turn["utterance"] = turn["utterance_delex"]
                turn["slot-values"] = turn["slot-values"].copy()
                if "[cpf]" in turn["utterance"]:
                    selected_values["cpf"].append(turn["slot-values"]["cpf"])
                    cpf = gen_cpf(selected_values["cpf"])
                    turn["utterance"] = turn["utterance"].replace("[cpf]", cpf)
                    turn["slot-values"]["cpf"] = cpf
                if "[placa]" in turn["utterance"]:
                    selected_values["placa"].append(turn["slot-values"]["placa"])
                    placa = gen_placa(selected_values["placa"])
                    turn["utterance"] = turn["utterance"].replace("[placa]", placa)
                    turn["slot-values"]["placa"] = placa
                if "[valor]" in turn["utterance"]:
                    selected_values["valor"].append(turn["slot-values"]["valor"])
                    valor = gen_valor(selected_values["valor"])
                    turn["utterance"] = turn["utterance"].replace("[valor]", valor)
                    turn["slot-values"]["valor"] = valor
                if "[nome]" in turn["utterance"]:
                    if (nome == None):
                        selected_values["nome"].append(turn["slot-values"]["nome"])
                        nome = gen_nome(selected_values["nome"])
                    turn["utterance"] = turn["utterance"].replace("[nome]", nome)
                    turn["slot-values"]["nome"] = nome
            augmented["dialogs"].append(order_dialog(new_dialog))
    with open("synthetic_augmented.json", 'w', encoding='utf-8') as fout:
        fout.write(json.dumps(augmented, indent=2, default=default, ensure_ascii=False))