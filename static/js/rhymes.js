var alphabet = "-абвгдеёжзійклмнопрстуўфхцчш'ыьэюя";
var vowels= "аеёіоуыэюя";

var rhymes_response = [];
var precalc_rhymes_html = [];
var precalc_rhymes_count = [];

var w;
var accent_index = -1;
var filtered_parts_of_speech = [1, 1, 1, 1, 1, 1, 1];
var filtered_only_initial = false;
var search_mistake = -1;
var sort_mode = "quality";

const search_input_rhyme = document.getElementById("search-input");
const search_form = document.getElementById("search-form");
const search_button_rhyme = document.getElementById("search-button");
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
const search_accent_button = document.getElementById("search-accent-button");
const save_filters_button = document.getElementById("save-filters-button");
const scroll_up_button = document.querySelector(".button-scroll-up");

const fa_long_arrow_left = `<i class="fa fa-long-arrow-left" aria-hidden="true"></i>`

function set_loading(is_loading) {
    search_button_rhyme.disabled = is_loading;
    search_icon.hidden = is_loading;
    search_spinner.hidden = !is_loading;
}


function escape_html(value) {
    return String(value ?? "").replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
    }[char]));
}


function bind_events() {
    search_form.addEventListener("submit", (event) => {
        event.preventDefault();
        post_rhymes_request();
    });
    search_accent_button.addEventListener("click", post_rhymes_with_manual_accent);
    save_filters_button.addEventListener("click", update_filters);
    scroll_up_button.addEventListener("click", scroll_up);
}


function is_belarusian(word){
    for (let char in word){
        if (!alphabet.includes(word[char].toLowerCase()))
            return false;
    }
    return true;
}


function word_contains_vowels(word){
    let seen_vowel = false;
    for (let char in word)
        if (vowels.includes(word[char]))
            seen_vowel = true;
    return seen_vowel;
}


function word_with_accent(word, accent, classes_accent="accent-vowel"){
    word = String(word ?? "");
    if (accent !== undefined && accent !== null && accent >= 0 && accent < word.length)
        return escape_html(word.slice(0, accent)) + `<span class="${classes_accent}">${escape_html(word[accent])}</span>` + escape_html(word.slice(accent + 1));
    return escape_html(word);
}


function word_data_to_html(word_data, classes_normal="info-text", classes_accent="accent-vowel"){
    let word = word_data.word;
    let accent = word_data.accent;

    let text = word_with_accent(word, accent, classes_accent);
    if (word_data.is_initial !== undefined){
        if (!word_data.is_initial)
            text += ` ${fa_long_arrow_left} ${word_with_accent(word_data.initial_word, word_data.initial_accent, classes_accent)}`;
        text += ` (${escape_html(word_data.part_of_speech)})`;
    }

    text = `<p class="${classes_normal}">${text}</p>`;
    return text;
}


function update_rhymes(word_variant_index){
    dropdown_choose_word.innerHTML = "";
    if (precalc_rhymes_html.length > 1)
        dropdown_choose_word.innerHTML = `${word_variant_index + 1}/${precalc_rhymes_html.length} `;
    dropdown_choose_word.innerHTML +=
        word_data_to_html(rhymes_response.rhymes_list[word_variant_index].word_variant);
    
    rhymes_list.innerHTML = precalc_rhymes_html[word_variant_index];
    rhymes_count_text.innerHTML = precalc_rhymes_count[word_variant_index];
}


function process_rhymes_response(data){
    rhymes_list.innerHTML = "";

    rhymes_response = data;
    
    set_loading(false);

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

    precalc_rhymes_html = precalc_rhymes_html.slice(0, data.rhymes_list.length)
    precalc_rhymes_count = precalc_rhymes_count.slice(0, data.rhymes_list.length)
    for (let i in data.rhymes_list){
        let word_data = data.rhymes_list[i].word_variant;
        dropdown_choose_word_menu.innerHTML += `<li><button class="dropdown-item" data-rhyme-index="${i}">${word_data_to_html(word_data)}</button></li>`;

        precalc_rhymes_html[i] = "";
        const rhymes_data = data.rhymes_list[i].rhymes_data;

        if (rhymes_data.length == 0){
            precalc_rhymes_html[i] += `<div class="alert alert-info info-text" role="alert">Пу-пу-пу! Рыфмаў абранай трапнасці не знайшлося. Змяніце фільтры (<i class="fa fa-cog"></i>) або паспрабуйце іншае слова.</div>`;
            precalc_rhymes_count[i] = ` - `;
        }
        else{
            rhymes_count_text.innerHTML = `Рыфмы: ${rhymes_data.length}`;
            if (rhymes_data.length == 1000)
                rhymes_count_text.innerHTML += `<span class="count-warning">(!)</span>`
            precalc_rhymes_count[i] = rhymes_count_text.innerHTML;
        }

        for (let j in rhymes_data){
            precalc_rhymes_html[i] += `<li>${word_data_to_html(rhymes_data[j], "rhyme-word")}</li>`;
        }
    }

    dropdown_choose_word_menu.querySelectorAll("[data-rhyme-index]").forEach((button) => {
        button.addEventListener("click", () => update_rhymes(Number(button.dataset.rhymeIndex)));
    });
    update_rhymes(0);
}


function generate_letter_buttons(){
    accent_index = -1;
    search_status_info.innerHTML = `<div class="alert alert-warning info-text" role="alert">Невядомае слова</div>`

    let word = w;

    if (!word_contains_vowels(word)){
        search_status_info.innerHTML = `<div class="alert alert-danger info-text" role="alert">У гэтым слове няма галосных</div>`;
        return;
    }
    
    letter_buttons_block.innerHTML = "";
    manual_accent_modal.show();
    
    const letters_div = letter_buttons_block;

    for (let char in word){
        if (vowels.includes(word[char])){
            letters_div.innerHTML += `\n<button type="button" class="square-letter-button-outline" data-accent-index="${char}" id="letter_btn${char}">${escape_html(word[char])}</button>`;
            accent_index = parseInt(char);
        }
        else{
            letters_div.innerHTML += `\n<div class="square-letter-label"><label>${escape_html(word[char])}</label></div>`;
        }
    }

    letters_div.querySelectorAll("[data-accent-index]").forEach((button) => {
        button.addEventListener("click", () => letter_button_onclick(Number(button.dataset.accentIndex)));
    });
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


function post_rhymes_request(){
    for (let i = 1; i <= 7; ++i){
        filtered_parts_of_speech[i - 1] = document.getElementById(`check-posp-${i}`).checked;
    }
    filtered_only_initial = document.getElementById(`check-only-initial`).checked;
    search_mistake = parseInt($("#search-mistake-radio :input:radio:checked").val());
    sort_mode = $("#sort-mode-radio :input:radio:checked").val();

    w = clean_input_word(search_input_rhyme.value);

    accent_index = -1;

    if (w == ""){
        word_variants_block.style.visibility = "visible";
        return;
    }

    if (!is_belarusian(w)){        
        search_status_info.innerHTML = `<div class="alert alert-danger info-text" role="alert">Слова павінна складацца толькі з беларускіх літар!</div>`;
        return;
    }

    if (w.length > 40){        
        search_status_info.innerHTML = `<div class="alert alert-danger info-text" role="alert">Нельга ўводзіць словы даўжэй за 40 літар! </div>`;
        return;
    }

    set_loading(true);
    rhymes_block.style.display = "none";

    $.ajax({
        url: "/",
        method: "post",
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify({
            "word": w,
            "filtered_posp": filtered_parts_of_speech,
            "only_initial": filtered_only_initial,
            "search_mistake": search_mistake,
            "sort_mode": sort_mode,
        }),
        success: process_rhymes_response,
        error: () => {
            search_status_info.innerHTML = `<div class="alert alert-danger info-text" role="alert">Не атрымалася выканаць пошук. Паспрабуйце яшчэ раз.</div>`;
        },
        complete: () => set_loading(false),
    });
}


function post_rhymes_with_manual_accent(){
    if (w == ""){
        word_variants_block.style.visibility = "visible";
        return;
    }

    if (!is_belarusian(w)){        
        search_status_info.innerHTML = `<div class="alert alert-danger info-text" role="alert">Слова павінна складацца толькі з беларускіх літар!</div>`;
        return;
    }

    if (w.length > 40){        
        search_status_info.innerHTML = `<div class="alert alert-danger info-text" role="alert">Нельга ўводзіць словы даўжэй за 40 літар! </div>`;
        return;
    }

    if (accent_index == -1){        
        search_status_info.innerHTML = `<div class="alert alert-danger info-text" role="alert">Укажыце націскную галосную</div>`
        return;
    }

    manual_accent_modal.hide();
    
    search_status_info.innerHTML = "";
    set_loading(true);

    $.ajax({
        url: "/",
        method: "post",
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify({
            "word": w,
            "accent": accent_index,
            "filtered_posp": filtered_parts_of_speech,
            "only_initial": filtered_only_initial,
            "search_mistake": search_mistake,
            "sort_mode": sort_mode,
        }),
        success: process_rhymes_response,
        error: () => {
            search_status_info.innerHTML = `<div class="alert alert-danger info-text" role="alert">Не атрымалася выканаць пошук. Паспрабуйце яшчэ раз.</div>`;
        },
        complete: () => set_loading(false),
    });
}


function update_filters(){
    for (let i = 1; i <= 7; ++i){
        filtered_parts_of_speech[i - 1] = document.getElementById(`check-posp-${i}`).checked;
    }
    filtered_only_initial = document.getElementById(`check-only-initial`).checked;
    search_mistake = parseInt($("#search-mistake-radio :input:radio:checked").val());
    sort_mode = $("#sort-mode-radio :input:radio:checked").val();

    let new_input = clean_input_word(search_input_rhyme.value);
    if (new_input != w){
        w = new_input;
        accent_index = -1;
    }

    if (w == "" || !is_belarusian(w) || w.length > 40)
        return;

    search_status_info.innerHTML = "";
    set_loading(true);

    if (accent_index == -1){
        $.ajax({
            url: "/",
            method: "post",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({
                "word": w,
                "filtered_posp": filtered_parts_of_speech,
                "only_initial": filtered_only_initial,
                "search_mistake": search_mistake,
                "sort_mode": sort_mode,
            }),
                success: process_rhymes_response,
                error: () => {
                    search_status_info.innerHTML = `<div class="alert alert-danger info-text" role="alert">Не атрымалася абнавіць фільтры. Паспрабуйце яшчэ раз.</div>`;
                },
                complete: () => set_loading(false),
            });
    }
    else{
        $.ajax({
            url: "/",
            method: "post",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({
                "word": w,
                "accent": accent_index,
                "filtered_posp": filtered_parts_of_speech,
                "only_initial": filtered_only_initial,
                "search_mistake": search_mistake,
                "sort_mode": sort_mode,
            }),
            success: process_rhymes_response,
            error: () => {
                search_status_info.innerHTML = `<div class="alert alert-danger info-text" role="alert">Не атрымалася абнавіць фільтры. Паспрабуйце яшчэ раз.</div>`;
            },
            complete: () => set_loading(false),
        });
    }
}


function scroll_up(){
    window.scrollTo({top: 0, behavior: "smooth"});
}


bind_events();
