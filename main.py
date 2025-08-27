from flask import Flask, render_template, redirect, request, make_response, session, jsonify, send_from_directory
import json
import ryfmach
from pprint import pprint
import logging
import os

app = Flask(__name__, template_folder='static/templates')
app.config['SECRET_KEY'] = 'garikgoyda_secret_key'
app.logger.setLevel(logging.INFO)


@app.route('/')
def main_page():
    input_word_info = session.get('input_word_info', {'word': ''})
    session['input_word_info'] = input_word_info
    return render_template('index.html', input_word=input_word_info["word"])


@app.route('/', methods=['POST'])
def update_rhymes():
    input_word_info = request.json
    if input_word_info.get('word') is None:
        session['input_word_info'] = {'word': ''}
        return jsonify(rhymes_list=[], word_found=False)

    app.logger.info("%s Request rhyme: %s", str(request.remote_addr), str(input_word_info))
    rhymes = ryfmach.rhymes_text_list(input_word_info)
    word_found = True
    if rhymes is None:
        rhymes = []
        word_found = False

    session['input_word_info'] = input_word_info
    return jsonify(rhymes_list=rhymes, word_found=word_found)


# @app.route('/add_word')
# def add_word_page():
#     return render_template('add_word.html')


# @app.route('/report')
# def report_page():
#     return "report page"


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/x-icon')


# @app.route('/<input_word>', methods=['GET'])
# def show_rhymes(input_word):
#     session['input_word_info'] = {'word': input_word}
#     return redirect('/')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')