import requests
from bs4 import BeautifulSoup
import async_requests, asyncio

import ryfmach
import language
import sounds

async_requests.REQUEST_INTERVAL = 1 / 100


def process_verse_page(page_text):
    # with open("buf.txt", "w", encoding="utf-8") as file:
    #     file.write(page_text)

    verse_text = page_text[page_text.find('BOOK_BEGIN'):page_text.find('BOOK_END')]
    # verse_text = language.clear_punctuation(verse_text)
    # print(verse_text)
    # print()
    soup = BeautifulSoup(verse_text, 'html.parser')
    rows = soup.find_all('p')

    # words = list(map(
    #     lambda r: language.clear_punctuation(
    #         r.get_text().split()
    #     ), rows))
    words = []

    for i, row in enumerate(rows):
        w = language.clear_punctuation(row.get_text()).split()
        if len(w) == 0:
            w = []
        else:
            w = w[-1]
            if w == '&nbsp;' or not language.is_belarusian(w):
                w = []
            else:
                w = ryfmach.get_word_data_from_db(w)
        words.append(w)
    
    # print("WORDS:")
    # for w in words:
    #     if w is None:
    #         print("-")
    #     else:
    #         for var in w:
    #             print(var["word"], end=' ')
    #         print()
    # print()

    # prev = -1
    for i in range(len(words)):
        if len(words[i]) == 0:
            print()
            # prev = i
            continue

        # if prev < i - 4:
        #     prev = i - 4

        best = ([], ryfmach.MAX_ACCEPTABLE_PENALTY, {"word": None}, {"word": None}, -1)
        for var in words[i]:
            for j in range(i + 1, min(i + 5, len(words))):
                for var2 in words[j]:
                    # print("COMP ", var["word"], var2["word"])
                    cur = sounds.get_rhyme_sounds_mapping(
                        var["word"],
                        var["accent"],
                        var2["word"],
                        var2["accent"]
                    )
                    if cur[1] < best[1]:
                        best = (cur[0], cur[1], var, var2, j)
                        
            # print("var:", var["word"], best[3]["word"], best[0], best[1])
        
        if best[1] < 20:
            print(best[2]["word"], best[3]["word"], best[0], best[1], best[4])
            with open("pairs.txt", "a", encoding="utf-8") as file:
                file.write('\n' + str(best))
            words[best[4]] = []
        
        words[i] = []


def search_authors_verses(page_text, domain, verse_page_list):
    if len(verse_page_list) > 10:
        return
    
    soup = BeautifulSoup(page_text, 'html.parser')

    verse_titles = ['вершы']

    title_divs = soup.find_all('div', class_='titler-section')

    for title in title_divs:
        for verse_title in verse_titles:
            if verse_title in title.getText().lower():
                links_list = title.find_next_sibling()

                if links_list is not None:
                    verse_links = links_list.find_all('a')

                    for link in verse_links:
                        href_attr = link.get('href', default='')
                        try:
                            assert href_attr.endswith('.html')
                            assert not href_attr.endswith('.html')
                            assert not 'audio' in href_attr.lower()
                            print(f"Add {domain + href_attr}")
                            verse_page_list.append(domain + href_attr)

                        except AssertionError:
                            print(href_attr, 'fails')
                            pass
                break


def enumerate_authors(domain, main_url, author_page_list):
    print('ping ', main_url)
    response = requests.request('GET', main_url)
    print(response)
    page_text = response.content.decode('utf-8')
    soup = BeautifulSoup(page_text, 'html.parser')

    container_divs = soup.find_all('div', class_='container')
    links_container = None
    for cont in container_divs:
        if len(cont['class']) == 1:
            links_container = cont

    if links_container is None:
        raise ValueError('links container not found')
    
    links = links_container.find_all('a')

    for local_link in links:
        if local_link.get('href'):
            author_page_list.append(domain + local_link.get('href'))


def main():
    author_pages = []
    verse_pages = []
    enumerate_authors('https://knihi.com', 'https://knihi.com/autary.html', author_pages)
    author_pages = list(map(lambda url: (
        url,
        search_authors_verses,
        ('https://knihi.com', verse_pages), {}
    ), author_pages))[:10]

    print(f"author pages: {author_pages}")
    asyncio.run(async_requests.parse_pages_batch(author_pages))
    
    verse_pages = list(map(lambda url: (
        url,
        process_verse_page,
        (), {}
    ), verse_pages))[:10]

    print(f"verse pages: {verse_pages}")
    asyncio.run(async_requests.parse_pages_batch(verse_pages))


if __name__ == '__main__':
    main()
    # with open("buf.txt", encoding="utf-8") as file:
    #     text = file.read()
    #     process_verse_page(text)