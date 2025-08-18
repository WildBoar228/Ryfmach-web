var alphabet = "-абвгдеёжзійклмнопрстуўфхцчш'ыьэюя";
var vowels= "аеёіоуыэюя";

var rhymes_response = [];
var precalc_rhymes_html = [];
var precalc_rhymes_count = [];

var input_word;
var accent_index = -1;
var filtered_parts_of_speech = [1, 1, 1, 1, 1, 1, 1];
var filtered_only_initial = false;

const search_input_rhyme = document.getElementById("search-input-rhyme");
const search_icon = document.getElementById("search-icon");
const search_spinner = document.getElementById("search-spinner");
const search_status_text = document.getElementById("search-status-text");
const search_status_info = document.getElementById("search-status-info");

const word_variants_block = document.getElementById("word-variants-block");
const dropdown_choose_word = document.getElementById("dropdown-choose-word");
const dropdown_choose_word_menu = document.getElementById("dropdown-choose-word-menu");
const rhymes_block = document.getElementById("rhymes-block");
const rhymes_count_text = document.getElementById("rhyme-count-text");
const rhymes_list = document.getElementById("rhymes-list");

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


function update_rhymes(word_variant_index){
    dropdown_choose_word.innerHTML = word_data_to_html(rhymes_response.rhymes_list[word_variant_index].word_variant);
    
    rhymes_list.innerHTML = precalc_rhymes_html[word_variant_index];
    rhymes_count_text.innerHTML = precalc_rhymes_count[word_variant_index];
}


function process_rhymes_response(data){
    rhymes_list.innerHTML = "";

    rhymes_response = data;
    
    search_icon.style.display = "block";
    search_spinner.style.display = "none";

    word_variants_block.style.visibility="visible";
    dropdown_choose_word.innerHTML="-";
    dropdown_choose_word_menu.innerHTML = "";
    search_status_text.innerHTML = `Варыянты: ${Object.keys(data.rhymes_list).length}`;
    search_status_info.innerHTML = "";

    if (Object.keys(data.rhymes_list).length == 0){
        generate_letter_buttons();
        return;
    }
    
    rhymes_block.style.display = "block";

    for (i in data.rhymes_list){
        word_data = data.rhymes_list[i].word_variant;
        dropdown_choose_word_menu.innerHTML += `<li><button class="dropdown-item" onclick=update_rhymes(${i})>${word_data_to_html(word_data)}</button></li>`;

        precalc_rhymes_html[i] = "";
        const rhymes_data = data.rhymes_list[i].rhymes_data;

        if (rhymes_data.length == 0){
            precalc_rhymes_html[i] += `<div class="alert alert-info info-text" role="alert">Пу-пу-пу! Рыфмаў не знайшлося. Паспрабуйце іншае слова. Падказка: чым бліжэй націск да канца слова, тым лягчэй знайсці рыфму.</div>`;
            precalc_rhymes_count[i] = ` - `;
        }
        else{
            rhymes_count_text.innerHTML = `Рыфмы: ${rhymes_data.length}`;
            if (rhymes_data.length == 1000)
                rhymes_count_text.innerHTML += `<span style="color: red">(!)</span>`
            precalc_rhymes_count[i] = rhymes_count_text.innerHTML;
            // precalc_rhymes_html[i] = `<h1 class="rhyme-word" style="text-align: center">${rhymes_count_text}</h1>` + precalc_rhymes_html[i];
        }

        for (j in rhymes_data){
            precalc_rhymes_html[i] += `<li>${word_data_to_html(rhymes_data[j], classes_normal="rhyme-word")}</li>`;
        }
    }

    update_rhymes(0);
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
        }
        else{
            letters_div.innerHTML += `\n<div class="square-letter-label"><label>${word[char]}</label></div>`;
        }
    }
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


function post_rhymes_request(){
    input_word = search_input_rhyme.value.toLowerCase();
    input_word = input_word.replaceAll(" ", "");
    
    input_word = input_word.replaceAll("и", "і");
    input_word = input_word.replaceAll("щ", "ў");
    input_word = input_word.replaceAll("ъ", "'");

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
    rhymes_block.style.display = "none";

    $.ajax({
        url: "/",
        method: "post",
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify({
            "word": input_word,
            "filter_posp": filtered_parts_of_speech,
            "only_initial": filtered_only_initial,
        }),
        success: process_rhymes_response,
    });
}


function post_rhymes_with_manual_accent(){
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
        url: "/",
        method: "post",
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify({
            "word": input_word,
            "accent": accent_index,
            "filter_posp": filtered_parts_of_speech,
            "only_initial": filtered_only_initial,
        }),
        success: process_rhymes_response,
    });
}


function update_filters(){
    for (i = 1; i <= 7; ++i){
        filtered_parts_of_speech[i - 1] = document.getElementById(`check-posp-${i}`).checked;
    }
    filtered_only_initial = document.getElementById(`check-only-initial`).checked;

    search_status_info.innerHTML = "";
    search_icon.style.display = "none";
    search_spinner.style.display = "block";

    if (accent_index == -1){
        $.ajax({
            url: "/",
            method: "post",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({
                "word": input_word,
                "filtered_posp": filtered_parts_of_speech,
                "only_initial": filtered_only_initial,
            }),
            success: process_rhymes_response,
        });
    }
    else{
        $.ajax({
            url: "/",
            method: "post",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({
                "word": input_word,
                "accent": accent_index,
                "filtered_posp": filtered_parts_of_speech,
                "only_initial": filtered_only_initial,
            }),
            success: process_rhymes_response,
        });
    }
}


function scroll_up(){
    window.scrollTo({top: 0, behavior: "smooth"});
}