import backtranslation
import deanonymization
import argparse
import random
import mada
import util
import json
import eda

def parse_args():
    parser = argparse.ArgumentParser(description="Applying data augmentation on a dialog dataset formatted in the MultiWOZ pattern.")
    parser.add_argument("--filename", type=str, default="original.json", help="Path to dialogs dataset.")
    parser.add_argument("--min_sents", type=str, default=4, help="Minimum number of new sentences generated.")
    parser.add_argument("--max_sents", type=str, default=14, help="Maximum number of new sentences generated.")
    parser.add_argument("--silence", type=str, default=False, help="Keep algorithm muted (do not show outputs).")
    parser.add_argument("--path_model", type=str, default="wiki.pt.bin", help="Language model that will be used.")
    parser.add_argument("--names_dir", type=str, default="names.json", help="Path to file with Brazilian names.")
    parser.add_argument("--lastnames_dir", type=str, default="lastnames.json", help="Path to file with Brazilian lastnames.")
    parser.add_argument("--swap", type=str, default=False, help="Perform only the swap of entity values, without data augmentation.")
    parser.add_argument("--anonymize", type=str, default=False, help="Perform a pre-anonymization of data, identifying the entities present in each sentence.")
    parser.add_argument("--bert_path", type=str, default="bert_entities_model/", help="Path to Bert model for entity identification.")
    parser.add_argument("--rate", type=str, default=0.93, help="Pruning probability in the MADA tree of possibilities.")
    parser.add_argument("--min_bleu", type=str, default=0.0, help="Minimum bleu metric value for a backtranslation to be selected.")
    return parser.parse_args()

def join(data_a, data_b, original_path):
    data = util.join_train_test(data_a[1], data_b[1])
    data = deanonymization.deanonymization(data, True)
    data = util.fill_ontology(data)
    random.shuffle(data["dialogs"])

    label = data_a[0]+data_b[0]
    util.format_jsonfile(data, original_path, label)
    args.filename = original_path.replace(".json", label+".json")
    deanonymization.main(args)
    return [label, data]

def main(args):
    backtranslation.main(args)
    deanonymization.main(args)
    mada.main(args)
    eda.main(args)

    original_path = args.filename
    methods = [[".eda", None], [".mada", None], 
               [".backtranslated", None]]

    for i in range(len(methods)):
        label = methods[i][0]
        args.filename = original_path.replace(".json", label+".json")
        deanonymization.main(args)

        dfile = open(args.filename, "r", encoding='utf-8')
        methods[i][1] = json.load(dfile)
        dfile.close()

    new_methods = []
    for i in range(len(methods)-1):
        for j in range(i+1, len(methods)):
            new_methods.append(join(methods[i], methods[j], original_path))
    methods += new_methods
    methods.append(join(methods[0], methods[-1], original_path))

if __name__ == '__main__':
    args = parse_args()
    main(args)