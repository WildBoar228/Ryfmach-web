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

vowel_list = ["а","о","у","і","ы","э"]
cons_list = list(cons_data)

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


def get_accent_in_transcription(tr):
    for i in range(len(tr)):
        if (len(tr[i]) == 3 and tr[i][0] == '_' and
            tr[i][1] in vowel_list and tr[i][2] == '_'):
            return i
    return -1


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