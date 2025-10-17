import language
import ryfmach
import numpy as np
from pprint import pprint

cost_to_replace = {
    ("", ""): 0
}


def run_first_iter_replace_cost():
    # delete vowel
    for s in language.vowel_list:
        cost_to_replace[("_" + s + "_", "")] = 30
        cost_to_replace[(s, "")] = 10
        
    # replace vowel with vowel
    for s1 in language.vowel_list:
        for s2 in language.vowel_list:
            if s1 == s2:
                cost_to_replace[(s1, s1)] = 0
                cost_to_replace[("_" + s1 + "_", s1)] = 20
                cost_to_replace[("_" + s1 + "_", "_" + s1 + "_")] = 0
                break
            elif s1 + ";" + s2 in ["і;ы", "ы;і"]:
                cost_to_replace[(s1, s2)] = 0
                cost_to_replace[("_" + s1 + "_", s2)] = 0
                cost_to_replace[(s1, "_" + s2 + "_")] = 0
                cost_to_replace[("_" + s1 + "_", "_" + s2 + "_")] = 0
            else:
                cost_to_replace[(s1, s2)] = 1
                cost_to_replace[("_" + s1 + "_", s2)] = 30
                cost_to_replace[(s1, "_" + s2 + "_")] = 30
                cost_to_replace[("_" + s1 + "_", "_" + s2 + "_")] = 10
            
    # delete consonant
    for s in language.cons_list:
        cost_to_replace[(s, "")] = 2

    # replace consonant with consonant
    for s1 in language.cons_list:
        for s2 in language.cons_list:
            if s1 == s2:
                cost_to_replace[(s1, s1)] = 0
                break
            else:
                # ringing/thud, soft/hard
                diff = (
                    abs(language.cons_data[s1][1] - language.cons_data[s2][1]) + 
                    abs(language.cons_data[s1][2] - language.cons_data[s2][2]) * 2
                ) * 7

                # if have any common group
                if language.cons_data[s1][0] == language.cons_data[s2][0]:
                    diff /= 2
                else:
                    diff += 6

                if language.is_whistl(s1) and language.is_whistl(s2):
                    diff /= 3
                if language.is_hiss(s1) and language.is_hiss(s2):
                    diff /= 3
                
                cost_to_replace[(s1, s2)] = diff

    # replace vowel with consonant
    for v in language.vowel_list:
        for c in language.cons_list:
            if language.is_ring(c):
                cost_to_replace[(v, c)] = 15
                cost_to_replace[("_" + v + "_", c)] = 30
            else:
                cost_to_replace[(v, c)] = 20
                cost_to_replace[("_" + v + "_", c)] = 40

    if __name__ == "__main__":
        pprint(cost_to_replace)
        print(len(cost_to_replace))


def get_replace_cost(s1, s2):
    if cost_to_replace.get((s1, s2)) is not None:
        return cost_to_replace[(s1, s2)]
    if cost_to_replace.get((s2, s1)) is not None:
        return cost_to_replace[(s2, s1)]

    print("NO PAIR: ", (s1, s2))
    return 1000


def get_transcript_mapping(s, t, max_shift=2):
    n = len(s)
    m = len(t)
    
    dp = np.ones((n + 1, m + 1), dtype=np.int64) * 1000
    dp[0][0] = 0
    anc = np.zeros((n + 1, m + 1), dtype=np.int32)
    for i in range(1, n + 1):
        for j in range(max(1, i - max_shift), min(m + 1, i + max_shift + 1)):
            if i >= 1 and i >= j - max_shift and dp[i - 1][j] < dp[i][j]:
                dp[i][j] = dp[i - 1][j]
                anc[i][j] = 1
                
            if j >= 1 and j >= i - max_shift and dp[i][j - 1] < dp[i][j]:
                dp[i][j] = dp[i][j - 1]
                anc[i][j] = 2

            if i >= 1 and j >= 1 and dp[i - 1][j - 1] < dp[i][j]:
                dp[i][j] = dp[i - 1][j - 1]
                anc[i][j] = 3

            dp[i][j] += get_replace_cost(s[i - 1] if i >= 1 else "",
                                         t[j - 1] if j >= 1 else "")
            # dp[i][j] += cost_to_replace[(s[i - 1] if i >= 1 else "",
            #                              t[j - 1] if j >= 1 else "")]
    
    mapping = []

    i = n
    j = m
    while i >= 0 and j >= 0 and anc[i][j] != 0:
        mapping.append((i - 1, j - 1))
        if anc[i][j] == 1:
            i -= 1
        elif anc[i][j] == 2:
            j -= 1
        elif anc[i][j] == 3:
            i -= 1
            j -= 1
        # else:
        #     print("ERROR in anc: ")
        #     pprint(anc)
        #     pprint(dp)
        #     print(i, j)
        #     break
    if i == 1 and j == 1:
        mapping.append((i - 1, j - 1))
    
    if __name__ == "__main__":
        pprint(dp)
        print(f"final error: ", dp[n][m])
    
    return mapping, dp[n][m]


def get_rhyme_sounds_mapping(word1, accent1, word2, accent2, max_shift=5, use_prev_sound=True):
    tr1 = language.get_transcription(word1, accent1)
    tr2 = language.get_transcription(word2, accent2)
    cut_index1 = language.get_accent_in_transcription(tr1)
    cut_index2 = language.get_accent_in_transcription(tr2)
    if use_prev_sound:
        cut_index1 = max(0, cut_index1 - 1)
        cut_index2 = max(0, cut_index2 - 2)
    
    cut_tr1 = tr1[cut_index1:]
    cut_tr2 = tr2[cut_index2:]
    pairs, err = get_transcript_mapping(cut_tr1, cut_tr2, max_shift)
    return pairs, err


def get_rhyme_quality(word1, accent1, word2, accent2, max_shift=5, use_prev_sound=False):
    return get_rhyme_sounds_mapping(word1, accent1, word2, accent2,
                                    max_shift=max_shift, use_prev_sound=use_prev_sound)


run_first_iter_replace_cost()


if __name__ == "__main__":
    # input_word = input()
    # input_accent = int(input())

    # rhymes = (
    #     ryfmach.find_rhymes(input_word, input_accent, mistake=0, cnt_limit=10, filtered_posp=[1,0,0,0,0,0,0]) +
    #     ryfmach.find_rhymes(input_word, input_accent, mistake=1, cnt_limit=10, filtered_posp=[1,0,0,0,0,0,0]) +
    #     ryfmach.find_rhymes(input_word, input_accent, mistake=2, cnt_limit=10, filtered_posp=[1,0,0,0,0,0,0])
    # )
    # print(',  '.join([w["word"] for w in rhymes]))
    # rhymes = sorted(
    #     rhymes,
    #     key=lambda w: get_rhyme_quality(
    #         input_word,
    #         input_accent,
    #         w["word"],
    #         w["accent"],
    #     )
    # )
    # print(',  '.join([w["word"] for w in rhymes]))


    print()
    get_rhyme_quality(
        "прішлыя", 2,
        "прышлая", 2
    )

    print()
    get_rhyme_quality(
        "прішлыя", 2,
        "авантурыстычная", 10
    )
