from bel_lang_engine.ryfmach import (
    get_word_data_from_db, get_word_forms, find_word_records_in_table,
    db_lock, con, cur
)
from bel_lang_engine.language import *
from pprint import pprint


prefix_parts = cur.execute("""SELECT * FROM morph_prefixes""").fetchall()
prefix_parts = sorted(prefix_parts, key=lambda rec: -len(rec[1]))


class MorphemType:
    UNKNOWN = 0
    PREFIX = 1
    ROOT = 2
    SUFFIX = 3
    ENDING = 4


class Morphem:
    def __init__(self,
                 text: str,
                 mtype: MorphemType = MorphemType.UNKNOWN):
        self.text = text
        self.mtype = mtype
        self.initial_form = ""
        # if self.text.endswith('ь'):
        #     self.initial_form = self.text[:-1]
    
    def get_initial(self):
        return self.text if self.initial_form == "" else self.initial_form
    
    def __str__(self):
        if self.initial_form:
            return f"({self.text} [{self.initial_form}], {self.mtype})"
        return f"({self.text}, {self.mtype})"
    
    def __repr__(self):
        if self.initial_form:
            return f"Morphem(\"{self.text}\" [\"{self.initial_form}\"], {[
                "UNKNOWN", "PREFIX", "ROOT", "SUFFIX", "ENDING"
                ][self.mtype]})"
        return f"Morphem(\"{self.text}\", {[
            "UNKNOWN", "PREFIX", "ROOT", "SUFFIX", "ENDING"
            ][self.mtype]})"
    

def input_morphemic_analysis(input_word_info) -> tuple[list, bool]:
    input_word_info["word"] = input_word_info["word"].replace("и", "і")
    input_word_info["word"] = input_word_info["word"].replace("щ", "ў")
    input_word_info["word"] = input_word_info["word"].replace("ъ", "'")

    if not is_belarusian(input_word_info["word"]) or len(input_word_info["word"]) > 40:
        return []
        
    return word_morphemic_analysis(input_word_info["word"])


def word_morphemic_analysis(word: str, fix_similar_letters = True) -> list:
    result = find_word_records_in_table(word, "morphemics", fix_similar_letters)

    # analysis found
    if len(result) > 0:
        result = list(map(lambda a: 
                          {"analysis": decrypt_analysis_to_json(a[2]),
                           "sure": True},
                          result))
        return result


    word_dicts = get_word_data_from_db(word, True)
    result = []
    for word_dict in word_dicts:
        result += try_sure_predictions_or_initial(word_dict)
    if result:
        return result
    

    # try remove prefixes
    prefix_morphems = []
    first_prefix, cut_word = cut_one_prefix(word)
    while first_prefix is not None:
        print(cut_word)
        prefix_morphems += first_prefix
        analysis_of_cut = word_morphemic_analysis(cut_word, fix_similar_letters)
        if len(analysis_of_cut):
            analysis_of_cut = list(map(lambda a: 
                                       {"analysis": prefix_morphems + a["analysis"],
                                        "sure": a["sure"]},
                                        analysis_of_cut))
            return analysis_of_cut
        
        first_prefix, cut_word = cut_one_prefix(cut_word)
        
    
    result = []
    for word_dict in word_dicts:
        result += try_other_predictions(word_dict)
    if result:
        return result

    return []


def cut_one_prefix(word: str):
    prefix_morphem = None
    cut_word = word
    for _, part_text, part_analysis in prefix_parts:
        if cut_word.startswith(part_text):
            prefix_morphem = decrypt_analysis_to_json(part_analysis)
            cut_word = cut_word[len(part_text):]
            break
    
    return prefix_morphem, cut_word


def cut_some_prefixes(word: str):
    prefix_morphems = []
    cut_word = word
    first_prefix, cut_word = cut_one_prefix(word)
    while first_prefix is not None:
        prefix_morphems += first_prefix
        first_prefix, cut_word = cut_one_prefix(cut_word)
    
    return prefix_morphems, cut_word


def extract_word_basis(word: dict) -> str:
    word_forms = get_word_forms(word["initial_id"])

    for i in range(len(word["word"])):
        is_common = True
        for form in word_forms:
            if not (i < len(form["word"]) and form["word"][i] == word["word"][i]):
                if (word["word"][i] not in ["ў", "ь", "'", "й"]
                    and form["word"][i] not in ["ў", "ь", "'", "й"]):
                    is_common = False
                    break

        if not is_common:
            return word["word"][:i]
    
    return word["word"]


def try_sure_predictions_or_initial(word_dict: dict) -> list[dict[list, bool]]:
    analysis = []
    if word_dict["part_of_speech_id"] == PartsOfSpeech.DZEIASLOU:
        if word_dict["word"][-3:] == "цца":
            if word_dict["is_initial"]:
                non_reflexive_word = word_dict["word"][:-2] + "ь"
                non_reflexive_analysis = word_morphemic_analysis(non_reflexive_word, False)

                for variant in non_reflexive_analysis:
                    if variant["analysis"][-1]["text"] == "ць":
                        variant["analysis"][-1]["text"] = "ц"
                        analysis.append({"analysis": variant["analysis"] + decrypt_analysis_to_json("<ца>"),
                                         "sure": variant["sure"]})
        
        elif word_dict["word"][-2:] == "ся":
            non_reflexive_word = word_dict["word"][:-2]
            non_reflexive_analysis = word_morphemic_analysis(non_reflexive_word, False)

            for variant in non_reflexive_analysis:
                analysis.append({"analysis": variant["analysis"] + decrypt_analysis_to_json("<ся>"),
                                 "sure": variant["sure"]})
        
        elif word_dict["word"][-3:] in ["ючы", "учы", "ўшы"]:
            non_reflexive_word = word_dict["word"][:-3] + "ць"
            dzeeprysl_suf = word_dict["word"][-3:]
            non_reflexive_analysis = word_morphemic_analysis(non_reflexive_word, False)
            print(non_reflexive_word)

            for variant in non_reflexive_analysis:
                print(variant["analysis"][-1])
                if variant["analysis"][-1]["text"] == "ць":
                    variant["analysis"][-1]["text"] = dzeeprysl_suf
                    analysis.append(variant)

    if len(analysis):
        return analysis
    
    if word_dict.get("is_initial") != True:
        return word_morphemic_analysis(word_dict["initial_word"])
    
    return []


def try_other_predictions(word_dict: dict) -> list[dict[list, bool]]:
    analysis = []

    if word_dict["part_of_speech_id"] == PartsOfSpeech.DZEIASLOU:
        if word_dict["is_initial"] and word_dict["word"][-2:] == "ць":
            analysis.append({
                "analysis": decrypt_analysis_to_json(word_dict["word"][:-2]) + 
                            decrypt_analysis_to_json("<ць>"),
                "sure": False
            })
    
    if len(analysis):
        return analysis
    
    if word_dict["part_of_speech_id"] not in [PartsOfSpeech.PRYSLOUE, PartsOfSpeech.SLUZBOVAYA]:
        postfixes = []
        basis_text = extract_word_basis(word_dict)
        ending_text = word_dict["word"][len(basis_text):]

        # if ending_text and ending_text[0] in ["ў", "ь", "'", "й"]:
        #     basis_text += ending_text[0]
        #     ending_text = ending_text[1:]
        
        analysis += decrypt_analysis_to_json(basis_text)

        if word_dict["part_of_speech_id"] == PartsOfSpeech.DZEIASLOU:
            if ending_text and ending_text[0] == "л":
                analysis += decrypt_analysis_to_json("<л>")
                ending_text = ending_text[1:]

        analysis += decrypt_analysis_to_json(f"[{ending_text}]")
        for postf in postfixes:
            analysis += decrypt_analysis_to_json(f"<{postf}>")

    else:
        analysis += decrypt_analysis_to_json(word_dict["word"])
    
    return [{"analysis": analysis, "sure": False}]


def encrypt_morphems_to_store(ms: list[Morphem], use_letters=True):
    def morphem_pretty_text(morphem: Morphem):
        mtext = morphem.text if use_letters else morphem.get_initial()
        if morphem.mtype == MorphemType.PREFIX:
            mtext = "|" + mtext + "|"
        elif morphem.mtype == MorphemType.ROOT:
            mtext = "(" + mtext + ")"
        elif morphem.mtype == MorphemType.SUFFIX:
            mtext = "<" + mtext + ">"
        elif morphem.mtype == MorphemType.ENDING:
            mtext = "[" + mtext + "]"
        return mtext
    
    return "-".join(list(map(lambda m: morphem_pretty_text(m), ms)))


def decrypt_analysis_to_json(analysis: str) -> list[dict]:
    morphems = analysis.split("-")
    result = []

    for m in morphems:
        if m == "":
            continue
        elif m[0] == "|" and m[-1] == "|":
            result.append({"type": MorphemType.PREFIX , "text": m[1:-1]})
        elif m[0] == "(" and m[-1] == ")":
            result.append({"type": MorphemType.ROOT   , "text": m[1:-1]})
        elif m[0] == "<" and m[-1] == ">":
            result.append({"type": MorphemType.SUFFIX , "text": m[1:-1]})
        elif m[0] == "[" and m[-1] == "]":
            result.append({"type": MorphemType.ENDING , "text": m[1:-1]})
        else:
            result.append({"type": MorphemType.UNKNOWN, "text": m})
            
    return result