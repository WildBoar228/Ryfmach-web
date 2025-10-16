import sqlite3
import threading
from language import *

MAX_RHYMES_IN_RESP = 300


def get_word_dict(w):
    try:
        db_lock.acquire(True)
        word_data = {}
        word_data["word"] = w[1]
        word_data["accent"] = w[4]
        posp = cur.execute('''SELECT name FROM parts_of_speech
                            WHERE id == ?''',
                            (w[3], )).fetchone()[0]
        word_data["part_of_speech"] = posp
        if w[2] == w[0]:
            word_data["is_initial"] = True
        else:
            word_data["is_initial"] = False
            try:
                word_data["initial_word"], word_data["initial_accent"] = cur.execute(
                    '''SELECT word, accent_index FROM words WHERE id == ?''',
                    (w[2],)
                ).fetchone()
            except TypeError:
                word_data["is_initial"] = None

    except Exception as exc:
        print(exc)

    finally:
        db_lock.release()
    
    return word_data


def get_word_data(input_word: str):
    try:
        db_lock.acquire(True)
        words = cur.execute('''SELECT * FROM words WHERE word == ?
                                ORDER BY word, initial_id, accent_index;''',
                        (input_word,)).fetchall()
    except Exception as exc:
        print(exc)
    finally:
        db_lock.release()
    
    words = sorted(words, key=lambda w: (alphabet_sort_key(w[1])))
    
    word_variants = []
        
    for i in range(len(words)):
        if i == 0 or not (words[i][1] == words[i - 1][1] and
                          words[i][2] == words[i - 1][2] and
                          words[i][4] == words[i - 1][4]):
            word_variants.append(get_word_dict(words[i]))

    return word_variants


def get_working_part(word: str, accent: int, mistake: int = 0):
    t = get_transcription(word, accent)

    acc_sound = 0

    # ідэяльная рыфма
    i = 0
    while i < len(t):
        if i > 0 and not is_vowel(t[i]) and (t[i] == t[i - 1] or t[i] in ["дз", "дз'", "дж"] and t[i - 1] in ["д"]):
            t.pop(i - 1)
            continue

        if t[i] == "_ы_":
            t[i] = "_і_"
        
        if "_" in t[i]:
            acc_sound = i
        i += 1

    if acc_sound == len(t) - 1 and len(t) > 1 and mistake < 2:
        t = t[acc_sound - 1:]
    else:
        t = t[acc_sound:]
    
    # добрая рыфма
    if mistake >= 1:
        i = 0
        while i < len(t):
            if i > 0 and is_soft(t[i - 1]):
                if t[i] == "э":
                    t[i] = "і"
                elif t[i] == "а":
                    t[i] = "і"
                elif t[i] == "у":
                    t[i] = "і"
            elif t[i] == "э":
                t[i] = "ы"
            elif t[i] == "а":
                t[i] = "ы"
            elif t[i] == "у":
                t[i] = "ы"

            if i > 0 and i < len(t) - 1 and is_consonant_sound(t[i]):
                if is_ring(t[i]) and thud_pair(t[i]):
                    t[i] = thud_pair(t[i])
            
            if is_consonant_sound(t[i]) and (i == len(t) - 1 or not is_vowel(t[i + 1])):
                if is_soft(t[i]) and hard_pair(t[i]):
                    t[i] = hard_pair(t[i])
            
            i += 1
    
    # слабая рыфма
    if mistake >= 2:
        i = 0
        while i < len(t):
            if t[i] in ["й", "ў"]:
                t.pop(i)
                continue

            if i < len(t) - 1:
                if is_sonor(t[i]):
                    t[i] = "л"
                elif is_hiss(t[i]):
                    t[i] = "ш"
                elif is_whistl(t[i]):
                    t[i] = "с"
            
            i += 1
    
        i = 0
        while i < len(t):
            if i > 0 and (t[i] == t[i - 1] or t[i] in ["дз", "дз'", "дж"] and t[i - 1] in ["д"]):
                t.pop(i - 1)
                continue
            i += 1
    
    return "".join(t)


def find_rhymes(input_word: str,
                accent: int,
                filtered_posp: list[bool] = [True, True, True, True, True, True, True,],
                only_initial: bool = False,
                mistake: int = 0,
                debug_output=True,
                cnt_limit=MAX_RHYMES_IN_RESP):
    
    # print(get_transcription(input_word, accent))
    working_part0 = get_working_part(input_word, accent, 0)
    working_part1 = get_working_part(input_word, accent, 1)
    working_part2 = get_working_part(input_word, accent, 2)
    # print(f'{working_part0} \t {working_part1} \t {working_part2}')
    try:
        db_lock.acquire(True)

        enabled_posp_cnt = sum(filtered_posp)
        posp_filter = " AND ("
        if (enabled_posp_cnt > len(filtered_posp) / 2):
            for i in range(len(filtered_posp)):
                if not filtered_posp[i]:
                    if (posp_filter[-1] != '('):
                        posp_filter += " AND "
                    posp_filter += f"part_of_speech != {i + 1}"
        else:
            for i in range(len(filtered_posp)):
                if filtered_posp[i]:
                    if (posp_filter[-1] != '('):
                        posp_filter += " OR "
                    posp_filter += f"part_of_speech == {i + 1}"
        posp_filter += ")"
        if not any(filtered_posp) or all(filtered_posp):
            posp_filter = ""

        # print(f'posp_filter = "{posp_filter}"')

        if mistake == -1 or mistake == 0:
            words = cur.execute(f'''SELECT * FROM words
                                    WHERE working_part0 == ? AND word != ?{posp_filter}
                                    ORDER BY word, initial_id, accent_index
                                    LIMIT ?;''',
                                        (working_part0, input_word,
                                         min(cnt_limit * 2, MAX_RHYMES_IN_RESP))).fetchall()
            
        elif mistake == 1:
            words = cur.execute(f'''SELECT * FROM words
                                    WHERE working_part0 != ? AND working_part1 == ? AND word != ?{posp_filter}
                                    ORDER BY word, initial_id, accent_index
                                    LIMIT ?;''',
                                        (working_part0, working_part1,
                                         input_word,
                                         min(cnt_limit * 2, MAX_RHYMES_IN_RESP))).fetchall()
            
        elif mistake == 2:
            words = cur.execute(f'''SELECT * FROM words
                                    WHERE working_part0 != ? AND working_part1 != ? AND working_part2 == ? AND word != ?{posp_filter}
                                    ORDER BY word, initial_id, accent_index
                                    LIMIT ?;''',
                                        (working_part0, working_part1,
                                         working_part2, input_word,
                                         min(cnt_limit * 2, MAX_RHYMES_IN_RESP))).fetchall()

    except Exception as exc:
        print(exc)
    finally:
        db_lock.release()

    words = sorted(words, key=lambda w: (alphabet_sort_key(w[1])))
    # print(f'{len(words)} words (at first), last: {words[-1] if len(words) > 0 else '-'}')

    rhymes = []
    for i in range(len(words)):
        if ((i == 0 or not (words[i][1] == words[i - 1][1] and
                            words[i][2] == words[i - 1][2] and
                            words[i][4] == words[i - 1][4])) and
            filtered_posp[words[i][3] - 1] and (words[i][0] == words[i][2] or not only_initial)):
                word_dict = get_word_dict(words[i])
                if word_dict.get("initial_word") != input_word:
                    rhymes.append(word_dict)
    
    if len(rhymes) > cnt_limit:
        rhymes = rhymes[:cnt_limit]
        # only_initial = list(filter(lambda w: w["is_initial"] == True, rhymes))
        # if len(only_initial) > MAX_RHYMES_IN_RESP:
        #     rhymes = only_initial[:MAX_RHYMES_IN_RESP]
        # else:
        #     rhymes = only_initial + rhymes[:MAX_RHYMES_IN_RESP - len(only_initial)]
        #     rhymes = sorted(rhymes, key=lambda w: (alphabet_sort_key(w[1])))
    
    output_str = f'{mistake}  {input_word} ({accent}):  '
    if mistake == -1:
        if len(rhymes) < 10:
            output_str += f'{len(rhymes)}  '

            for mst in (1, 2):
                if len(rhymes) < 10:
                    rhymes1 = find_rhymes(input_word, accent, filtered_posp,
                                        only_initial, mst, cnt_limit=50 - len(rhymes))
                    
                    rhymes += rhymes1

                    output_str += f'+{len(rhymes1)}  '

            rhymes = sorted(rhymes, key=lambda w: (alphabet_sort_key(w["word"])))
            output_str += '=  '

    output_str += f'{len(rhymes)} rhymes found'
    print(output_str)
    
    return rhymes


def rhymes_text_list(input_word_info):
    input_word_info["word"] = input_word_info["word"].replace("и", "і")
    input_word_info["word"] = input_word_info["word"].replace("щ", "ў")
    input_word_info["word"] = input_word_info["word"].replace("ъ", "'")

    if not is_belarusian(input_word_info["word"]) or len(input_word_info["word"]) > 40:
        return []
    if input_word_info.get("accent") is None:
        input_word_data = get_word_data(input_word_info["word"].lower())
    else:
        input_word_data = [input_word_info]
    
    filtered_posp = input_word_info.get("filtered_posp", [True] * 7)
    only_initial = input_word_info.get("only_initial", False)
    mistake = input_word_info.get("search_mistake", 0)

    rhymes = []
    for i in range(len(input_word_data)):
        rhymes.append({"word_variant": input_word_data[i],
                       "rhymes_data": find_rhymes(input_word_data[i]["word"],
                                                  input_word_data[i]["accent"],
                                                  filtered_posp=filtered_posp,
                                                  only_initial=only_initial,
                                                  mistake=mistake)})
    
    return rhymes


con = sqlite3.connect('db/Slounik2.db', check_same_thread=False)
cur = con.cursor()

db_lock = threading.Lock()


if __name__ == "__main__":
    tests = []

    # import random
    # for i in range(30):
    #     resp = cur.execute(
    #                 '''SELECT word, accent_index FROM words WHERE id == ?''',
    #                 (random.randint(1, 1000000),)
    #             ).fetchone()
    #     if resp:
    #         tests.append(resp)

    tests = [("хата", 1),
         ("неба", 1),
         ("дзень", 2),
         ("ксёндз", 2),
         ("шчаўе", 2),
         ("лодка", 1),
         ("кніжка", 2),
         ("касьба", 5),
         ("лічба", 1),
         ("малацьба", 7),
         ("цемя", 1),
         ("здзек", 3),
         ("збіраць", 4),
         ("дзверы", 3),
         ("чацвёрты", 4),
         ("скінуць", 2),
         ("дошцы", 1),
         ("смяешся", 3),
         ("зжаць", 2),
         ("сшытак", 2),
         ("расчасаць", 6),
         ("нарэшце", 3),
         ("нарэжце", 3),
         ("матчын", 1),
         ("кладцы", 2),
         ("разводдзе", 4),
         ("ерась", 0),
         ("верас", 1),]

    for i, test in enumerate(tests):
        print(f'{i}  {test[0]}:    {' '.join(get_transcription(*test))}')
        for j in range(3):
            print(f'{get_working_part(*test, mistake=j)}')
        print()

    con.close()
