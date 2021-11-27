from copy import deepcopy
import string
import json
import time

algtrain = ("0", "4", "5", "6", "7", "8", "9")
algtest = ("1", "2", "3")

def replacetag(backtranslation, currtags, tags):
    result = backtranslation
    valid = 0
    for tag_a in currtags:
        if (backtranslation.count(tag_a[0]) == tag_a[1]):
            for tag_b in tags:
                if (tag_b[1] == tag_a[0]):
                    result = result.replace(tag_a[0], tag_b[0])
                    valid += 1
    if (valid == len(currtags)): valid = True
    else: valid = False
    return result, valid

def define_tags(content, original_tags = []):
    tags = original_tags
    slot_values = []
    for item in content["dialogs"]:
        for turn in item["turns"]:
            for key in turn["slot-values"].keys():
                if (key not in slot_values):
                    slot_values.append(key)

    count = 101
    for i in range(len(slot_values)):
        slot_values[i] = ["["+slot_values[i]+"]", "{"+str(count)+"}"]
        count += 1

    tags += slot_values
    for i in range(len(tags)-1):
        for j in range(i+1, len(tags)):
            if (len(tags[j][0]) > len(tags[i][0])):
                aux = tags[i][0]
                tags[i][0] = tags[j][0]
                tags[j][0] = aux
    return tags

def clear_punctuation(text):
    sentence = deepcopy(text)
    patterns = [[";)", "{1001}"], [":)", "{1002}"], [": )", "{1003}"], ["(A)", "{1004}"], [":-)", "{1005}"], ["(Y)", "{1006}"], [":D", "{1007}"], ["=)", "{1008}"], ["(Iv)", "{1009}"], [":heart", "{1010}"]]
    for pattern in patterns: sentence = sentence.replace(pattern[0], pattern[1])
    punctuation = ["!),.:;?]}", "([{"]
    old = ""

    while (sentence != old):
        old = deepcopy(sentence)
        sentence = sentence.replace("  ", " ")
        for punct in punctuation[0]:
            for space in string.whitespace:
                sentence = sentence.replace(str(space+punct), str(punct))
            sentence = sentence.replace(str(" "+punct), str(punct))
            sentence = sentence.replace(str(punct), str(punct+" "))
            for puncta in punctuation[0]:
                sentence = sentence.replace(str(puncta+" "+punct), str(puncta+punct))
                sentence = sentence.replace(str(punct+" "+puncta), str(punct+puncta))

        for punct in punctuation[1]:
            for space in string.whitespace:
                sentence = sentence.replace(str(punct+space), str(punct))
            sentence = sentence.replace(str(punct+" "), str(punct))
            sentence = sentence.replace(str(punct), str(" "+punct))
            for puncta in punctuation[0]:
                sentence = sentence.replace(str(puncta+" "+punct), str(puncta+punct))
                sentence = sentence.replace(str(punct+" "+puncta), str(punct+puncta))

        sentence = sentence.replace("  ", " ")
        if (sentence[len(sentence)-1] == " "): sentence = sentence[:len(sentence)-1]
        if (sentence[0] == " "): sentence = sentence[1:]

    old = ""
    for space in string.whitespace: sentence = sentence.replace(str(space), str(" "))
    while (sentence != old):
        old = deepcopy(sentence)
        sentence = sentence.replace("  ", " ")

    for pattern in patterns: sentence = sentence.replace(pattern[1], pattern[0])
    return sentence

def format_jsonfile(dialogs, filename, sufix):
    with open(filename.replace(".json", sufix+".json"), 'w', encoding='utf-8') as f:
        f.write(json.dumps(dialogs, indent=2, ensure_ascii=False))

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

def organizeturn(turn, delex):
    new_turn = turn.copy()
    new_turn["utterance"] = delex
    new_turn["utterance_delex"] = delex
    new_turn["slot-values"] = turn["slot-values"].copy()
    return new_turn

def str_time_prop(start, end, format, prop):
    stime = time.mktime(time.strptime(start, '%d/%m/%Y'))
    etime = time.mktime(time.strptime(end, '%d/%m/%Y'))
    ptime = stime + prop * (etime - stime)
    return time.strftime(format, time.localtime(ptime))

def random_date(start, end, prop, format):
    return str_time_prop(start, end, format, prop)

def fill_ontology(data):
    slot_values = {}
    action = []
    intent = []

    for item in data["dialogs"]:
        for turn in item["turns"]:
            if "action" in turn.keys():
                acts = turn["action"].replace("][", ", ").replace("[", "").replace("]", "").split(", ")
                for value in acts:
                    if (str("["+value+"]") not in action): action.append(str("["+value+"]"))
                
            elif "intent" in turn.keys():
                ints = turn["intent"].replace("][", ", ").replace("[", "").replace("]", "").split(", ")
                for value in ints:
                    if (str("["+value+"]") not in intent): intent.append(str("["+value+"]"))

            for key in turn["slot-values"].keys():
                if (key not in slot_values.keys()): slot_values[key] = []
                if isinstance(turn["slot-values"][key], list):
                    for value in turn["slot-values"][key]:
                        if (value not in slot_values[key]):
                            slot_values[key].append(value)
                else:
                    if (turn["slot-values"][key] not in slot_values[key]):
                        slot_values[key].append(turn["slot-values"][key])

    data["ontology"]["slot-values"] = slot_values
    data["ontology"]["intents"] = intent
    data["ontology"]["actions"] = action
    return data

def get_train_test(data):
    global algtest
    train = data.copy()
    test = data.copy()
    train["dialogs"] = []
    test["dialogs"] = []

    for dialog in data["dialogs"]:
        if (str(dialog["id"]).endswith(algtest)):
            test["dialogs"].append(dialog.copy())
        else: train["dialogs"].append(dialog.copy())

    train = fill_ontology(train)
    test = fill_ontology(test)
    return train, test

def join_data_dialog(data, final, ids):
    for dialog in data["dialogs"]:
        if (("-" in str(dialog["id"]))or(str(dialog["id"]) not in ids)):
            while (str(dialog["id"]) in ids):
                sequence = str(dialog["id"]).split("-")
                sequence[0] = str(int(sequence[0])+1)
                dialog["id"] = "-".join(sequence)
            final["dialogs"].append(dialog.copy())
            ids.append(str(dialog["id"]))

def join_datasets(datasets):
    data = datasets[0].copy()
    data["dialogs"] = []
    ids = []

    for i in range(len(datasets)):
        join_data_dialog(datasets[i], data, ids)
    data = fill_ontology(data)
    return data

def join_train_test(train, test):
    return join_datasets([train, test])