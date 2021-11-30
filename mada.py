import json
import random
from eda import eda
from tqdm import tqdm
from collections import defaultdict
from deanony import gen_placa, gen_cpf, gen_nome, gen_valor

random.seed(20211109)

def augment(sentence):
    return eda(sentence, ["[cpf]", "[placa]", "[valor]"])

def bfs(pflow, intent_sample):
    count = 0
    samples = []
    visit = []
    for flow in pflow:
        visit.append((flow,[]))
    while visit:
        flow, dialog = visit.pop(0)
        if flow:
            agent = "intent" if len(flow) % 2 == 0 else "action"
            for turn in intent_sample[agent][flow[0]]:
                if random.random() > .91:
                    visit.append((flow[1:], dialog+[turn]))
        else:
            count += 1
            samples.append(dialog)
            if count % 100 == 0: print(f"Generated {count} dialogues...")
    return samples

def main():
    possible_flows = []
    intent_sample = {"intent":defaultdict(list), "action":defaultdict(list)}
    with open("dialogs.json") as fin:
        data = json.load(fin)
    for dialog in data["dialogs"]:
        dialog["id"] = str(dialog["id"])
        if dialog["id"].endswith(("1","2","3")): continue
        curr_flow = []
        for turn in dialog["turns"]:
            agent = "intent" if turn["turn-num"] % 2 == 0 else "action"
            utt = turn[agent]
            curr_flow.append(utt)
            intent_sample[agent][utt].append(turn)
        if curr_flow not in possible_flows:
            possible_flows.append(curr_flow)
    samples = bfs(possible_flows, intent_sample)
    size = len(data["dialogs"])
    out_data = []
    for i, dialog in enumerate(tqdm(samples)):
        current_values = {}
        for num, turn in enumerate(dialog):
            turn["turn-num"] = num
            if turn["speaker"] == "client":
                aug_text = augment(turn["utterance_delex"].lower())
                turn["utterance_delex"] = random.choice(aug_text)
            turn["utterance"] = turn["utterance_delex"]
            if "[cpf]" in turn["utterance"]:
                cpf = gen_cpf()
                current_values["cpf"] = cpf.replace(" ","").replace("-","").replace(".","")
                turn["utterance"] = turn["utterance"].replace("[cpf]", cpf)
            if "[placa]" in turn["utterance"]:
                placa = gen_placa()
                current_values["placa"] = placa.replace(" ","").replace("-","")
                turn["utterance"] = turn["utterance"].replace("[placa]", placa)
            if turn["speaker"] == "client":
                turn["slot-values"] = current_values.copy()
        out_data.append({
            "id": f"{i*1000}",
            "dialog_domain": "consulta_saldo",
            "turns": dialog})
    random.shuffle(out_data)
    data["dialogs"] += out_data
    with open("dialogs.mada.json", "w") as fout:
        json.dump(data, fout, indent=2, ensure_ascii=False, sort_keys=True)


if __name__ == "__main__":
    main()
