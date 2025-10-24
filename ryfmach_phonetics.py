from ryfmach import get_word_data_from_db, get_word_dict
import language
from language import *
import sounds
from pprint import pprint


class PHONETIC_PHENOMENA:
    IOTATION = 0
    CONS_SOFTENING = 1
    AFFRICATES = 2
    THUD_ASSIMILATION = 3
    RING_ASSIMILATION = 4
    SOFT_ASSIMILATION = 5
    WHISTL_ASSIMILATION = 6
    HISS_ASSIMILATION = 7
    DENTAL_ASSIMILATION = 8


def get_transcription_full(word, accent):
    letter_to_sounds = [[] for _ in range(len(word))]
    t = []
    phenomena = []
    for i in range(len(word)):
        if word[i] in "аоуыэі":
            if accent == i:
                t.append(f"_{word[i]}_")
            else:
                t.append(word[i])
            letter_to_sounds[i] += [len(t) - 1]
            
        elif word[i] in vowels:
            if accent == i:
                t.append(f"_{iotation[word[i]]}_")
            else:
                t.append(iotation[word[i]])
                    
            letter_to_sounds[i] += [len(t) - 1]

        elif word[i] in consonants:
            t.append(word[i])
            letter_to_sounds[i] += [len(t) - 1]


    for i in range(len(word)):
        if word[i] in vowels and not word[i] in "аоуыэі":
            # ётацыя
            if (i == 0 or
                word[i - 1] in vowels or
                word[i - 1] == "ў" or
                word[i - 1] == "ь" or
                word[i - 1] == "'" or
                word[i - 1] == "-"):
                    sound_i = letter_to_sounds[i][0]
                    phenomena.append((sound_i, t.copy(), PHONETIC_PHENOMENA.IOTATION))
                    t.insert(sound_i, "й")

                    # for j in range(len(phenomena)):
                    #     if phenomena[j][0] >= sound_i:
                    #         phenomena[j] = (phenomena[j][0] + 1, *phenomena[j][1:])
                    for j in range(len(letter_to_sounds)):
                        letter_to_sounds[j] = [s if s < sound_i else s + 1 for s in letter_to_sounds[j]]
                        if letter_to_sounds[j] and letter_to_sounds[j][0] == sound_i + 1:
                             letter_to_sounds[j].insert(0, sound_i)

        elif word[i] in consonants:
            sound_i = letter_to_sounds[i][-1]
            # змягчэнне зычных
            if (i + 1 < len(word) and
                (word[i + 1] in softening_vowels or word[i + 1] == 'ь') and
                soft_pair(t[sound_i])):
                    if t[sound_i] == 'ц':
                        t[sound_i] = 'т'
                    phenomena.append((sound_i, t.copy(), PHONETIC_PHENOMENA.CONS_SOFTENING))
                    t[sound_i] = soft_pair(t[sound_i])
    
    # афрыкаты
    i = 0
    while i < len(t) - 1:
        if t[i] == "д" and t[i + 1] in ["ж", "з", "з'"]:
            phenomena.append((i, t.copy(), PHONETIC_PHENOMENA.AFFRICATES))
            # for j in range(len(phenomena)):
            #     if phenomena[j][0] >= i + 1:
            #         phenomena[j] = (phenomena[j][0] - 1, *phenomena[j][1:])
            t[i] += t[i + 1]
            for j in range(len(letter_to_sounds)):
                for k in range(len(letter_to_sounds[j])):
                    if letter_to_sounds[j][k] >= i + 1:
                        letter_to_sounds[j][k] -= 1
            t.pop(i + 1)
        i += 1

    changed = True
    while (changed):
        changed = False

        for i in range(len(t)):
            # асіміляцыя па глухасці + аглушэнне на канцы
            if (is_ring(t[i]) and thud_pair(t[i]) and
                (i + 1 >= len(t) or is_thud(t[i + 1]))):
                    phenomena.append((i, t.copy(), PHONETIC_PHENOMENA.THUD_ASSIMILATION))
                    t[i] = thud_pair(t[i])
                    changed = True
            # асіміляцыя па звонкасці
            elif (is_thud(t[i]) and ring_pair(t[i]) and
                (i + 1 < len(t) and is_ring(t[i + 1]) and not is_sonor(t[i + 1]))):
                    phenomena.append((i, t.copy(), PHONETIC_PHENOMENA.RING_ASSIMILATION))
                    t[i] = ring_pair(t[i])
                    changed = True

            # асіміляцыя па мяккасці
            if (i + 1 < len(t) and
                (t[i] in ["з", "с"] and is_soft(t[i + 1]) and t[i + 1] not in ["г'", "к'", "х'"] or 
                 t[i] in ["д", "т", "дз", "ц"] and t[i + 1] == "в'")):
                    phenomena.append((i, t.copy(), PHONETIC_PHENOMENA.SOFT_ASSIMILATION))
                    t[i] = soft_pair(t[i])
                    changed = True

            # прыпадабненне шыпячага да свісцячага
            if (i + 1 < len(t) and
                is_hiss(t[i]) and is_whistl(t[i + 1])):
                    phenomena.append((i, t.copy(), PHONETIC_PHENOMENA.WHISTL_ASSIMILATION))
                    t[i] = whistl_pair(t[i])
                    changed = True
            # прыпадабненне свісцячага да шыпячага
            elif (i + 1 < len(t) and
                is_whistl(t[i]) and is_hiss(t[i + 1])):
                    phenomena.append((i, t.copy(), PHONETIC_PHENOMENA.HISS_ASSIMILATION))
                    t[i] = hiss_pair(t[i])
                    changed = True

            # асіміляцыя зубных гукаў
            if (i + 1 < len(t) and
                t[i] in ["д", "т"] and t[i + 1] in ["ц", "ч"]):
                    phenomena.append((i, t.copy(), PHONETIC_PHENOMENA.DENTAL_ASSIMILATION))
                    t[i] = t[i + 1]
                    changed = True

    return letter_to_sounds, t, phenomena


def input_phonetic_analysis(input_word_info):
    input_word_info["word"] = input_word_info["word"].replace("и", "і")
    input_word_info["word"] = input_word_info["word"].replace("щ", "ў")
    input_word_info["word"] = input_word_info["word"].replace("ъ", "'")

    if not is_belarusian(input_word_info["word"]) or len(input_word_info["word"]) > 40:
        return []
    if input_word_info.get("accent") is None:
        word_variants = get_word_data_from_db(input_word_info["word"].lower(),
                                              fix_similar_letters=True)
    else:
        word_variants = [input_word_info]
    
    analysed = []
    for wv in word_variants:
        analysed.append(word_phonetic_analysis(wv))
        
    pprint(analysed)
    return analysed


def word_phonetic_analysis(wdict: dict):
    letter_to_sounds, tr, phenomena = get_transcription_full(wdict["word"], wdict["accent"])
    letter_map = []

    i = 0
    while i < len(letter_to_sounds):
        if i > 0 and letter_to_sounds[i - 1] == letter_to_sounds[i]:
            letter_map[-1][0] += [i]
        else:
            letter_map.append([[i], letter_to_sounds[i]])
        i += 1
    
    print(letter_to_sounds)
    print(letter_map, tr, phenomena)
    if __name__ == "__main__":
        print(letter_map, tr, phenomena)
    
        # for ph in phenomena:
        #     print(ph[2])
        #     for c in ph[1]:
        #         print(c.rjust(4, ' '), end='')
        #     print()
        #     print('    ' * ph[0] + '   ^', ph[0])
        
        # for c in tr:
        #     print(c.rjust(4, ' '), end='')
        # print()

    return {
         "word_variant": wdict,
         "letter_map": letter_map,
         "transcription": tr,
         "phenomena": phenomena
    }


if __name__ == "__main__":
    word_phonetic_analysis({
         "word": "неба",
         "accent": 1,
    })
    
    word_phonetic_analysis({
         "word": "ксёндз",
         "accent": 2,
    })
    
    word_phonetic_analysis({
         "word": "гвоздзь",
         "accent": 2,
    })
    
    word_phonetic_analysis({
         "word": "нарэшце",
         "accent": 3,
    })
