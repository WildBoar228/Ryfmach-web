from flask import Flask, render_template, redirect, request, make_response, session, jsonify, send_from_directory
import json
import bel_lang_engine.ryfmach as ryfmach
import bel_lang_engine.rhyme_likes as rhyme_likes
import bel_lang_engine.ryfmach_phonetics as ryfmach_phonetics
import bel_lang_engine.ryfmach_morphemics as ryfmach_morphemics
from pprint import pprint

from logging.handlers import RotatingFileHandler
import logging
import os
import time

app = Flask(__name__, template_folder='static/templates')
app.config['SECRET_KEY'] = 'garikgoyda_secret_key'

app_file_handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=1 * 1024 * 1024,  # 1 MB
    backupCount=10,
    encoding="utf-8",
)

app_file_handler.setLevel(logging.INFO)
app_file_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s %(levelname)s "
        "[%(name)s] %(message)s"
    )
)

app.logger.setLevel(logging.INFO)
app.logger.addHandler(app_file_handler)


def get_like_payload():
    data = request.get_json(silent=True) or {}
    request_word = data.get("request", {})
    rhyme_word = data.get("rhyme", {})

    try:
        payload = {
            "request_word": str(request_word["word"]),
            "request_stress": int(request_word["stress"]),
            "rhyme_word": str(rhyme_word["word"]),
            "rhyme_stress": int(rhyme_word["stress"]),
        }
    except (KeyError, TypeError, ValueError):
        return None

    if not payload["request_word"] or not payload["rhyme_word"]:
        return None

    return payload


def update_rhyme_like_score(delta: int):
    payload = get_like_payload()
    if payload is None:
        return jsonify(error="Invalid like payload"), 400

    score = rhyme_likes.update_score(delta=delta, **payload)
    return jsonify(score=score)


@app.route('/')
def rhyme_page():
    input_word_info = session.get('rhyme_input_word_info', {'word': ''})
    session['rhyme_input_word_info'] = input_word_info
    return render_template(
        'rhyme_page.html',
        title="Рыфмач - падабраць рыфму",
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

    app.logger.info(f"{str(request.remote_addr)} Response time: {int((time.time() - start_time) * 1000)} ms")

    session['rhyme_input_word_info'] = input_word_info
    return jsonify(rhymes_list=rhymes, word_found=word_found)


@app.route('/rhyme/like', methods=['POST'])
def like_rhyme():
    return update_rhyme_like_score(1)


@app.route('/rhyme/dislike', methods=['POST'])
def dislike_rhyme():
    return update_rhyme_like_score(-1)


@app.route('/phonetics')
def phonetics_page():
    input_word_info = {'word': ''} # session.get('phon_input_word_info', {'word': ''})
    # session['phon_input_word_info'] = input_word_info
    return render_template(
        'phonetics_page.html',
        title="Рыфмач - фанетычны разбор",
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

    app.logger.info(f"{str(request.remote_addr)} Response time: {int((time.time() - start_time) * 1000)} ms")

    # session['phon_input_word_info'] = input_word_info
    return jsonify(word_variants=analysed, word_found=word_found)


@app.route('/morphemics')
def morphemics_page():
    input_word_info = session.get("sklad_input_word_info", {"word": ""})
    
    return render_template(
        "morphemics_page.html",
        title="Рыфмач - марфемны разбор",
        page_description="Рыфмач. Марфемны і словаўтваральны разбор, разбор па складзе. Морфемный разбор, разбор слова по составу.",
        input_word=input_word_info["word"],
        add_search_filter_button=False,
        canonical_url="https://ryfmach.online/morphemics"
    )


@app.route('/morphemics', methods=['POST'])
def morphemic_analysis():
    input_word_info = request.json
    if input_word_info.get('word') is None:
        return jsonify(phon_analys=[], word_found=False)
    
    session["sklad_input_word_info"] = input_word_info

    start_time = time.time()
    app.logger.info("%s Request morphemics: %s", str(request.remote_addr), str(input_word_info))

    analysed = ryfmach_morphemics.input_morphemic_analysis(input_word_info)
    app.logger.info(analysed)
    word_found = len(analysed) > 0

    app.logger.info(f"{str(request.remote_addr)} Response time: {int((time.time() - start_time) * 1000)} ms")

    # session['phon_input_word_info'] = input_word_info
    return jsonify(variants=analysed, word_found=word_found)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/x-icon')


@app.route('/sitemap')
def sitemap():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'sitemap.xml', mimetype='application/xml')


if __name__ == '__main__':
    app.run(port=20004, host='127.0.0.1')
