from ryfmach import *


con = sqlite3.connect('db/Slounik2.db', check_same_thread=False)
cur = con.cursor()


all_words = cur.execute( '''SELECT * FROM words''').fetchall()

for i in range(len(all_words)):
    all_words[i] = list(all_words[i])
    all_words[i][5] = get_working_part(all_words[i][1], all_words[i][4], 0)
    all_words[i][6] = get_working_part(all_words[i][1], all_words[i][4], 1)
    all_words[i][7] = get_working_part(all_words[i][1], all_words[i][4], 2)
    #print(all_words[i][5])

    cur.execute('''UPDATE words
                    SET working_part0 = ?, working_part1 = ?, working_part2 = ?
                    WHERE id = ?;''',
                (all_words[i][5], all_words[i][6], all_words[i][7], all_words[i][0]))

    if i % 10000 == 0 or i == len(all_words) - 1:
        print(i)
        print(all_words[i][5], all_words[i][6], all_words[i][7])
        con.commit()


#cur.execute('''INSERT INTO words(word, initial_id, part_of_speech,
#                               accent_index, working_part)
#                               VALUES(?, ?, ?, ?, ?)''',
#            (tests[0][0], ))



#tests = [('нага', 3)]
#import random
#for i in range(30):
#    resp = cur.execute(
#                '''SELECT word, accent_index FROM words WHERE id == ?''',
#                (random.randint(1, 1000000),)
#            ).fetchone()
#    if resp:
#        tests.append(resp)

#for i, test in enumerate(tests):
#    print(f'{i}  {test[0]}:    {' '.join(get_transcription(*test))}')
#    for j in range(3):
#        print(f'{get_working_part(*test, mistake=j)}')
#    print()

