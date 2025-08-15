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
    for i in range(len(t) - 1):
        if t[i] == "д" and t[i + 1] in ["ж", "з", "з'"]:
            t[i] += t[i + 1]
            t.pop(i + 1)

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


similar = {#'р': 'н',
           #'л': 'н',
           #'м': 'н',
           'э': 'е',
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
    
    words = sorted(words, key=lambda w: alphabet_sort_key(w[1]))
    
    word_variants = []
    # for w in words:
    #     word_variants.append(get_word_dict(w))
        
    for i in range(len(words)):
        if i == 0 or not (words[i][1] == words[i - 1][1] and
                          words[i][2] == words[i - 1][2] and
                          words[i][4] == words[i - 1][4]):
            word_variants.append(get_word_dict(words[i]))

    return word_variants


def get_working_part(word: str, accent: int):
    t = get_transcription(word, accent)

    acc_sound = 0
    for i in range(len(t)):
        if "_" in t[i]:
            acc_sound = i
            #t[i] = t[i].replace("_", "")

    if acc_sound == len(t) - 1 and len(t) > 1:
        return "".join(t[acc_sound - 1:])
    
    return "".join(t[acc_sound:])


def find_rhymes(input_word: str, accent: int):
    working_part = get_working_part(input_word, accent)
    try:
        db_lock.acquire(True)
        words = cur.execute('''SELECT * FROM words
                                WHERE working_part == ? AND word != ?
                                ORDER BY word, initial_id, accent_index;''',
                                    (working_part, input_word)).fetchall()
    except Exception as exc:
        print(exc)
    finally:
        db_lock.release()

    words = sorted(words, key=lambda w: alphabet_sort_key(w[1]))

    #print(add_accent(input_word, accent), len(words), words)
    rhymes = []
    for i in range(len(words)):
        if i == 0 or not (words[i][1] == words[i - 1][1] and
                          words[i][2] == words[i - 1][2] and
                          words[i][4] == words[i - 1][4]):
            rhymes.append(get_word_dict(words[i]))
    
    if len(rhymes) > 1000:
        only_initial = list(filter(lambda w: w["is_initial"] == True, rhymes))
        if len(only_initial) > 1000:
            rhymes = only_initial[:1000]
        else:
            rhymes = only_initial + rhymes[:1000 - len(only_initial)]
            rhymes = sorted(rhymes, key=lambda w: alphabet_sort_key(w["word"]))
    
    return rhymes


def rhymes_text_list(input_word_info):
    if not is_belarusian(input_word_info["word"]):
        return []

    if input_word_info.get("accent") is None:
        input_word_data = get_word_data(input_word_info["word"].lower())
    else:
        input_word_data = [input_word_info]

    rhymes = []
    for i in range(len(input_word_data)):
        rhymes.append({"word_variant": input_word_data[i],
                       "rhymes_data": find_rhymes(input_word_data[i]["word"],
                                                  input_word_data[i]["accent"])})
    
    return rhymes


con = sqlite3.connect('db/Slounik2.db', check_same_thread=False)
cur = con.cursor()

db_lock = threading.Lock()


if __name__ == "__main__":
    tests = []

    import random
    for i in range(30):
        resp = cur.execute(
                    '''SELECT word, accent_index FROM words WHERE id == ?''',
                    (random.randint(1, 1000000),)
                ).fetchone()
        if resp:
            tests.append(resp)

    for i, test in enumerate(tests):
        print(f'{i}  {test[0]}:    {' '.join(get_transcription(*test))}')

    """
    while True: 
        input_word = input('Увядзіце слова: ')
        if input_word in ['exit', 'e', 'q', 'quit', 'выход', 'в']:
            break

        new_word = False
        word = cur.execute('''SELECT * FROM words WHERE word == ?''',
                        (input_word,)).fetchall()
        if len(word) == 0:
            new_word = True
            print('Гэтае слова для нас новае.')
            while True:
                try:
                    accent = int(input('Увядзіце нумар ударнай літары: ')) - 1
                    if accent >= len(input_word) or accent < 0:
                        print('Літары з такім нумарам тут няма')
                        continue
                    if not is_vowel(input_word[accent]):
                        print('Гэта на галосны гук')
                        continue
                    break
                
                except ValueError:
                    print('Гэта не лічба')
            
            working_part = input_word[accent:]
            if accent == len(input_word) - 1:
                working_part = input_word[accent - 1:]
            for sound in similar:
                if sound in working_part:
                    working_part = working_part.replace(sound, similar[sound])
            word = (0, input_word, 0, 0, accent, working_part)
            print(word)
        else:
            word = word[0]

        words = cur.execute('''SELECT * FROM words
                            WHERE working_part == ? AND word != ?''',
                            (word[5], word[1])).fetchall()
        words = sorted(words, key=lambda w: alphabet_sort_key(w[1]))
        for w in words:
            print(add_accent(w[1], w[4]))
            posp = cur.execute('''SELECT name FROM parts_of_speech
                                WHERE id == ?''',
                                (w[3], )).fetchone()[0]
            if w[2] == w[0]:
                initial = 'пач. форма'
            else:
                initial = f'ад ' + cur.execute('''SELECT word FROM words
                                    WHERE id == ?''',
                                    (w[2],)).fetchone()[0]
            print(f' ({posp}, {initial})')
            
        if len(words) == 0:
            print('На жаль, мы не ведаем падыходных рыфмаў')

        if new_word:
            answer = input('Захаваць гэтае слова? ')
            if answer.lower() in ['да', 'так', 'д', 'т', '+', 'ок',
                                'ok', 'y', 'yes', '1', 'true']:
                while True:
                    try:                    
                        print('Якая гэта часціна мовы?')
                        print('назоўнік    -   1')
                        print('дзеяслоў    -   2')
                        print('прыметнік   -   3')
                        print('займеннік   -   4')
                        print('лічэбнік    -   5')
                        print('прыслоўе    -   6')
                        print('інш.        -   7')
                        posp = int(input())
                        if posp < 1 or posp > 7:
                            print('Гэтай лічбы ў спісе не было.')
                            print('Нічога, у наступны раз атрымаецца (мабыць)')
                            continue
                        break
                    except ValueError:
                        print('Гэта не лічба')

                ans = input('Гэта пачатковая форма слова? ')
                is_initial = (ans.lower() in ['да', 'так', 'д', 'т', '+', 'ок',
                                            'ok', 'y', 'yes', '1', 'true'])
                if not is_initial:
                    initial = input('Якая ў яго пачатковая форма? ')
                    initial_id = cur.execute('''
                                SELECT * FROM words WHERE word == ?''',
                                (initial,)).fetchone()
                    if initial_id is not None:
                        initial_id = initial_id[0]
                else:
                    print('Будзем лічыць, што так')
                    initial_id = cur.execute('''
                                SELECT MAX(id) from words''').fetchone()[0]
                    if initial_id is None:
                        initial_id = 1
                    else:
                        initial_id += 1
                    initial = word[1]
                    accent = word[4]
                
                working_part = initial[accent:]
                if accent == len(initial) - 1:
                    working_part = initial[accent - 1:]

                if is_initial:
                    cur.execute('''INSERT INTO words(word, initial_id, part_of_speech,
                                accent_index, working_part)
                                VALUES(?, ?, ?, ?, ?)''',
                                (word[1], initial_id, posp, word[4], word[5]))
                else:
                    if initial_id is None:
                        print('Яшчэ штосьці новае...')
                        while True:
                            try:
                                accent = int(input('Куды падае націск у пач. форме? ')) - 1
                                if accent >= len(initial) or accent < 0:
                                    print('Літары з такім нумарам тут няма')
                                    continue
                                if not is_vowel(initial[accent]):
                                    print('Гэта на галосны гук')
                                    continue
                                break
                            except ValueError:
                                print('Гэта не лічба')
                            
                        initial_id = cur.execute('''
                                    SELECT MAX(id) from words''').fetchone()[0]
                        if initial_id is None:
                            initial_id = 1
                        else:
                            initial_id += 1
                            
                        working_part = initial[accent:]
                        if accent == len(input_word) - 1:
                            working_part = initial[accent - 1:]
                        for sound in similar:
                            if sound in working_part:
                                working_part = working_part.replace(sound, similar[sound])

                        print((initial_id, initial, initial_id, posp, accent,
                                working_part))
                        cur.execute('''INSERT INTO words(word, initial_id,
                        part_of_speech, accent_index, working_part)
                        VALUES(?, ?, ?, ?, ?)''',
                                (initial, initial_id, posp, accent,
                                working_part))
                    
                    cur.execute('''INSERT INTO words(word, initial_id, part_of_speech,
                        accent_index, working_part)
                        VALUES(?, ?, ?, ?, ?)''',
                                (word[1], initial_id, posp, word[4], word[5]))
                con.commit()
                print('Слова захавана')
            else:
                print('Слова не захавана')
        print()
    """

    con.close()
