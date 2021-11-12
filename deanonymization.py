from transformers import BertTokenizer, BertForTokenClassification
import numpy as np
import argparse
import random
import string
import torch
import util
import json

names = None
lastnames = None
bert_entity_tokenizer = None
bert_entity_model = None
bert_entity_tag_values = None
replaceterm = [["[protocolo]", 0], ["[adesivo]", 0], ["[cpf]", 0], ["[atendente]", 1],
               ["[inicio_hora_att]", 0], ["[fim_hora_att]", 0], ["[sobrenome]", 0],
               ["[valor_monetario]", 0], ["[valor]", 0], ["[estado_civil]", 0],
               ["[servico_whatsapp]", 0], ["[servico_telcap]", 0], ["[servico_tel]", 0],
               ["[email]", 0], ["[local]", 0], ["[placa]", 0], ["[telefone]", 0],
               ["[periodo]", 0], ["[caracter]", 0], ["[quantidade]", 0],
               ["[dia_da_semana]", 0], ["[hora]", 0], ["[data]", 0], ["[marca]", 0],
               ["[modelo]", 0], ["[ano]", 0], ["[link]", 0], ["[categoria]", 0],
               ["[cliente]", 1], ["[nome]", 1]]

def load_names_lastnames (names_dir, lastnames_dir):
    global names
    global lastnames    
    with open(names_dir, 'r', encoding='utf-8') as fin: names = json.load(fin)
    with open(lastnames_dir, 'r', encoding='utf-8') as fin: lastnames = json.load(fin)

def load_bert_entities (bert_entity_dir):
    global bert_entity_tokenizer
    global bert_entity_model
    global bert_entity_tag_values

    bert_entity_tokenizer = BertTokenizer.from_pretrained(bert_entity_dir)
    bert_entity_model = BertForTokenClassification.from_pretrained(bert_entity_dir)
    bert_entity_tag_values = None
    with open(bert_entity_dir+"tag_values.json", 'r') as tfile:
        bert_entity_tag_values = json.load(tfile)

def create_value (key, old_values):
    global names
    global lastnames
    if ((names == None)or(lastnames == None)):
        load_names_lastnames("names.json", "lastnames.json")

    old_value = ""
    if (len(old_values) > 0): old_value = old_values[-1]
    key_repeat = ["[inicio_hora_att]", "[fim_hora_att]", "[servico_whatsapp]", "[servico_telcap]", "[servico_tel]", "[local]", "[categoria]", "[link]"]

    value = ""
    iteration = 0
    if (key not in key_repeat): value = old_value
    while (((value == old_value)and(key not in key_repeat))or
           ((value == "")and(key in key_repeat))and(iteration < 5)):
        value = ""
        if (key == "[protocolo]"):
            for i in range(20): value += str(random.randint(0, 9))

        elif (key == "[adesivo]"):
            for i in range(15): value += str(random.randint(0, 9))

        elif (key == "[cpf]"):
            for i in range(11): value += str(random.randint(0, 9))
            prob = random.random()
            if (prob <= 0.33): value = value[:3]+"."+value[3:6]+"."+value[6:9]+"-"+value[9:]
            elif (prob <= 0.66): value = value[:3]+" "+value[3:6]+" "+value[6:9]+" "+value[9:]

        elif (key == "[atendente]"):
            try: gender = names[1][names[0].index(old_value)]
            except: gender = random.sample([0, 1], k=1)[0]
            index = random.randint(0, len(names[0])-1)
            while(int(names[1][index]) != gender): index = random.randint(0, len(names[0])-1)
            value = names[0][index]

        elif (key == "[hora]"):
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            if (hour < 10): value = "0"+str(hour)
            else: value = str(hour)
            if (minute < 10): value += ":0"+str(minute)
            else: value += ":"+str(minute)
            prob = random.random()
            if (prob > 0.5):
                second = random.randint(0, 59)
                if (second < 10): value += ":0"+str(second)
                else: value += ":"+str(second)

        elif (key == "[data]"):
            start = "01/01/2017"
            end = "01/09/2021"
            prob = random.random()
            format = '%d/%m/%Y %I:%M'
            if (prob <= 0.16): format = '%d/%m/%Y'
            elif (prob <= 0.33): format = '%d/%m'
            elif (prob <= 0.49): format = '%d-%m-%Y %I:%M'
            elif (prob <= 0.66):  format = '%d-%m-%Y'
            elif (prob <= 0.82):  format = '%d-%m'
            value = util.randomDate(start, end, random.random(), format)

        elif (key == "[sobrenome]"):
            for i in range(random.randint(1, 5)):
                value += lastnames[random.randint(0, len(lastnames)-1)]+" "
            value = value[:len(value)-1]

        elif (key == "[inicio_hora_att]"): value = "08:00"
        elif (key == "[fim_hora_att]"): value = "22:00"

        elif ((key == "[valor_monetario]")or(key == "[valor]")):
            valueint = random.randint(0, 999)
            valuefloat = random.randint(0, 99)
            if (valuefloat < 10): valuefloat = "0"+str(valuefloat)
            else: valuefloat = str(valuefloat)
            prob = random.random()
            if (prob <= 0.2): value = str(valueint)+" reais"
            elif (prob <= 0.4): value = "R$"+str(valueint)
            elif (prob <= 0.6): value = "R$"+str(valueint)+","+valuefloat
            elif (prob <= 0.8): value = str(valueint)+","+valuefloat+" reais"
            else: value = str(valueint)

        elif (key == "[estado_civil]"):
            prob = random.random()
            if (prob <= 0.2): value = "Solteir"
            elif (prob <= 0.4): value = "Casad"
            elif (prob <= 0.6): value = "Separad"
            elif (prob <= 0.8): value = "Divorciad"
            else: value = "Viúv"
            gender = random.sample([0, 1], k=1)[0]
            if (gender == 1): value += "a"
            else: value += "o"

        elif (key == "[servico_whatsapp]"): value = "3003-4475"
        elif (key == "[servico_telcap]"): value = "4020-2227"
        elif (key == "[servico_tel]"): value = "0800 030 2227"

        elif (key == "[email]"):
            dominio = ["yahoo.com.br", "gmail.com", "hotmail.com", "live.com"]
            value = names[0][random.randint(0, len(names[0])-1)].lower()+str(random.randint(1, 99))+"@"
            value += dominio[random.randint(0, len(dominio)-1)]

        elif (key == "[periodo]"):
            valueint = random.randint(0, 99)
            value = str(valueint)
            prob = random.random()
            if (prob <= 0.17): value += " minuto"
            elif (prob <= 0.34): value += " hora"
            elif (prob <= 0.50): value += " hr"
            elif (prob <= 0.67): value += " dia"
            elif (prob <= 0.83): value += " semana"
            else: value += " mes"
            if (valueint > 1):
                if (prob > 0.83):  value += "es"
                else: value += "s"

        elif (key == "[quantidade]"): value = str(random.randint(0, 99))
        elif (key == "[caracter]"): value = str(string.ascii_letters[random.randint(0, len(string.ascii_letters)-1)])

        elif (key == "[dia_da_semana]"):
            weekday = ["domingo", "Domingo", "sábado", "sabado", "Sábado", "Sabado", "Segunda-feira", "Segunda-Feira", "segunda-feira", "segunda", "segunda feira", "Terça-feira", "Terça-Feira", "terça-feira", "terça", "terça feira", "Quarta-feira", "Quarta-Feira", "quarta-feira", "quarta", "quarta feira", "Quinta-feira", "Quinta-Feira", "quinta-feira", "quinta", "quinta feira", "Sexta-feira", "Sexta-Feira", "sexta-feira", "sexta", "sexta feira"]
            value = random.sample(weekday, k=1)[0]

        elif (key == "[local]"): value = old_value
        elif (key == "[categoria]"): value = old_value

        elif (key == "[modelo]"):
            modelos = ["Gol", "Uno", "Palio", "CrossFox", "Siena", "Celta", "Voyage", "HB20", "Corsa Sedan", "Onix", "Sandero", "Fiesta", "Cobalt", "Ka", "Corolla", "Civic", "Punto", "Fit", "Spin", "C3", "Cruze Sedan", "Logan", "Agile", "City", "Idea", "March", "Fiesta Sedan", "Space Fox", "Cruze HB", "Focus", "Versa", "i30", "Etios HB", "Doblò", "Golf", "Polo Sedan", "Palio Weekend", "Livina", "Fluence", "Bravo", "New Fiesta", "Jetta", "C3 Picasso", "Etios Sedan", "Polo", "Focus Sedan"]
            value = random.sample(modelos, k=1)[0]
            if (random.random() >= 0.5): value = value.lower()

        elif (key == "[marca]"):
            marcas = ["Chevrolet", "Volkswagen", "Fiat", "Renault", "Ford", "Toyota", "Hyundai", "Jeep", "Honda", "Nissan", "Citroën", "Mitsubishi", "Peugeot", "Chery", "BMW", "Mercedes-Benz", "Kia", "Audi", "Volvo", "Land Rover"]
            value = random.sample(marcas, k=1)[0]
            if (random.random() >= 0.5): value = value.lower()

        elif (key == "[ano]"): value = random.sample(["2017", "2018", "2019", "2020", "2021"], k=1)[0]
        elif (key == "[link]"): value = old_value

        elif (key == "[placa]"):
            prob = random.random()
            if (prob <= 0.5):
                for i in range(3): value += string.ascii_letters[random.randint(0, len(string.ascii_letters)-1)].upper()
                for i in range(4): value += str(random.randint(0, 9))
                prob = random.random()
                if (prob <= 0.6):
                    if (prob <= 0.2): value = value[:3]+" "+value[3:]
                    elif (prob <= 0.4): value = value[:3]+"-"+value[3:]
                else: value = value[:4]+string.ascii_letters[random.randint(0, len(string.ascii_letters)-1)].upper()+value[5:]
            else:
                for i in range(3): value += string.ascii_letters[random.randint(0, len(string.ascii_letters)-1)].lower()
                for i in range(4): value += str(random.randint(0, 9))
                prob = random.random()
                if (prob <= 0.6):
                    if (prob <= 0.2): value = value[:3]+" "+value[3:]
                    elif (prob <= 0.4): value = value[:3]+"-"+value[3:]
                else: value = value[:4]+string.ascii_letters[random.randint(0, len(string.ascii_letters)-1)].lower()+value[5:]

        elif (key == "[telefone]"):
            for i in range(11): value += str(random.randint(0, 9))
            prob = random.random()
            if (prob <= 0.11): value = "0"+value
            elif (prob <= 0.22): value = "("+value[:2]+") "+value[2:7]+"-"+value[7:]
            elif (prob <= 0.33): value = "("+value[:2]+") "+value[2:7]+" "+value[7:]
            elif (prob <= 0.44): value = value[:2]+" "+value[2:7]+" "+value[7:]
            elif (prob <= 0.55): value = value[:2]+" "+value[2:7]+"-"+value[7:]
            elif (prob <= 0.66): value = value[:2]+"-"+value[2:7]+"-"+value[7:]
            elif (prob <= 0.77): value = value[2:7]+" "+value[7:]
            elif (prob <= 0.88): value = value[2:7]+"-"+value[7:]
            else: value = "("+value[:2]+") "+value[2:]

        elif ((key == "[cliente]")or(key == "[nome]")):
            try: gender = names[1][names[0].index(old_value)]
            except: gender = random.sample([0, 1], k=1)[0]
            index = random.randint(0, len(names[0])-1)
            while(int(names[1][index]) != gender): index = random.randint(0, len(names[0])-1)
            value = names[0][index]

        iteration += 1
    return value

def get_entities (sentence):
    global bert_entity_tokenizer
    global bert_entity_model
    global bert_entity_tag_values

    tokenizer = bert_entity_tokenizer
    model = bert_entity_model
    tag_values = bert_entity_tag_values
    if ((tokenizer == None)or(model == None)or(tag_values == None)):
        return None

    tokenized_sentence = tokenizer.encode(sentence)
    input_ids = torch.LongTensor([tokenized_sentence]).reshape(1,-1)

    with torch.no_grad(): output = model(input_ids)
    label_indices = np.argmax(output[0].to('cpu').numpy(), axis=2)[0]
    tokens = tokenizer.convert_ids_to_tokens(input_ids.to('cpu').numpy()[0])

    new_tokens, new_labels = [], []
    old = label_indices[0]

    for token, label_idx in zip(tokens, label_indices):
        if ("B-" in tag_values[label_idx]):
            if (tag_values[old] != tag_values[label_idx]):
                new_labels.append("["+tag_values[label_idx].replace("B-", "")+"]")
                new_tokens.append("["+tag_values[label_idx].replace("B-", "")+"]")
        else: new_tokens.append(token)
        old = label_idx

    output_ids = tokenizer.convert_tokens_to_ids(new_tokens)
    sentence_delex = tokenizer.decode(output_ids)
    original = "[CLS] "+sentence+" [SEP]"
    curr_sentence = sentence_delex

    slot_values = {}
    for label in new_labels:
        sentence_delex = sentence_delex.replace("[UNK]", label, 1)
        try:
            slices = curr_sentence.split("[UNK]")
            value = original.split(slices[0])[1].split(slices[1])[0]
            curr_sentence = curr_sentence.replace("[UNK]", value, 1)

            key = label.replace("[", "").replace("]", "")
            if (key not in slot_values.keys()): slot_values[key] = value
            elif isinstance(slot_values[key], list): slot_values[key].append(value)
            else: slot_values[key] = [slot_values[key], value]
        except: continue

    result = {}
    sentence_delex = sentence_delex.replace("[CLS] ", "").replace(" [SEP]", "")
    result["utterance"] = sentence
    result["utterance_delex"] = sentence_delex
    result["slot-values"] = slot_values.copy()

    return result

def deanonymization (data, swap = False, anonymize = False, min_sents = 4, max_sents = 14):
    global replaceterm
    augmented = {}
    augmented["ontology"] = data["ontology"].copy()
    augmented["dialogs"] = []

    selected_values_original = {}
    for key in replaceterm: selected_values_original[key[0]] = []

    static_data_original = {}
    for key in replaceterm:
        if (key[1] == 1): static_data_original[key[0]] = None

    for dialog in data["dialogs"]:
        selected_values = selected_values_original.copy()
        frequency = random.randint(min_sents, max_sents)
        if (swap): frequency = 1

        for i in range(frequency):
            new_dialog = dialog.copy()
            if (swap == False):
                if ("-" in str(new_dialog["id"])):
                    new_dialog["id"] = new_dialog["id"].replace("-", "-"+str(i)+"-")
                else: new_dialog["id"] = str(i+1)+"-"+str(new_dialog["id"])
            new_dialog["turns"] = new_dialog["turns"].copy()
            static_data = static_data_original.copy()

            all_slots = {}
            for turn in new_dialog["turns"]:
                turn["slot-values"] = turn["slot-values"].copy()
                if ((turn["utterance"] == turn["utterance_delex"])and(anonymize)):
                    anonyres = get_entities(turn["utterance"])
                    turn["utterance"] = anonyres["utterance"]
                    turn["utterance_delex"] = anonyres["utterance_delex"]
                    turn["slot-values"] = anonyres["slot-values"].copy()
                turn["utterance"] = turn["utterance_delex"]

                for key in replaceterm:
                    if (key[0] in turn["utterance"]):
                        for occurrence in range(turn["utterance"].count(key[0])):
                            value = None
                            if (key[0].replace("[", "").replace("]", "") not in turn["slot-values"]):
                                turn["slot-values"][key[0].replace("[", "").replace("]", "")] = None
                            if isinstance(turn["slot-values"][key[0].replace("[", "").replace("]", "")], list):
                                selected_values[key[0]].append(turn["slot-values"][key[0].replace("[", "").replace("]", "")][occurrence])
                            else: selected_values[key[0]].append(turn["slot-values"][key[0].replace("[", "").replace("]", "")])

                            if (key[1] == 0): value = create_value(key[0], selected_values[key[0]])
                            else:
                                if (static_data[key[0]] == None):
                                    value = create_value(key[0], selected_values[key[0]])
                                    static_data[key[0]] = value
                                else: value = static_data[key[0]]

                            turn["utterance"] = turn["utterance"].replace(key[0], value, 1)
                            if isinstance(turn["slot-values"][key[0].replace("[", "").replace("]", "")], list):
                                turn["slot-values"][key[0].replace("[", "").replace("]", "")][occurrence] = value
                            else: turn["slot-values"][key[0].replace("[", "").replace("]", "")] = value

                for key in turn["slot-values"].keys():
                    try: all_slots[key] = turn["slot-values"][key].copy()
                    except: all_slots[key] = turn["slot-values"][key]
                turn["slot-values"] = all_slots.copy()
            augmented["dialogs"].append(util.order_dialog(new_dialog))
    return augmented

def parse_args ():
    parser = argparse.ArgumentParser(description="Deanonymization on a dialog dataset formatted in the MultiWOZ pattern.")
    parser.add_argument("--filename", type=str, default="original.json", help="Path to dialogs dataset.")
    parser.add_argument("--names_dir", type=str, default="names.json", help="Path to file with Brazilian names.")
    parser.add_argument("--lastnames_dir", type=str, default="lastnames.json", help="Path to file with Brazilian lastnames.")
    parser.add_argument("--swap", type=str, default=False, help="Perform only the swap of entity values, without data augmentation.")
    parser.add_argument("--anonymize", type=str, default=False, help="Perform a pre-anonymization of data, identifying the entities present in each sentence.")
    parser.add_argument("--bert_path", type=str, default="bert_entities_model/", help="Path to Bert model for entity identification.")
    parser.add_argument("--min_sents", type=str, default=4, help="Minimum number of new sentences generated.")
    parser.add_argument("--max_sents", type=str, default=14, help="Maximum number of new sentences generated.")
    return parser.parse_args()

def main (args):
    load_names_lastnames(args.names_dir, args.lastnames_dir)
    if (args.anonymize): load_bert_entities(args.bert_path)

    dfile = open(args.filename, "r", encoding='utf-8')
    data = json.load(dfile)
    dfile.close()

    result = deanonymization(data, args.swap, args.anonymize,
                             args.min_sents, args.max_sents)
    result = util.fill_ontology(result)
    random.shuffle(result["dialogs"])
    util.format_jsonfile(result, args.filename, ".deanonymized")

if __name__ == '__main__':
    args = parse_args()
    main(args)