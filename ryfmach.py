import sqlite3
import threading
from language import *
import sounds
import hashlib
from pprint import pprint


MAX_RHYMES_IN_RESP = 500
MAX_RHYME_MISTAKE = 3


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
    
    words = sorted(words, key=record_sort_key(alphabet_sort_words_key))
    
    word_variants = []
    
    for i in range(len(words)):
        if i == 0 or not (words[i][1] == words[i - 1][1] and
                          words[i][2] == words[i - 1][2] and
                          words[i][4] == words[i - 1][4]):
            word_variants.append(get_word_dict(words[i]))

    return word_variants


def get_working_part(word: str, accent: int, mistake: int = 0):
    if mistake < 0:
        mistake = 0
    t = get_transcription(word, accent)

    acc_sound = 0

    # ідэяльная рыфма
    i = 0
    while i < len(t):
        if i > 0 and not is_vowel_sound(t[i]) and (t[i] == t[i - 1] or t[i] in ["дз", "дз'", "дж"] and t[i - 1] in ["д"]):
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
            if is_vowel_sound(t[i]):
                if non_accent_pair(t[i]) is None:
                    t[i] = "ы"

            if is_consonant_sound(t[i]):
                if i > 0 and i < len(t) - 1:
                    if is_ring(t[i]) and thud_pair(t[i]):
                        t[i] = thud_pair(t[i])
                
                if (i == len(t) - 1 or not is_vowel_sound(t[i + 1])):
                    if is_soft(t[i]) and hard_pair(t[i]):
                        t[i] = hard_pair(t[i])
            
            i += 1
    
    # сярэдняя рыфма
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
    
    # слабая рыфма
    if mistake >= 3:
        i = 0
        while i < len(t):
            if is_consonant_sound(t[i]):
                if i == len(t) - 1 or is_vowel_sound(t[i + 1]):
                    if is_sonor(t[i]):
                        t[i] = "л"
                    elif is_hiss(t[i]):
                        t[i] = "ш"
                    elif is_whistl(t[i]):
                        if i == len(t) - 1:
                            t[i] = "с"
                        else:
                            t[i] = "ш"
                    elif is_ring(t[i]):
                        t[i] = "в"
                    elif is_thud(t[i]):
                        t[i] = "ф"
                else:
                    t.pop(i)
                    i -= 1

            i += 1
    
        i = 0
        while i < len(t):
            if i > 0 and t[i] == t[i - 1]:
                t.pop(i - 1)
                continue
            i += 1
    
    return "".join(t)


def get_sound_hash(word: str, accent: int, mistake: int = 0):
    sound_str = get_working_part(word, accent, mistake)
    return int(hashlib.sha1(sound_str.encode('utf-8')).hexdigest(), 16) % 12345678901234277


def alphabet_sort_words_key(w, accent=None):
    global alphabet
    try:
        return [alphabet.index(c) if c in alphabet else -1 for c in w]
    except Exception as exc:
        print(w, exc)


def quality_sort_words_key(compare_with):
    def quality_with_comparation(w, accent):
        global alphabet
        try:
            return (
                sounds.get_rhyme_quality(
                    w, accent,
                    compare_with["word"], compare_with["accent"],
                    use_prev_sound=False
                ),
                alphabet_sort_words_key(w, accent),
            )
        except Exception as exc:
            print(compare_with, w, exc)
    return quality_with_comparation


def record_sort_key(word_key):
    def record_key(w_record):
        return (
            word_key(w_record[1], w_record[4]),
            w_record[0] != w_record[2],
        )
    return record_key


def json_sort_key(word_key):
    def json_key(w_record):
        return (
            word_key(w_record["word"], w_record["accent"]),
            w_record["word"] != w_record.get("initial_word"),
        )
    return json_key


def find_rhymes(input_word: str,
                accent: int,
                filtered_posp: list[bool] = [True, True, True, True, True, True, True,],
                only_initial: bool = False,
                mistake: int = 0,
                debug_output=True,
                cnt_limit=MAX_RHYMES_IN_RESP,
                words_sort_key=alphabet_sort_words_key):
    
    working_parts = [get_working_part(input_word, accent, i)
                     for i in range(0, max(0, mistake) + 1)]
    # print(working_parts)
    
    sound_hashes = [get_sound_hash(input_word, accent, i)
                    for i in range(0, max(0, mistake) + 1)]

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

        is_initial_filter = " AND id == initial_id" if only_initial else ""

        sound_hash_filter = ""
        for i in range(mistake):
            sound_hash_filter += f"sound_hash{i} != ? AND "
        sound_hash_filter += f"sound_hash{max(0, mistake)} == ?"
        
        words = cur.execute(f'''SELECT * FROM words
                                WHERE {sound_hash_filter} AND word != ?
                                {posp_filter}
                                {is_initial_filter}
                                ORDER BY word, initial_id, accent_index
                                LIMIT ?;''',
                                (*sound_hashes, input_word, MAX_RHYMES_IN_RESP)
        ).fetchall()

    except Exception as exc:
        print("ERROR query: ", exc)
    finally:
        db_lock.release()

    words = list(filter(lambda r:
                        get_working_part(r[1], r[4], mistake) ==
                            working_parts[-1],
                        words))

    words = sorted(words, key=record_sort_key(words_sort_key))
    # print(f'{len(words)} words (at first), last: {words[-1] if len(words) > 0 else '-'}')

    # with open("output.txt", "w", encoding="utf-8") as file:
    #     file.write(str(words))

    rhymes = []
    for i in range(len(words)):
        word_dict = get_word_dict(words[i])
        if word_dict.get("initial_word") != input_word:
            rhymes.append(word_dict)
    
    if len(rhymes) > cnt_limit:
        rhymes = rhymes[:cnt_limit]
    
    used_initial = set()
    k = 0
    for i in range(len(rhymes)):
        if rhymes[i].get("initial_word"):
            used_key = (rhymes[i]["initial_word"], rhymes[i]["initial_accent"])
        else:
            used_key = (rhymes[i]["word"], rhymes[i]["accent"])
            
        if used_key not in used_initial:
            used_initial.add(used_key)
            rhymes[k] = rhymes[i]
            k += 1
    rhymes = rhymes[:k]
    
    output_str = f'{mistake}  {input_word} ({accent}):  '
    if mistake == -1:
        if len(rhymes) < 10:
            output_str += f'{len(rhymes)}  '

            for mst in range(1, MAX_RHYME_MISTAKE + 1):
                if len(rhymes) < 10:
                    old_size = len(rhymes)
                    rhymes1 = find_rhymes(input_word, accent, filtered_posp,
                                          only_initial, mst, cnt_limit=cnt_limit // 2,
                                          words_sort_key=words_sort_key)
                    
                    rhymes += rhymes1
    
                    k = old_size
                    for i in range(k, len(rhymes)):
                        if rhymes[i]["is_initial"]:
                            used_key = (rhymes[i]["word"], rhymes[i]["accent"])
                        else:
                            used_key = (rhymes[i]["initial_word"], rhymes[i]["initial_accent"])
                            
                        if used_key not in used_initial:
                            used_initial.add(used_key)
                            rhymes[k] = rhymes[i]
                            k += 1
                    rhymes = rhymes[:k]

                    output_str += f'+{len(rhymes1)}  '

            output_str += '=  '
            
            rhymes = sorted(rhymes, key=json_sort_key(words_sort_key))
    
    if len(rhymes) > cnt_limit:
        rhymes = rhymes[:cnt_limit]

    output_str += f'{len(rhymes)} rhymes found'
    if debug_output:
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
        if input_word_info["sort_mode"] == "alphabet":
            sort_func = alphabet_sort_words_key
        elif input_word_info["sort_mode"] == "quality":
            sort_func = quality_sort_words_key(input_word_data[i])

        rhymes.append({"word_variant": input_word_data[i],
                       "rhymes_data": find_rhymes(input_word_data[i]["word"],
                                                  input_word_data[i]["accent"],
                                                  filtered_posp=filtered_posp,
                                                  only_initial=only_initial,
                                                  mistake=mistake,
                                                  words_sort_key=sort_func)})
    
    return rhymes


con = sqlite3.connect('db/Slounik3.db', check_same_thread=False)
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
         ("верас", 1),
         ("роспач", 1),
         ("пробашч", 2),
         ("бусел", 1),
         ("вузел", 1),]

    for i, test in enumerate(tests):
        print(f'{i}  {test[0]}:    {' '.join(get_transcription(*test))}')
        for j in range(4):
            print(f'{get_working_part(*test, mistake=j)} {get_sound_hash(*test, mistake=j)}')
        print()

    con.close()
