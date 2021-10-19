import json
import random
from pprint import pprint
from collections import defaultdict

intent_sample = defaultdict(list)
counter = defaultdict(int)
samples = []
count = 0

def dfs(flow, utterances=[]):
    global count
    if flow:
        for utt in intent_sample[flow[0]]:
            dfs(flow[1:], utterances+[utt])
    elif random.random() > .9999:
        count += 1
        if count % 100 == 0:
            print(f"Generated {count} dialogues...")
        samples.append(utterances)

def main():
    possible_flows = set()

    with open("synthetic_anotado.json") as fin:
        data = json.load(fin)
    for dialog in data["dialogs"]:
        curr_flow = []
        for turn in dialog["turns"]:
            agent = "intent" if turn["turn-num"] % 2 == 0 else "action"
            utt = turn[agent]
            curr_flow.append(utt)
            counter[utt] += 1
            intent_sample[utt].append(turn["utterance_delex"])
        possible_flows.add(tuple(curr_flow))
    for i in counter.items():
        print(i)

    for flow in possible_flows:
        dfs(flow)

if __name__ == "__main__":
    main()
