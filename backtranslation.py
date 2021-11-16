import deanonymization as deanony
import translators as ts
import threading
import argparse
import random
import json
import nltk
import util

tags = [["saldo", "{999}"], ["Saldo", "{998}"], ["Minha placa", "{997}"], ["minha placa", "{996}"], ["A placa", "{995}"], ["a placa", "{994}"], ["Placa", "{993}"], ["placa", "{992}"]]
idiomas = ["en", "zh", "ar", "ru", "fr", "de", "es", "pt", "it", "ja", "ko",
           "el", "nl", "hi", "tr", "ms", "th", "vi", "id", "he", "pl", "mn",
           "cs", "hu", "et", "bg", "da", "fi", "ro", "sv", "sl", "fa", "bs",
           "sr", "fj", "tl", "ht", "ca", "hr", "lv", "lt", "ur", "uk", "cy",
           "ty", "to", "sw", "sm", "sk", "af", "no", "bn", "mg", "mt", "otq",
           "tlh", "gu", "ta", "te", "pa", "am", "az", "ba", "be", "ceb", "cv",
           "eo", "eu", "ga", "emj", "zh-CHS", "zh-CHT", "wyw", "yue", "mww"]

def select_backtranslation(original, idioma, tradutor):
    result = ""
    try:
        if (tradutor == 0):
            trad = ts.google(original, if_use_cn_host=False, from_language='pt', to_language=idioma)
            result = ts.google(trad, if_use_cn_host=False, from_language=idioma, to_language='pt')
        elif (tradutor == 1):
            trad = ts.bing(original, if_use_cn_host=False, from_language='pt', to_language=idioma)
            result = ts.bing(trad, if_use_cn_host=False, from_language=idioma, to_language='pt')
        elif (tradutor == 2):
            trad = ts.sogou(original, is_detail_result=False, from_language='pt', to_language=idioma)
            result = ts.sogou(trad, is_detail_result=False, from_language=idioma, to_language='pt')
        elif (tradutor == 3):
            trad = ts.translate_html(original, translator=ts.google, from_language='pt', to_language=idioma, n_jobs=1, timeout=20.0)
            result = ts.translate_html(trad, translator=ts.google, from_language=idioma, to_language='pt', n_jobs=1, timeout=20.0)
        elif (tradutor == 4):
            trad = ts.translate_html(original, translator=ts.bing, from_language='pt', to_language=idioma, n_jobs=1, timeout=20.0)
            result = ts.translate_html(trad, translator=ts.bing, from_language=idioma, to_language='pt', n_jobs=1, timeout=20.0)
        elif (tradutor == 5):
            trad = ts.translate_html(original, translator=ts.alibaba, from_language='pt', to_language=idioma, n_jobs=1, timeout=20.0)
            result = ts.translate_html(trad, translator=ts.alibaba, from_language=idioma, to_language='pt', n_jobs=1, timeout=20.0)
        elif (tradutor == 6):
            trad = ts.translate_html(original, translator=ts.sogou, from_language='pt', to_language=idioma, n_jobs=1, timeout=20.0)
            result = ts.translate_html(trad, translator=ts.sogou, from_language=idioma, to_language='pt', n_jobs=1, timeout=20.0)
        elif (tradutor == 7):
            trad = ts.translate_html(original, translator=ts.deepl, from_language='pt', to_language=idioma, n_jobs=1, timeout=20.0)
            result = ts.translate_html(trad, translator=ts.deepl, from_language=idioma, to_language='pt', n_jobs=1, timeout=20.0)
    except: result = ""
    return result

def parallel_translation(original, rate, idioma, tradutor, currtags, traducoes):
    global tags
    retrad = select_backtranslation(original, idioma, tradutor)
    clearetrad = util.clear_punctuation(retrad)
    result, valid = util.replacetag(clearetrad, currtags, tags)
    bleu = nltk.translate.bleu_score.sentence_bleu([original], result)
    if ((valid)and(bleu >= rate)): traducoes.append(result)

def dialog_backtranslation(original_users, original_system, retrot, key, rate):
    global tags
    traducoes = [original_users]
    currtags = []
    for tag in tags:
        if (tag[0] in original_users):
            count = original_users.count(tag[0])
            original_users = original_users.replace(tag[0], tag[1])
            currtags.append([tag[1], count])

    threads = []
    for tradutor in range(3, 5):
        for idioma in random.sample(idiomas, k=int(float(len(idiomas))*0.5)):
            threads.append(threading.Thread(target=parallel_translation,
                           args=(original_users, rate, idioma,
                                 tradutor, currtags, traducoes,)))
            threads[-1].start()

    alive = len(threads)
    while (alive > 0):
        alive = 0
        for i in range(len(threads)):
            if (threads[i].is_alive()): alive += 1
            else: threads[i].join()
    threads = None

    for i in range(len(traducoes)):
        try:
            traducoes[i] = traducoes[i].split("<br>")
            lenusers = len(traducoes[i])
            aux = []
            for j in range(lenusers):
                aux.append(traducoes[i][j])
                if (j < len(original_system)):
                    aux.append(original_system[j])
            if (lenusers < len(original_system)):
                for j in range(len(original_system) - lenusers):
                    aux.append(original_system[lenusers + j])
            traducoes[i] = aux
        except: continue

    dictaug = retrot[key].copy()
    for i in range(len(traducoes[0])):
        for j in range(len(traducoes)):
            if (traducoes[j][i] not in dictaug[i]):
                dictaug[i].append(traducoes[j][i])
        dictaug[i] = list(set(dictaug[i]))
    retrot[key] = dictaug.copy()

def backtranslation(filename, min_bleu = 0.0):
    global tags
    data = None
    with open(filename, 'r', encoding='utf-8') as fin:
        data = json.load(fin)

    tags = util.define_tags(data, tags)
    retrot_dialogs = {}
    threads = []
    maxt = 2
    for dialog in data["dialogs"]:
        while (len(threads) == maxt):
            excluded = []
            for i in range(len(threads)):
                if (threads[i].is_alive() == False): excluded.append(i)
            for i in excluded:
                threads[i].join()
                util.format_jsonfile(retrot_dialogs, filename, ".btsentences")
                threads.pop(i)

        retrot_dialogs[dialog["id"]] = {}
        original_users = ""
        original_system = []

        if ("action" in dialog["turns"][0].keys()): dialog["turns"].pop(0)
        for i in range(len(dialog["turns"])):
            retrot_dialogs[dialog["id"]][i] = []
            if (i % 2 == 0): original_users += dialog["turns"][i]["utterance_delex"]+"<br>"
            else: original_system.append(dialog["turns"][i]["utterance_delex"])

        original_users = original_users[:-4]
        threads.append(threading.Thread(target=dialog_backtranslation, args=(original_users,
                       original_system, retrot_dialogs, dialog["id"], min_bleu,)))
        threads[-1].start()

    alive = len(threads)
    while (alive > 0):
        alive = 0
        for i in range(len(threads)):
            if (threads[i].is_alive()): alive += 1
            else: threads[i].join()

    util.format_jsonfile(retrot_dialogs, filename, ".btsentences")
    threads = None

def build_backtranslation(file_aug, file_original):
    data = None
    with open(file_aug, 'r', encoding='utf-8') as fin:
        data = json.load(fin)

    content = None
    with open(file_original, 'r', encoding='utf-8') as fin:
        content = json.load(fin)

    new_content = {}
    new_content["ontology"] = {"actions": None, "intents": None, "slot-values": None}
    new_content["dialogs"] = []

    for key in data.keys():
        max = 0
        newid = 1
        for turn in data[key].keys():
            if (len(data[key][turn]) > max): max = len(data[key][turn])

        original_dialog = None
        for dialog in content["dialogs"]:
            if (int(dialog["id"]) == int(key)):
                original_dialog = dialog.copy()

        dialogs = []
        textdia = []
        while (len(dialogs) < max):
            dialog = original_dialog.copy()
            dialog["turns"] = original_dialog["turns"].copy()
            text = ""
            for j in data[key].keys():
                index = random.sample(list(range(len(data[key][j]))), k = 1)[0]
                delex = data[key][j][index]
                dialog["turns"][int(j)] = util.organizeturn(dialog["turns"][int(j)], delex)
                text += delex

            if (text not in textdia):
                textdia.append(text)
                dialogs.append(dialog.copy())
                dialogs[-1]["turns"] = dialog["turns"].copy()

        for dialog in dialogs:
            dialog["id"] = str(newid)+"-"+str(key)
            newid += 1
            new_content["dialogs"].append(util.order_dialog(dialog.copy()))
            new_content["dialogs"][-1]["turns"] = dialog["turns"].copy()

    new_content = deanony.deanonymization(new_content, True)
    new_content = util.fill_ontology(new_content)
    random.shuffle(new_content["dialogs"])
    util.format_jsonfile(new_content, file_original, ".backtranslated")

def parse_args():
    parser = argparse.ArgumentParser(description="Backpropagation on a dialog dataset formatted in the MultiWOZ pattern.")
    parser.add_argument("--filename", type=str, default="original.json", help="Path to dialogs dataset.")
    parser.add_argument("--min_bleu", type=str, default=0.0, help="Minimum bleu metric value for a backtranslation to be selected.")
    return parser.parse_args()

def main(args):
    file_aug = args.filename.replace(".json", ".btsentences.json")
    backtranslation(args.filename, args.min_bleu)
    build_backtranslation(file_aug, args.filename)

if __name__ == '__main__':
    args = parse_args()
    main(args)