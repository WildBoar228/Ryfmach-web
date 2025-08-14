from flask import Flask, render_template, redirect, request, make_response, session, jsonify
import json
import ryfmach
from pprint import pprint

app = Flask(__name__, template_folder='static/templates')
app.config['SECRET_KEY'] = 'garikgoyda_secret_key'


@app.route('/')
def main_page():
    input_word_info = session.get('input_word_info', {'word': ''})
    # rhymes = ryfmach.rhymes_text_list(input_word)
    session['input_word_info'] = input_word_info
    return render_template('index.html', input_word=input_word_info["word"]) #, rhymes=rhymes, input_word=input_word, errors=['Памылка'])


@app.route('/', methods=['POST'])
def update_rhymes():
    input_word_info = request.json
    if input_word_info.get('word') is None:
        session['input_word_info'] = {'word': ''}
        return jsonify(rhymes_list=[], word_found=False)

    pprint(input_word_info)
    rhymes = ryfmach.rhymes_text_list(input_word_info)
    word_found = True
    if rhymes is None:
        rhymes = []
        word_found = False
    
    # pprint(rhymes)

    session['input_word_info'] = input_word_info
    return jsonify(rhymes_list=rhymes, word_found=word_found)
    # return render_template('rhymes_content.html', rhymes=rhymes)


@app.route('/<input_word>', methods=['GET'])
def show_rhymes(input_word):
    if input_word == 'favicon.ico':
        input_word = ''

    session['input_word_info'] = {'word': input_word}
    return redirect('/')

    # if input_word == '' or input_word == 'favicon.ico':
    #     return redirect('/')

    # rhymes = ryfmach.rhymes_text_list(input_word)
    # if isinstance(rhymes, int):
    #     return render_template('index.html')

    # return render_template('index.html', rhymes=rhymes, input_word=input_word)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')