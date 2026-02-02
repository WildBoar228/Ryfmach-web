var alphabet = "-абвгдеёжзійклмнопрстуўфхцчш'ыьэюя";
var vowels= "аеёіоуыэюя";

var cons_sound_list = ['б', "б'", 'п', "п'", 'в', "в'", 'г', "г'", 'х', "х'", 'ґ', "ґ'", 'к', "к'", 'д', "дз'", 'т', "ц'", 'дз', 'ц', 'ж', 'ш', 'з', "з'", 'с', "с'", 'й', 'л', "л'", 'м', "м'", 'н', "н'", 'р', 'ф', "ф'", 'дж', 'ч', 'ў'];
var cons_soft_sound_list = ["б'", "п'", "в'", "г'", "х'", "ґ'", "к'", "дз'", "ц'", "з'", "с'", 'й', "л'", "м'", "н'", "ф'"];

var sklad_response = [];
var precalc_sklad_html = [];

var input_word = "";
var accent_index = -1;

const search_input_sklad = document.getElementById("search-input");
const search_button_sklad = document.getElementById("search-button");
const search_icon = document.getElementById("search-icon");
const search_spinner = document.getElementById("search-spinner");
const search_status_text = document.getElementById("search-status-text");
const search_status_info = document.getElementById("search-status-info");

const word_variants_block = document.getElementById("word-variants-block");
const dropdown_choose_word = document.getElementById("dropdown-choose-word");
const dropdown_choose_word_menu = document.getElementById("dropdown-choose-word-menu");

const manual_accent_modal = new bootstrap.Modal(document.getElementById('manual-accent-modal'));
const letter_buttons_block = document.getElementById("letter-buttons-block");

const sklad_analysis_block = document.getElementById("sklad-analysis-block");

const fa_long_arrow_left = `<i class="fa fa-long-arrow-left" aria-hidden="true"></i>`
const fa_long_arrow_right = `<i class="fa fa-long-arrow-right" aria-hidden="true"></i>`

const fa_warning = `<i class="fa fa-warning" style="color: orange"></i>`

const kPartTypeUnknown = 0;
const kPartTypePrefix  = 1;
const kPartTypeRoot    = 2;
const kPartTypeSuffix  = 3;
const kPartTypeEnding  = 4;


window.onload = () => {
    search_button_sklad.onclick = post_sklad_request;
    word_variants_block.style.display = "none";
}


function is_belarusian(word){
    for (char in word){
        if (!alphabet.includes(word[char].toLowerCase()))
            return false;
    }
    return true;
}


function is_vowel(sound) {
    if (sound.length == 0) return false;
    if ("аоуыіэ".includes(sound[0])) {
        return true;
    }
    if (sound.length == 3) {
        if (sound[0] == "_" && "аоуыіэ".includes(sound[1]) && sound[2] == "_") {
            return true;
        }
    }
    return false;
}


function is_consonant(sound) {
    return cons_sound_list.includes(sound);
}


function process_sklad_response(data){
    sklad_response = data;
    
    search_icon.style.display = "block";
    search_spinner.style.display = "none";

    sklad_analysis_block.innerHTML = "";

    let analysis_content = "";
    for (i in data.variants){
        analysis_content = "";
        const word_analysis = data.variants[i].analysis;
        
        for (j in word_analysis) {
            let classes = "word-part ";
            let show_text = word_analysis[j].text;
            
            switch (word_analysis[j].type) {
                case kPartTypePrefix:
                    classes += "word-part-prefix";
                    break;
                case kPartTypeRoot:
                    classes += "word-part-root";
                    break;
                case kPartTypeSuffix:
                    classes += "word-part-suffix";
                    if (show_text == "") { show_text = "&empty;" }
                    break;
                case kPartTypeEnding:
                    classes += "word-part-ending";
                    break;
                default:
                    classes += "word-part-unknown";
                    break;
            }
            analysis_content += `<div class="${classes}">${show_text}</div>`;
        }
        
        if (!data.variants[i].sure) {
            analysis_content += `<div class="word-part">${fa_warning}</div>`
        }

        sklad_analysis_block.innerHTML += `<div class="analysed-word-block">${analysis_content}</div>`;
    }

    if (data.variants.length == 0) {
        const alert = `<div class="alert alert-danger info-text" role="alert">На жаль, слова не знойдзена :(</div>`
        sklad_analysis_block.innerHTML = `<div class="analysed-word-block">${alert}</div>`;
    }
}


function clean_input_word(w) {
    w = w.toLowerCase();
    let pref = 0;
    while (pref < w.length && w[pref] == ' ') {
        ++pref;
    }
    let suf = w.length - 1;
    while (suf >= 0 && w[suf] == ' ') {
        --suf;
    }
    w = w.slice(pref, suf + 1);
    w = w.replaceAll(" ", "-");
    w = w.replaceAll("и", "і");
    w = w.replaceAll("i", "і"); // english i
    w = w.replaceAll("щ", "ў");
    w = w.replaceAll("ъ", "'");
    return w;
}


function post_sklad_request(){
    input_word = clean_input_word(search_input_sklad.value);
    accent_index = -1;

    if (input_word == ""){
        word_variants_block.style.visibility = "visible";
        return;
    }

    if (!is_belarusian(input_word)){        
        search_status_info.innerHTML = `<div class="alert alert-danger info-text" role="alert">Слова павінна складацца толькі з беларускіх літар!</div>`;
        return;
    }

    if (input_word.length > 40){        
        search_status_info.innerHTML = `<div class="alert alert-danger info-text" role="alert">Нельга ўводзіць словы даўжэй за 40 літар! </div>`;
        return;
    }

    search_icon.style.display = "none";
    search_spinner.style.display = "block";

    $.ajax({
        url: "/morphemics",
        method: "post",
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify({
            "word": input_word,
        }),
        success: process_sklad_response,
    });
}
