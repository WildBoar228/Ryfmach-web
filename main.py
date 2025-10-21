from flask import Flask, render_template, redirect, request, make_response, session, jsonify, send_from_directory
import json
import ryfmach
from pprint import pprint
import logging
import os
import time

app = Flask(__name__, template_folder='static/templates')
app.config['SECRET_KEY'] = 'garikgoyda_secret_key'
app.logger.setLevel(logging.INFO)


@app.route('/')
def rhyme_page():
    input_word_info = session.get('input_word_info', {'word': ''})
    session['input_word_info'] = input_word_info
    return render_template(
        'rhyme_page.html',
        title="Рыфмач&nbsp;&ndash; падабраць рыфму",
        input_word=input_word_info["word"]
    )


@app.route('/', methods=['POST'])
def update_rhymes():
    input_word_info = request.json
    if input_word_info.get('word') is None:
        session['input_word_info'] = {'word': ''}
        return jsonify(rhymes_list=[], word_found=False)

    start_time = time.time()
    app.logger.info("%s Request rhyme: %s", str(request.remote_addr), str(input_word_info))
    rhymes = ryfmach.rhymes_text_list(input_word_info)
    word_found = True
    if rhymes is None:
        rhymes = []
        word_found = False

    print(f"{str(request.remote_addr)} Response time: {int((time.time() - start_time) * 1000)} ms")

    session['input_word_info'] = input_word_info
    return jsonify(rhymes_list=rhymes, word_found=word_found)


@app.route('/phonetics')
def phonetics_page():
    input_word_info = session.get('input_word_info', {'word': ''})
    session['input_word_info'] = input_word_info
    return render_template(
        'phonetics_page.html',
        title="Рыфмач&nbsp;&ndash; фанетычны разбор",
        input_word=input_word_info["word"]
    )


@app.route('/phonetics', methods=['POST'])
def phonetic_analysis():
    input_word_info = request.json
    if input_word_info.get('word') is None:
        session['input_word_info'] = {'word': ''}
        return jsonify(phon_analys=[], word_found=False)

    start_time = time.time()
    app.logger.info("%s Request rhyme: %s", str(request.remote_addr), str(input_word_info))

    # rhymes = ryfmach.rhymes_text_list(input_word_info)
    # word_found = True
    # if rhymes is None:
    #     rhymes = []
    #     word_found = False

    print(f"{str(request.remote_addr)} Response time: {int((time.time() - start_time) * 1000)} ms")

    session['input_word_info'] = input_word_info
    return jsonify(phon_analys=[], word_found=False)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/x-icon')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')