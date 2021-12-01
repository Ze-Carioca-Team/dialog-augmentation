import json
import pprint
import argparse
import random

def parse_args():
    parser = argparse.ArgumentParser(description="Applying MADA on a dialog dataset formatted in the MultiWOZ pattern.")
    parser.add_argument("--filename", type=str, default="dialogs.json", help="Path to dialogs dataset.")
    return parser.parse_args()

def main():
    args = parse_args()
    with open(args.filename, encoding='utf-8') as fin:
        data = json.load(fin)
    for dialog in random.sample(data['dialogs'], 10):
        for turn in dialog['turns']:
            pprint.pprint(turn)
            print('\n')
        print('-----------------------')

if __name__ == "__main__":
    main()
