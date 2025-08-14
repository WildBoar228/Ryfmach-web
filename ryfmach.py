import sqlite3
import threading

alphabet = "-абвгдеёжзійклмнопрстуўфхцчш'ыьэюя"
vowels = ['а', 'о', 'у', 'ы', 'э', 'е', 'ё', 'і', 'ю', 'я']

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
    working_part = word[accent:]
    if accent == len(word) - 1:
        working_part = word[accent - 1:]
    for sound in similar:
        if sound in working_part:
            working_part = working_part.replace(sound, similar[sound])
    return working_part


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


con = sqlite3.connect('db/Slounik.db', check_same_thread=False)
cur = con.cursor()

db_lock = threading.Lock()


if __name__ == "__main__":
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

    con.close()
