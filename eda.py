# This is a modified version of EDA
# Easy data augmentation techniques for text classification
# Jason Wei and Kai Zou

from gensim.models.fasttext import load_facebook_vectors
import deanonymization as deanony
from random import shuffle
import argparse
import random
import json
import util
random.seed(1)
model = None

def load_model(path_model = "wiki.pt.bin", silence = False):
    global model
    if (silence == False): print("Loading word vectors...")
    model = load_facebook_vectors(path_model)
    if (silence == False): print("Done.")

########################################################################
# Synonym replacement
# Replace n words in the sentence with synonyms from wordnet
########################################################################

def synonym_replacement(words, n, stop_words):
    new_words = words.copy()
    random_word_list = list(set([word for word in words if word]))
    random.shuffle(random_word_list)
    num_replaced = 0
    for random_word in random_word_list:
        if random_word in stop_words: continue
        synonyms = get_synonyms(random_word)
        if len(synonyms) >= 1:
            synonym = random.choice(list(synonyms))
            new_words = [synonym if word == random_word else word for word in new_words]
            num_replaced += 1
        if num_replaced >= n: #only replace up to n words
            break

    #this is stupid but we need it, trust me
    sentence = ' '.join(new_words)
    new_words = sentence.split(' ')

    return new_words

def get_synonyms(word):
    global model
    synonyms = set()
    for syn in model.most_similar(word):
                synonym = syn[0]
                synonyms.add(synonym)
    if word in synonyms:
        synonyms.remove(word)
    return list(synonyms)

########################################################################
# Random deletion
# Randomly delete words from the sentence with probability p
########################################################################

def random_deletion(words, p):

    #obviously, if there's only one word, don't delete it
    if len(words) == 1:
        return words

    #randomly delete words with probability p
    new_words = []
    for word in words:
        r = random.uniform(0, 1)
        if r > p:
            new_words.append(word)

    #if you end up deleting all words, just return a random word
    if len(new_words) == 0:
        rand_int = random.randint(0, len(words)-1)
        return [words[rand_int]]

    return new_words

########################################################################
# Random swap
# Randomly swap two words in the sentence n times
########################################################################

def random_swap(words, n):
    new_words = words.copy()
    for _ in range(n):
        new_words = swap_word(new_words)
    return new_words

def swap_word(new_words):
    random_idx_1 = random.randint(0, len(new_words)-1)
    random_idx_2 = random_idx_1
    counter = 0
    while random_idx_2 == random_idx_1:
        random_idx_2 = random.randint(0, len(new_words)-1)
        counter += 1
        if counter > 3:
            return new_words
    new_words[random_idx_1], new_words[random_idx_2] = new_words[random_idx_2], new_words[random_idx_1]
    return new_words

########################################################################
# Random insertion
# Randomly insert n words into the sentence
########################################################################

def random_insertion(words, n):
    new_words = words.copy()
    for _ in range(n):
        add_word(new_words)
    return new_words

def add_word(new_words):
    synonyms = []
    counter = 0
    while len(synonyms) < 1:
        random_word = new_words[random.randint(0, len(new_words)-1)]
        synonyms = get_synonyms(random_word)
        counter += 1
        if counter >= 10:
            return
    random_synonym = synonyms[0]
    random_idx = random.randint(0, len(new_words)-1)
    new_words.insert(random_idx, random_synonym)

########################################################################
# main data augmentation function
########################################################################

def eda(sentence, stop_words, alpha_sr=0.1, alpha_ri=0.1, alpha_rs=0.1,
        p_rd=0.1, num_aug=9):

    words = sentence.split(' ')
    words = [word for word in words if word != '']
    num_words = len(words)

    augmented_sentences = []
    num_new_per_technique = int(num_aug/4)+1

    #sr
    if (alpha_sr > 0):
        n_sr = max(1, int(alpha_sr*num_words))
        for _ in range(num_new_per_technique):
            a_words = synonym_replacement(words, n_sr, stop_words)
            augmented_sentences.append(' '.join(a_words))

    #ri
    if (alpha_ri > 0):
        n_ri = max(1, int(alpha_ri*num_words))
        for _ in range(num_new_per_technique):
            a_words = random_insertion(words, n_ri)
            augmented_sentences.append(' '.join(a_words))

    #rs
    if (alpha_rs > 0):
        n_rs = max(1, int(alpha_rs*num_words))
        for _ in range(num_new_per_technique):
            a_words = random_swap(words, n_rs)
            augmented_sentences.append(' '.join(a_words))

    #rd
    if (p_rd > 0):
        for _ in range(num_new_per_technique):
            a_words = random_deletion(words, p_rd)
            augmented_sentences.append(' '.join(a_words))

    augmented_sentences = [sentence for sentence in augmented_sentences]
    shuffle(augmented_sentences)

    #trim so that we have the desired number of augmented sentences
    if num_aug >= 1:
        augmented_sentences = augmented_sentences[:num_aug]
    else:
        keep_prob = num_aug / len(augmented_sentences)
        augmented_sentences = [s for s in augmented_sentences if random.uniform(0, 1) < keep_prob]

    #append the original sentence
    augmented_sentences.append(sentence)

    return augmented_sentences

def build_eda(data, min_sents = 4, max_sents = 14):
    tags = util.define_tags(data)
    for i in range(len(tags)): tags[i] = tags[i][0]

    result = data.copy()
    result["dialogs"] = []
    for dialog in data["dialogs"]:
        amount = random.randint(min_sents, max_sents)
        augmented_sentences = []
        for turn in dialog["turns"]:
            if ("intent" in turn.keys()):
                new_sentences = eda(turn["utterance_delex"].lower(), tags, num_aug = amount)
                augmented_sentences.append(new_sentences)
            else: augmented_sentences.append([turn["utterance_delex"].lower()])

        result["dialogs"].append(dialog.copy())
        for key in dialog.keys():
            try: result["dialogs"][-1][key] = dialog[key].copy()
            except: continue

        for i in range(amount):
            result["dialogs"].append(dialog.copy())
            result["dialogs"][-1]["turns"] = []
            result["dialogs"][-1]["id"] = str(i)+"-"+result["dialogs"][-1]["id"]

            for j, turn in enumerate(dialog["turns"]):
                new_turn = turn.copy()
                for key in turn.keys():
                    try: new_turn[key] = turn[key].copy()
                    except: continue
                new_sentence = augmented_sentences[j][0]
                if ("intent" in turn.keys()):
                    new_sentence = augmented_sentences[j][i]
                new_turn["utterance_delex"] = new_sentence
                new_turn["utterance"] = new_sentence
                result["dialogs"][-1]["turns"].append(new_turn)

    return result

def parse_args():
    parser = argparse.ArgumentParser(description="Applying EDA on a dialog dataset formatted in the MultiWOZ pattern.")
    parser.add_argument("--filename", type=str, default="original.json", help="Path to dialogs dataset.")
    parser.add_argument("--min_sents", type=str, default=4, help="Minimum number of new sentences generated.")
    parser.add_argument("--max_sents", type=str, default=14, help="Maximum number of new sentences generated.")
    parser.add_argument("--silence", type=str, default=False, help="Keep algorithm muted (do not show outputs).")
    parser.add_argument("--path_model", type=str, default="wiki.pt.bin", help="Language model that will be used.")
    return parser.parse_args()

def main(args):
    load_model(args.path_model, args.silence)
    dfile = open(args.filename, "r", encoding='utf-8')
    data = json.load(dfile)
    dfile.close()

    result = build_eda(data, args.min_sents, args.max_sents)
    result = deanony.deanonymization(result, True)
    result = util.fill_ontology(result)
    random.shuffle(result["dialogs"])
    util.format_jsonfile(result, args.filename, ".eda")

if __name__ == '__main__':
    args = parse_args()
    main(args)