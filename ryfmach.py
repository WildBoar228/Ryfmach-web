import sqlite3
import threading

alphabet = "-абвгдеёжзійклмнопрстуўфхцчш'ыьэюя"
vowels = "аоуыэяёюіе"
consonants = "бвгджзйклмнпрстўфхцчш"
softening_vowels = "яёюіе"

iotation = {"я": "а", "ё": "о", "ю": "у", "е": "э",}

# [x][..][..] - группа звуков
# [..][0][..] - звонкий
# [..][1][..] - глухой
# [..][..][0] - твёрдый
# [..][..][1] - мягкий
cons_sounds =      [[["б", "б'"],
                     ["п", "п'"]],

                    [["в", "в'"],
                     [None, None]],

                    [["г", "г'"],
                     ["х", "х'"]],

                    [["г*", "г*'"],
                     ["к", "к'"]],

                    [["д", "дз'"],
                     ["т", "ц'"]],

                    [["дз", "дз'"],
                     ["ц", "ц'"]],

                    [["ж", None],
                     ["ш", None]],

                    [["з", "з'"],
                     ["с", "с'"]],

                    [[None, "й"],
                     [None, None]],

                    [["л", "л'"],
                     [None, None]],

                    [["м", "м'"],
                     [None, None]],

                    [["н", "н'"],
                     [None, None]],

                    [["р", None],
                     [None, None]],

                    [[None, None],
                     ["ф", "ф'"]],

                    [["дж", None],
                     ["ч", None]],

                    [["ў", None],
                     [None, None]],]


group_base_sound = ["б", "в", "г", "к", "д", "ц", "ж", "з", "й", "л", "м", "н", "р", "ф", "ч", "ў"]


cons_data =  {'б': (0, 0, 0), "б'": (0, 0, 1),
               'п': (0, 1, 0), "п'": (0, 1, 1),

               'в': (1, 0, 0), "в'": (1, 0, 1),
               
               'г': (2, 0, 0), "г'": (2, 0, 1),
               'х': (2, 1, 0), "х'": (2, 1, 1),

               'г*': (3, 0, 0), "г*'": (3, 0, 1),
               'к': (3, 1, 0), "к'": (3, 1, 1),

               'д': (4, 0, 0), "дз'": (4, 0, 1),
               'т': (4, 1, 0), "ц'": (4, 1, 1),

               'дз': (5, 0, 0),
               'ц': (5, 1, 0),

               'ж': (6, 0, 0),
               'ш': (6, 1, 0),

               'з': (7, 0, 0), "з'": (7, 0, 1),
               'с': (7, 1, 0), "с'": (7, 1, 1),

               'й': (8, 0, 1),

               'л': (9, 0, 0), "л'": (9, 0, 1),

               'м': (10, 0, 0), "м'": (10, 0, 1),

               'н': (11, 0, 0), "н'": (11, 0, 1),

               'р': (12, 0, 0),

               'ф': (13, 1, 0), "ф'": (13, 1, 1),

               'дж': (14, 0, 0),
               'ч': (14, 1, 0),

               'ў': (15, 0, 0)}


sonor = [1, 8, 9, 10, 11, 12, 15]


def is_consonant_sound(sound):
    return cons_data.get(sound) is not None


def is_ring(sound):
    return is_consonant_sound(sound) and cons_data[sound][1] == 0

def is_thud(sound):
    return is_consonant_sound(sound) and cons_data[sound][1] == 1

def is_hard(sound):
    return is_consonant_sound(sound) and cons_data[sound][2] == 0

def is_soft(sound):
    return is_consonant_sound(sound) and cons_data[sound][2] == 1

def is_sonor(sound):
    return is_consonant_sound(sound) and cons_data[sound][0] in sonor

def is_whistl(sound):
    return sound in ["з", "з'", "с", "с'", "дз", "дз'", "ц", "ц'"]

def is_hiss(sound):
    return sound in ["ж", "ш", "дж", "ч"]


def ring_pair(sound):
    if is_consonant_sound(sound):
        gr, th, sf = cons_data[sound]
        return cons_sounds[gr][0][sf]

def thud_pair(sound):
    if is_consonant_sound(sound):
        gr, th, sf = cons_data[sound]
        return cons_sounds[gr][1][sf]

def hard_pair(sound):
    if is_consonant_sound(sound):
        gr, th, sf = cons_data[sound]
        return cons_sounds[gr][th][0]

def soft_pair(sound):
    if is_consonant_sound(sound):
        gr, th, sf = cons_data[sound]
        return cons_sounds[gr][th][1]

def whistl_pair(sound):
    if is_hiss(sound):
        if sound == "ж":
            return "з"
        if sound == "ш":
            return "с"
        if sound == "дж":
            return "дз"
        if sound == "ч":
            return "ц"

def hiss_pair(sound):
    if is_whistl(sound):
        if sound == "з" or sound == "з'":
            return "ж"
        if sound == "с" or sound == "с'":
            return "ш"
        if sound == "дз" or sound == "дз'":
            return "дж"
        if sound == "ц" or sound == "ц'":
            return "ч"


def get_transcription(word, accent):
    t = []
    for i in range(len(word)):        
        if word[i] in "аоуыэі":
            if accent == i:
                t.append(f"_{word[i]}_")
            else:
                t.append(word[i])
            
        elif word[i] in vowels:
            # ётацыя
            if (i == 0 or
                word[i - 1] in vowels or
                word[i - 1] == "ў" or
                word[i - 1] == "ь" or
                word[i - 1] == "'" or
                word[i - 1] == "-"):
                    t.append("й")
            
            if accent == i:
                t.append(f"_{iotation[word[i]]}_")
            else:
                t.append(iotation[word[i]])

        elif word[i] in consonants:
            t.append(word[i])

            # змягчэнне зычных
            if (i + 1 < len(word) and
                (word[i + 1] in softening_vowels or word[i + 1] == 'ь') and
                soft_pair(t[-1])):
                    t[-1] = soft_pair(t[-1])

    # афрыкаты
    i = 0
    while i < len(t) - 1:
        if t[i] == "д" and t[i + 1] in ["ж", "з", "з'"]:
            t[i] += t[i + 1]
            t.pop(i + 1)
        i += 1

    changed = True
    while (changed):
        changed = False

        for i in range(len(t)):
            # асіміляцыя па глухасці + аглушэнне на канцы
            if (is_ring(t[i]) and thud_pair(t[i]) and
                (i + 1 >= len(t) or is_thud(t[i + 1]))):
                    t[i] = thud_pair(t[i])
                    changed = True
            # асіміляцыя па звонкасці
            elif (is_thud(t[i]) and ring_pair(t[i]) and
                (i + 1 < len(t) and is_ring(t[i + 1]) and not is_sonor(t[i + 1]))):
                    t[i] = ring_pair(t[i])
                    changed = True

            # асіміляцыя па мяккасці
            if (i + 1 < len(t) and
                (t[i] in ["з", "с"] and is_soft(t[i + 1]) and t[i + 1] not in ["г'", "к'", "х'"] or 
                 t[i] in ["д", "т", "дз", "ц"] and t[i + 1] == "в'")):
                    t[i] = soft_pair(t[i])
                    changed = True

            # прыпадабненне шыпячага да свісцячага
            if (i + 1 < len(t) and
                is_hiss(t[i]) and is_whistl(t[i + 1])):
                    t[i] = whistl_pair(t[i])
                    changed = True
            # прыпадабненне свісцячага да шыпячага
            elif (i + 1 < len(t) and
                is_whistl(t[i]) and is_hiss(t[i + 1])):
                    t[i] = hiss_pair(t[i])
                    changed = True

            # асіміляцыя зубных гукаў
            if (i + 1 < len(t) and
                t[i] in ["д", "т"] and t[i + 1] in ["ц", "ч"]):
                    t[i] = t[i + 1]
                    changed = True

    return t


similar = {'э': 'е',
           'я': 'а',
           'ё': 'о',
           'ю': 'у'}

def is_belarusian(word: str):
    for char in word:
        if char not in alphabet:
            return False
    return True

def is_vowel(letter: str):
    return letter in vowels

def add_accent(word: str, accent: int):
    return word[:accent] + '<span class="accent-vowel">' + word[accent] + '</span>' + word[accent + 1:]


def alphabet_sort_key(w):
    global alphabet
    try:
        return [alphabet.index(c) if c in alphabet else -1 for c in w]
    except Exception as exc:
        print(w, exc)


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
                debug_output=True):
    
    # print(get_transcription(input_word, accent))
    working_part0 = get_working_part(input_word, accent, 0)
    working_part1 = get_working_part(input_word, accent, 1)
    working_part2 = get_working_part(input_word, accent, 2)
    # print(f'{working_part0} \t {working_part1} \t {working_part2}')
    try:
        db_lock.acquire(True)

        if mistake == -1 or mistake == 0:
            words = cur.execute('''SELECT * FROM words
                                    WHERE working_part0 == ? AND word != ?
                                    ORDER BY word, initial_id, accent_index;''',
                                        (working_part0, input_word)).fetchall()
            
        elif mistake == 1:
            words = cur.execute('''SELECT * FROM words
                                    WHERE working_part0 != ? AND working_part1 == ? AND word != ?
                                    ORDER BY word, initial_id, accent_index;''',
                                        (working_part0, working_part1, input_word)).fetchall()
            
        elif mistake == 2:
            words = cur.execute('''SELECT * FROM words
                                    WHERE working_part0 != ? AND working_part1 != ? AND working_part2 == ? AND word != ?
                                    ORDER BY word, initial_id, accent_index;''',
                                        (working_part0, working_part1, working_part2, input_word)).fetchall()

    except Exception as exc:
        print(exc)
    finally:
        db_lock.release()

    words = sorted(words, key=lambda w: (alphabet_sort_key(w[1])))

    rhymes = []
    for i in range(len(words)):
        if ((i == 0 or not (words[i][1] == words[i - 1][1] and
                            words[i][2] == words[i - 1][2] and
                            words[i][4] == words[i - 1][4])) and
            filtered_posp[words[i][3] - 1] and (words[i][0] == words[i][2] or not only_initial)):
                word_dict = get_word_dict(words[i])
                if word_dict.get("initial_word") != input_word:
                    rhymes.append(word_dict)
    
    if len(rhymes) > 1000:
        rhymes = rhymes[:1000]
        # only_initial = list(filter(lambda w: w["is_initial"] == True, rhymes))
        # if len(only_initial) > 1000:
        #     rhymes = only_initial[:1000]
        # else:
        #     rhymes = only_initial + rhymes[:1000 - len(only_initial)]
        #     rhymes = sorted(rhymes, key=lambda w: (alphabet_sort_key(w[1])))
    
    if mistake == -1 and len(rhymes) < 10:
        print(f'{len(rhymes)}', end='  ')

        for mst in (1, 2):
            if len(rhymes) < 10:
                rhymes1 = find_rhymes(input_word, accent, filtered_posp, only_initial, mst)
                if len(words) + len(rhymes1) > 500:
                    rhymes1 = rhymes1[len(rhymes) - 500:]
                
                rhymes += rhymes1
                print(f'+{len(rhymes1)}', end='  ')

        rhymes = sorted(rhymes, key=lambda w: (alphabet_sort_key(w["word"])))
        
        print('  rhymes found')
    
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
