import json
import random
from deanony import gen_placa, gen_cpf, gen_nome, gen_valor
from tqdm import tqdm
from collections import defaultdict

random.seed(20211109)
intent_sample = {"intent":defaultdict(list), "action":defaultdict(list)}
counter = defaultdict(int)
samples = []
count = 0

def dfs(flow, dialog=[], num=0):
    global count
    if flow:
        agent = "intent" if num % 2 == 0 else "action"
        for turn in intent_sample[agent][flow[0]]:
            if random.random() > .7: return
            turn["turn-num"] = num
            dfs(flow[1:], dialog+[turn], num+1)
    count += 1
    if count % 100 == 0:
        print(f"Generated {count} dialogues...")
    samples.append(dialog)

def main():
    possible_flows = set()

    with open("dialogs.json") as fin:
        data = json.load(fin)
    for dialog in data["dialogs"]:
        dialog["id"] = str(dialog["id"])
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
    size = len(data["dialogs"])
    for i, dialog in enumerate(tqdm(samples)):
        current_values = {}
        for num, turn in enumerate(dialog):
            turn["utterance"] = turn["utterance_delex"]
            turn["slot-values"] = {}
            nome = None
            if "intent" in turn and "[negacao]" in turn["intent"]:
                current_values = {}
            if "[cpf]" in turn["utterance"]:
                cpf = gen_cpf()
                current_values["cpf"] = cpf
                turn["utterance"] = turn["utterance"].replace("[cpf]", cpf)
                turn["slot-values"]["cpf"] = cpf
            if "[placa]" in turn["utterance"]:
                placa = gen_placa()
                current_values["placa"] = placa
                turn["utterance"] = turn["utterance"].replace("[placa]", placa)
                turn["slot-values"]["placa"] = placa
            if "[nome]" in turn["utterance"]:
                if (nome == None):
                    nome = gen_nome()
                current_values["nome"] = nome
                turn["utterance"] = turn["utterance"].replace("[nome]", nome)
            if turn["speaker"] == "client":
                turn["slot-values"] = current_values
        data["dialogs"].append({
            "id": f"{size+i}",
            "dialog_domain": "consulta_saldo",
            "turns": dialog})
    with open("dialogs.mada.json", "w") as fout:
        json.dump(data, fout, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
