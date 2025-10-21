var alphabet = "-абвгдеёжзійклмнопрстуўфхцчш'ыьэюя";
var vowels= "аеёіоуыэюя";

var phon_response = [];
var precalc_phon_html = [];

var input_word;
var accent_index = -1;

const search_input_rhyme = document.getElementById("search-input-rhyme");
const search_icon = document.getElementById("search-icon");
const search_spinner = document.getElementById("search-spinner");
const search_status_text = document.getElementById("search-status-text");
const search_status_info = document.getElementById("search-status-info");

const word_variants_block = document.getElementById("word-variants-block");
const dropdown_choose_word = document.getElementById("dropdown-choose-word");
const dropdown_choose_word_menu = document.getElementById("dropdown-choose-word-menu");

const manual_accent_modal = new bootstrap.Modal(document.getElementById('manual-accent-modal'));
const letter_buttons_block = document.getElementById("letter-buttons-block");

const fa_long_arrow_left = `<i class="fa fa-long-arrow-left" aria-hidden="true"></i>`


function is_belarusian(word){
    for (char in word){
        if (!alphabet.includes(word[char].toLowerCase()))
            return false;
    }
    return true;
}


function word_contains_vowels(word){
    let seen_vowel = false;
    for (char in word)
        if (vowels.includes(word[char]))
            seen_vowel = true;
    return seen_vowel;
}


function word_with_accent(word, accent, classes_accent="accent-vowel"){
    if (accent)
        word = word.slice(0, accent) + `<span class="${classes_accent}">${word[accent]}</span>` + word.slice(accent + 1);
    return word;
}


function word_data_to_html(word_data, classes_normal="info-text", classes_accent="accent-vowel"){
    let word = word_data.word;
    let accent = word_data.accent;

    let text = word_with_accent(word, accent);
    if (word_data.is_initial !== undefined){
        if (!word_data.is_initial)
            text += ` ${fa_long_arrow_left} ${word_with_accent(word_data.initial_word, word_data.initial_accent)}`;
        text += ` (${word_data.part_of_speech})`;
    }

    text = `<p class="${classes_normal}">${text}</p>`;
    return text;
}