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
        new_dialog = []
        for turn in dialog:
            new_turn = turn.copy()
            if new_turn["speaker"] == "client":
                aug_text = augment(new_turn["utterance_delex"].lower())
                new_turn["utterance_delex"] = random.choice(aug_text)
            new_turn["utterance"] = new_turn["utterance_delex"]
            if "[cpf]" in new_turn["utterance"]:
                cpf = gen_cpf()
                current_values["cpf"] = cpf
                new_turn["utterance"] = new_turn["utterance"].replace("[cpf]", cpf)
            if "[placa]" in new_turn["utterance"]:
                placa = gen_placa()
                current_values["placa"] = placa
                new_turn["utterance"] = new_turn["utterance"].replace("[placa]", placa)
            if new_turn["speaker"] == "client":
                new_turn["slot-values"] = current_values.copy()
            new_dialog.append(new_turn)
        out_data.append({
            "id": f"{size+i}",
            "dialog_domain": "consulta_saldo",
            "turns": new_dialog})
        data["dialogs"] = out_data
    with open("dialogs.mada.json", "w") as fout:
        json.dump(data, fout, indent=2, ensure_ascii=False, sort_keys=True)


if __name__ == "__main__":
    main()
