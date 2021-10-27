import json
import random
from tqdm import tqdm
from pprint import pprint
from collections import defaultdict
import nlpaug.augmenter.word as naw
from augment import gen_placa, gen_nome, gen_cpf

intent_sample = {"intent":defaultdict(list), "action":defaultdict(list)}
counter = defaultdict(int)
samples = []
count = 0

def dfs(flow, dialog=[], num=0):
    global count
    if flow:
        agent = "intent" if num % 2 == 0 else "action"
        for turn in intent_sample[agent][flow[0]]:
            turn["turn-num"] = num
            dfs(flow[1:], dialog+[turn], num+1)
    elif random.random() > .999:
        count += 1
        if count % 100 == 0:
            print(f"Generated {count} dialogues...")
        samples.append(dialog)

def main():
    possible_flows = set()

    with open("synthetic_anotado.json") as fin:
        data = json.load(fin)
    for dialog in data["dialogs"]:
        dialog["id"] = str(dialog["id"])
        # if dialog["id"].endswith(("1","2","3")): continue
        if dialog["id"].endswith(("2","3")): continue
        curr_flow = []
        for turn in dialog["turns"]:
            agent = "intent" if turn["turn-num"] % 2 == 0 else "action"
            utt = turn[agent]
            curr_flow.append(utt)
            counter[utt] += 1
            intent_sample[agent][utt].append(turn)
        possible_flows.add(tuple(curr_flow))

    for flow in possible_flows:
        dfs(flow)
    model_name = "neuralmind/bert-large-portuguese-cased"
    # TODO: fix tokenizer to not replace special tokens
    aug1 = naw.SynonymAug(aug_src='wordnet', lang='por', aug_max=1,
                          stopwords=["[cpf]", "[nome]", "[placa]"])
    # aug1 = naw.ContextualWordEmbsAug(model_path=model_name, model_type="bert",
    #                                  aug_max=1, stopwords=["[", "]", "cpf", "nome", "placa"])
    size = len(data["dialogs"])
    for i, dialog in enumerate(tqdm(samples)):
        selected_values = {"cpf": [], "placa": [], "valor": [], "nome": []}
        for num, turn in enumerate(dialog):
            # turn["utterance_delex"] = aug1.augment(turn["utterance_delex"])
            turn["utterance"] = turn["utterance_delex"]
            turn["slot-values"] = {}
            nome = None
            if "[cpf]" in turn["utterance"]:
                cpf = gen_cpf()
                selected_values["cpf"].append(cpf)
                turn["utterance"] = turn["utterance"].replace("[cpf]", cpf)
                turn["slot-values"]["cpf"] = cpf
            if "[placa]" in turn["utterance"]:
                placa = gen_placa()
                selected_values["placa"].append(placa)
                turn["utterance"] = turn["utterance"].replace("[placa]", placa)
                turn["slot-values"]["placa"] = placa
            if "[nome]" in turn["utterance"]:
                if (nome == None):
                    nome = gen_nome()
                    selected_values["nome"].append(nome)
                turn["utterance"] = turn["utterance"].replace("[nome]", nome)
                turn["slot-values"]["nome"] = nome
        data["dialogs"].append({
            "id": f"{(i*10000)+(i%6)+4}",
            "dialog_domain": "consulta_saldo",
            "turns": dialog})
    with open("synthetic_anotado_damd.json", "w") as fout:
        json.dump(data, fout, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
