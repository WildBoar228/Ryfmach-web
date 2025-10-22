var alphabet = "-абвгдеёжзійклмнопрстуўфхцчш'ыьэюя";
var vowels= "аеёіоуыэюя";

var phon_response = [];
var precalc_phon_html = [];

var input_word;
var accent_index = -1;

const search_input_phon = document.getElementById("search-input");
const search_button_phon = document.getElementById("search-button");
const search_icon = document.getElementById("search-icon");
const search_spinner = document.getElementById("search-spinner");
const search_status_text = document.getElementById("search-status-text");
const search_status_info = document.getElementById("search-status-info");

const word_variants_block = document.getElementById("word-variants-block");
const dropdown_choose_word = document.getElementById("dropdown-choose-word");
const dropdown_choose_word_menu = document.getElementById("dropdown-choose-word-menu");

const manual_accent_modal = new bootstrap.Modal(document.getElementById('manual-accent-modal'));
const letter_buttons_block = document.getElementById("letter-buttons-block");

const phon_analysis_block = document.getElementById("phon-analysis-block");

const fa_long_arrow_left = `<i class="fa fa-long-arrow-left" aria-hidden="true"></i>`
const fa_long_arrow_right = `<i class="fa fa-long-arrow-right" aria-hidden="true"></i>`

window.onload = () => {
    search_button_phon.onclick = post_phon_request;
}


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


function update_phon(word_variant_index){
    dropdown_choose_word.innerHTML = "";
    if (precalc_phon_html.length > 1)
        dropdown_choose_word.innerHTML = `${word_variant_index + 1}/${precalc_phon_html.length} `;
    dropdown_choose_word.innerHTML +=
        word_data_to_html(phon_response.word_variants[word_variant_index].word_variant);
    
    phon_analysis_block.innerHTML = precalc_phon_html[word_variant_index];
}


function process_phon_response(data){
    phon_response = data;
    
    search_icon.style.display = "block";
    search_spinner.style.display = "none";

    word_variants_block.style.visibility="visible";
    dropdown_choose_word.innerHTML="-";
    dropdown_choose_word_menu.innerHTML = "";
    search_status_text.innerHTML = `Варыянты: ${Object.keys(data.word_variants).length}`;
    search_status_info.innerHTML = "";

    if (Object.keys(data.word_variants).length == 0){
        generate_letter_buttons();
        return;
    }

    precalc_phon_html = precalc_phon_html.slice(0, data.word_variants);
    for (i in data.word_variants){
        word_data = data.word_variants[i].word_variant;
        dropdown_choose_word_menu.innerHTML += `<li><button class="dropdown-item" onclick=update_phon(${i})>${word_data_to_html(word_data)}</button></li>`;

        precalc_phon_html[i] = "";
        const transcription = data.word_variants[i].transcription;
        const phenomena = data.word_variants[i].phenomena;

        for (let j in transcription.length) {
            precalc_phon_html[i] += `${transcription[j][1]} `;
        }
        precalc_phon_html[i] += `\n<ol>`;

        for (let j in transcription.length) {
            precalc_phon_html[i] += `<li>${word_data["word"][transcription[i][0]]}   ${fa_long_arrow_right}   ${transcription[i][1]}</li>`;
        }
    }

    update_phon(0);
}


function generate_letter_buttons(){
    accent_index = -1;
    search_status_info.innerHTML = `<div class="alert alert-warning info-text" role="alert">Невядомае слова</div>`

    let word = input_word;

    if (!word_contains_vowels(word)){
        search_status_info.innerHTML = `<div class="alert alert-danger info-text" role="alert">У гэтым слове няма галосных</div>`;
        return;
    }
    
    letter_buttons_block.innerHTML = "";
    manual_accent_modal.show();
    
    const letters_div = letter_buttons_block;

    for (char in word){
        if (vowels.includes(word[char])){
            letters_div.innerHTML += `\n<button type="button" class="square-letter-button-outline" onclick="letter_button_onclick(${char})" id="letter_btn${char}">${word[char]}</button>`;
            accent_index = parseInt(char);
        }
        else{
            letters_div.innerHTML += `\n<div class="square-letter-label"><label>${word[char]}</label></div>`;
        }
    }

    letter_button_onclick(accent_index);
}


function letter_button_onclick(index){
    const btn = document.getElementById(`letter_btn${index}`);
    if (accent_index != -1){
        const prev_btn = document.getElementById(`letter_btn${accent_index}`);
        prev_btn.classList.remove("square-letter-button-chosen");
        prev_btn.classList.add("square-letter-button-outline");
    }

    accent_index = index;
    btn.classList.remove("square-letter-button-outline");
    btn.classList.add("square-letter-button-chosen");
}


function post_phon_request(){
    input_word = search_input_phon.value.toLowerCase();
    input_word = input_word.replaceAll(" ", "");
    
    input_word = input_word.replaceAll("и", "і");
    input_word = input_word.replaceAll("щ", "ў");
    input_word = input_word.replaceAll("ъ", "'");

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
        url: "/phonetics",
        method: "post",
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify({
            "word": input_word,
        }),
        success: process_phon_response,
    });
}


function post_phon_with_manual_accent(){
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

    if (accent_index == -1){        
        search_status_info.innerHTML = `<div class="alert alert-danger info-text" role="alert">Укажыце націскную галосную</div>`
        return;
    }

    manual_accent_modal.hide();
    
    search_status_info.innerHTML = "";
    search_icon.style.display = "none";
    search_spinner.style.display = "block";

    $.ajax({
        url: "/phonetics",
        method: "post",
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify({
            "word": input_word,
            "accent": accent_index
        }),
        success: process_phon_response,
    });
}


function scroll_up(){
    window.scrollTo({top: 0, behavior: "smooth"});
}