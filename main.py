from flask import Flask, render_template, redirect, request, make_response, session, jsonify, send_from_directory
import json
import ryfmach, ryfmach_phonetics
from pprint import pprint
import logging
import os
import time

app = Flask(__name__, template_folder='static/templates')
app.config['SECRET_KEY'] = 'garikgoyda_secret_key'
app.logger.setLevel(logging.INFO)


@app.route('/')
def rhyme_page():
    input_word_info = session.get('rhyme_input_word_info', {'word': ''})
    session['rhyme_input_word_info'] = input_word_info
    return render_template(
        'rhyme_page.html',
        title="Рыфмач&nbsp;&ndash; падабраць рыфму",
        page_description="Рыфмач. Рыфмы на беларускай мове, пошук рыфм для вершаў. Рифмы на белорусском языке, поиск рифм для стихотворений.",
        input_word=input_word_info["word"],
        add_search_filter_button=True,
        canonical_url="https://ryfmach.online"
    )


@app.route('/', methods=['POST'])
def update_rhymes():
    input_word_info = request.json
    if input_word_info.get('word') is None:
        session['rhyme_input_word_info'] = {'word': ''}
        return jsonify(rhymes_list=[], word_found=False)

    start_time = time.time()
    app.logger.info("%s Request rhyme: %s", str(request.remote_addr), str(input_word_info))
    rhymes = ryfmach.rhymes_text_list(input_word_info)
    word_found = True
    if rhymes is None:
        rhymes = []
        word_found = False

    print(f"{str(request.remote_addr)} Response time: {int((time.time() - start_time) * 1000)} ms")

    session['rhyme_input_word_info'] = input_word_info
    return jsonify(rhymes_list=rhymes, word_found=word_found)


@app.route('/phonetics')
def phonetics_page():
    input_word_info = {'word': ''} # session.get('phon_input_word_info', {'word': ''})
    # session['phon_input_word_info'] = input_word_info
    return render_template(
        'phonetics_page.html',
        title="Рыфмач&nbsp;&ndash; фанетычны разбор",
        page_description="Рыфмач. Фанетычны разбор і транскрыпцыі на беларускай мове. Фонетический разбор и транскрипции на белорусском языке.",
        input_word=input_word_info["word"],
        add_search_filter_button=False,
        canonical_url="https://ryfmach.online/phonetics"
    )


@app.route('/phonetics', methods=['POST'])
def phonetic_analysis():
    input_word_info = request.json
    if input_word_info.get('word') is None:
        # session['phon_input_word_info'] = {'word': ''}
        return jsonify(phon_analys=[], word_found=False)

    start_time = time.time()
    app.logger.info("%s Request phonetics: %s", str(request.remote_addr), str(input_word_info))

    analysed = ryfmach_phonetics.input_phonetic_analysis(input_word_info)
    word_found = len(analysed) > 0

    print(f"{str(request.remote_addr)} Response time: {int((time.time() - start_time) * 1000)} ms")

    # session['phon_input_word_info'] = input_word_info
    return jsonify(word_variants=analysed, word_found=word_found)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/x-icon')


@app.route('/sitemap')
def sitemap():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'sitemap.xml', mimetype='application/xml')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')