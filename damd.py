import json
import random
from pprint import pprint
from collections import defaultdict

intent_sample = defaultdict(list)
counter = defaultdict(int)
samples = []
count = 0

def dfs(flow, dialog=[], num=0):
    global count
    if flow:
        for turn in intent_sample[flow[0]]:
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
        if str(dialog["id"]).endswith(("1","2","3")): continue
        curr_flow = []
        for turn in dialog["turns"]:
            agent = "intent" if turn["turn-num"] % 2 == 0 else "action"
            utt = turn[agent]
            curr_flow.append(utt)
            counter[utt] += 1
            intent_sample[utt].append(turn)
        possible_flows.add(tuple(curr_flow))
    for i in counter.items():
        print(i)

    for flow in possible_flows:
        dfs(flow)

    size = len(data["dialogs"])
    for i, dialog in enumerate(samples):
        data["dialogs"].append({
            "id": f"damd{i}-{(i%5)+3}",
            "dialog_domain": "consulta_saldo",
            "turns": dialog})
    with open("synthetic_anotado_damd.json", "w") as fout:
        json.dump(data, fout, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
