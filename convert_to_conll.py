# Portuguese dataset
from pathlib import Path
from typing import List


def find_sublist_match(phrase, string_to_find, start=0):
    start_match = 0
    end_match = 0
    string_to_find = string_to_find.split(' ')

    phrase_tokens = phrase.split(' ')

    if start is None:
        start = 0

    if len(string_to_find) < 1:
        print("Vazio!")

    def clean_word(word):
        return word.strip("'").strip('"').strip('.')

    first_to_find = clean_word(string_to_find[0])
    last_to_find = clean_word(string_to_find[-1])
    for pos in range(start, len(phrase_tokens)):
        if first_to_find == clean_word(phrase_tokens[pos]):
            print(f"Achei {first_to_find} na pos {pos}")
            start_match = pos

            for pos_fim in range(pos, len(phrase_tokens)):
                if (last_to_find == clean_word(phrase_tokens[pos_fim])) and (
                        pos_fim - start_match >= len(string_to_find) - 2):
                    print(f"Achei o FIM {last_to_find} na pos {pos_fim}")
                    end_match = pos_fim
                    break
            if (len(string_to_find) == 1 or end_match > 0) and (
                    (abs((end_match - start_match) - len(string_to_find)) < 10) or (
                    (end_match - start_match) > len(string_to_find))):
                break

    tokens = []

    if (len(string_to_find) > 1 and end_match == 0) or (
            (abs((end_match - start_match) - len(string_to_find)) > 10) and (
            (end_match - start_match) < len(string_to_find))):
        print(
            f"[ERROR] Nao encontrei {string_to_find} sentenca {phrase} | first_to_find{first_to_find} last_to_find{last_to_find}")

        return None, None
        # sentence = Sentence(' '.join(string_to_find))
        # # embed words in sentence
        # if list(embeddings[0]._embeddings.keys())[0].startswith('bert'):
        #     result = EMBEDDING.embed(sentence)[0]
        # else:
        #     result = EMBEDDING_XLI.embed(sentence)[0]
        #
        # for token in result.tokens:
        #     tokens.append(token)

    else:
        print(
            f"[OK] encontrei {string_to_find} sentenca {phrase} | first_to_find{first_to_find} last_to_find{last_to_find}")
        # for pos in range(start_match, end_match + 1):
        #     tokens.append(embeddings.tokens[pos])

    return start_match, end_match


def convert_to_conll(sentence):
    frase = sentence['phase']
    extracao = sentence['extractions'][0]
    start_pos_arg1, end_pos_arg1 = find_sublist_match(frase, extracao['arg1'])
    start_pos_rel, end_pos_rel = find_sublist_match(frase, extracao['rel'], end_pos_arg1)
    start_pos_arg2, end_pos_arg2 = find_sublist_match(frase, extracao['arg2'], end_pos_rel)

    # TODO, so pegamos a 1º extracao
    # TODO, nao está funcionando quando a palavra é decomposta = num => em um

    result = []

    if any(elem is None for elem in [start_pos_arg1, start_pos_rel, start_pos_arg2]):
        print('Elemento quebrado')
    else:
        print('Elemento Funfando')

        for idx, token in enumerate(frase.split(' ')):

            actual_tag = '*'

            if idx == start_pos_arg1 and idx == end_pos_arg1:
                actual_tag = '(ARG0*)'
            elif idx == start_pos_arg1:
                actual_tag = '(ARG0*'
            elif end_pos_arg1 < idx > start_pos_arg1:
                actual_tag = '*'
            elif idx == end_pos_arg1:
                actual_tag = '*)'

            if idx == start_pos_rel and idx == end_pos_rel:
                actual_tag = '(V*)'
            elif idx == start_pos_rel:
                actual_tag = '(V*'
            elif end_pos_rel < idx > start_pos_rel:
                actual_tag = '*'
            elif idx == end_pos_rel:
                actual_tag = '*)'

            if idx == start_pos_arg2 and idx == end_pos_arg2:
                actual_tag = '(ARG1*)'
            elif idx == start_pos_arg2:
                actual_tag = '(ARG1*'
            elif end_pos_arg2 < idx > start_pos_arg2:
                actual_tag = '*'
            elif idx == end_pos_arg2:
                actual_tag = '*)'
            line = f"0\t{idx}\t{token}\tXX\t-\t-\t-\t-\t-\t*\t{actual_tag}\t-"

            result.append(line)

    return result


def load_dataset():
    dataset_pt = dict()

    pt = Path("gamalho_dataset/sentences.txt")
    with open(pt, 'r', encoding='utf-8') as f_pt:
        for line in f_pt:
            line = line.strip()
            pos, phase = line.split('\t', 1)
            dataset_pt[int(pos)] = {"phase": phase.strip(),
                                    "extractions": []
                                    }

    pt = Path("gamalho_dataset/argoe-pt-labeled.csv")
    with open(pt, 'r', encoding='utf-8') as f_pt:
        for line in f_pt:
            if '\t' in line:
                partes = line.split("\t")
                pos = int(partes[0])
                arg1 = partes[1].strip('"')
                rel = partes[2].strip('"')
                arg2 = partes[3].strip('"')
                valid = partes[-1].strip()

                if valid != '1':
                    continue  # so queremos pegar as positivas

                dataset_pt[pos]['extractions'].append({"arg1": arg1,
                                                       "rel": rel,
                                                       "arg2": arg2,
                                                       "valid": int(valid)})

    return dataset_pt


if __name__ == '__main__':
    dataset = load_dataset()

    actual_pos = 0

    with open('saida.gold_conll', 'w', encoding='utf-8') as f_out:
        with open('sentencas_teste.txt', 'w', encoding='utf-8') as f_teste:
            for idx, value in dataset.items():
                if len(value['extractions']) > 0:
                    result = convert_to_conll(value)

                    if len(result) < 1:
                        f_teste.write(f"{value['phase']}\n")
                        continue

                    actual_pos += 1
                    for line in result:
                        f_out.write(f"train/train/01\t{line}\n")

                    f_out.write('\n')
                else:
                    f_teste.write(f"{value['phase']}\n")
