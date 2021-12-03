import json
import random
import argparse
from eda import eda
from tqdm import tqdm
from collections import defaultdict
from deanony import gen_placa, gen_cpf, gen_nome, gen_valor


def augment(sentence):
    return eda(sentence, ["[cpf]", "[placa]", "[valor]"])

def bfs(pflow, intent_sample, rate):
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
                if random.random() > rate:
                    visit.append((flow[1:], dialog+[turn]))
        else:
            count += 1
            samples.append(dialog)
            if count % 100 == 0: print(f"Generated {count} dialogues...")
    return samples

def parse_args():
    parser = argparse.ArgumentParser(description="Applying MADA on a dialog dataset formatted in the MultiWOZ pattern.")
    parser.add_argument("--filename", type=str, default="dialogs.json", help="Path to dialogs dataset.")
    parser.add_argument("--rate", type=float, default=0.91, help="Pruning probability in the MADA tree of possibilities.")
    parser.add_argument("--no-augment", default=True, help="Augment dataset.", dest='augment', action="store_false")
    return parser.parse_args()

def main():
    args = parse_args()
    possible_flows = []
    intent_sample = {"intent":defaultdict(list), "action":defaultdict(list)}
    with open(args.filename) as fin:
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
    samples = bfs(possible_flows, intent_sample, args.rate)
    size = len(data["dialogs"])
    out_data = []
    for i, dialog in enumerate(tqdm(samples)):
        new_dialog = []
        current_values = {}
        for num, turn in enumerate(dialog):
            new_turn = turn.copy()
            new_turn["turn-num"] = num
            if turn["speaker"] == "client":
                if args.augment:
                    random.seed(20211109+i)
                    aug_text = augment(new_turn["utterance_delex"].lower())
                    new_turn["utterance_delex"] = random.choice(aug_text)
                else:
                    new_turn["utterance_delex"] = new_turn["utterance_delex"].lower()
            new_turn["utterance"] = new_turn["utterance_delex"]
            if "[cpf]" in new_turn["utterance"]:
                cpf = gen_cpf()
                current_values["cpf"] = cpf
                new_turn["utterance"] = new_turn["utterance"].replace("[cpf]", cpf)
            if "[placa]" in new_turn["utterance"]:
                placa = gen_placa()
                current_values["placa"] = placa
                new_turn["utterance"] = new_turn["utterance"].replace("[placa]", placa)
            if turn["speaker"] == "client":
                new_turn["slot-values"] = current_values.copy()
            new_dialog.append(new_turn)
        out_data.append({
            "id": f"{i*1000}",
            "turns": new_dialog})
    random.shuffle(out_data)
    data["dialogs"] = out_data
    with open("out."+args.filename, "w") as fout:
        json.dump(data, fout, indent=2, ensure_ascii=False, sort_keys=True)


if __name__ == "__main__":
    main()
