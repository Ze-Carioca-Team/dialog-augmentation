from collections import defaultdict
import deanonymization as deanony
from tqdm import tqdm
import argparse
import random
import json
import util
random.seed(20211109)

def bfs(pflow, intent_sample, size, example, rate = 0.91, silence = False, mode = "test"):
    count = 0
    samples = []
    visit = []

    lastalg = util.algtest
    if ("train" in mode): lastalg = util.algtrain

    for flow in pflow: visit.append((flow,[]))
    while (visit):
        flow, dialog = visit.pop(0)
        if (flow):
            agent = "intent" if (len(flow) % 2 == 0) else "action"
            for turn in intent_sample[agent][flow[0]]:
                if (random.random() > float(rate)):
                    visit.append((flow[1:], dialog+[turn]))
        else:
            count += 1
            result = example.copy()
            result["id"] = str(size+count)
            result["id"] += random.sample(lastalg, k=1)[0]
            result["turns"] = dialog
            samples.append(result)
            if ((count % 100 == 0)and(silence == False)):
                print(f"Generated {count} dialogues...")
    return samples

def mada(data, rate = 0.91, silence = False, mode = "test"):
    possible_flows = []
    intent_sample = {"intent" : defaultdict(list), "action" : defaultdict(list)}
    for dialog in data["dialogs"]:
        dialog["id"] = str(dialog["id"])
        curr_flow = []
        for turn in dialog["turns"]:
            agent = "intent" if (turn["turn-num"] % 2 == 0) else "action"
            utt = turn[agent]
            curr_flow.append(utt)
            intent_sample[agent][utt].append(turn)
        if (curr_flow not in possible_flows): possible_flows.append(curr_flow)

    size = len(data["dialogs"])
    if (size > 0):
        samples = bfs(possible_flows, intent_sample, size,
                      data["dialogs"][0], rate, silence, mode)
        result = data.copy()
        for key in data.keys():
            try: result[key] = data[key].copy()
            except: continue
        result["dialogs"] = samples.copy()
    else: return data
    return result

def build_mada(data, mode, args):
    data = mada(data, args.rate, args.silence, mode)
    data = deanony.deanonymization(data, True)
    data = util.fill_ontology(data)
    random.shuffle(data["dialogs"])
    util.format_jsonfile(data, args.filename, ".mada"+str(mode))
    return data

def parse_args():
    parser = argparse.ArgumentParser(description="Applying MADA on a dialog dataset formatted in the MultiWOZ pattern.")
    parser.add_argument("--filename", type=str, default="original.json", help="Path to dialogs dataset.")
    parser.add_argument("--rate", type=str, default=0.91, help="Pruning probability in the MADA tree of possibilities.")
    parser.add_argument("--silence", type=str, default=False, help="Keep algorithm muted (do not show outputs).")
    return parser.parse_args()

def main(args):
    data = None
    with open(args.filename) as fin: data = json.load(fin)

    train, test = util.get_train_test(data)
    train = build_mada(train, ".train", args)
    test = build_mada(test, ".test", args)

    data = util.join_train_test(train, test)
    data = deanony.deanonymization(data, True)
    data = util.fill_ontology(data)
    random.shuffle(data["dialogs"])
    util.format_jsonfile(data, args.filename, ".mada")

if __name__ == "__main__":
    args = parse_args()
    main(args)