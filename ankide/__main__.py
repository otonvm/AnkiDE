#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Usage:
    test_doc -h | --help
    test_doc -V | --version
    test_doc [-o FILE] <word>

Options:
    -o FILE   --output=FILE     Path to .csv file [$HOME/Dropbox/words.csv].
    -h        --help            Show this screen.
    -V        --version         Show program version.

Arguments:
    <verb>     Verb to translate.
"""

import sys
import csv
import pathlib
import configparser
import docopt
from microsofttranslator import Translator
from .wiktionary_parser import parse_word, WordNotFoundError

__version__ = 1.2

KEY = pathlib.Path(__file__).parent / "key.ini"


def bing_translator(word):
    config = configparser.ConfigParser()

    with KEY.open("r") as key:
        config.read_file(key)
        bing_id = config.get("KEY", "id")
        bing_secret = config.get("KEY", "secret")

    translator = Translator(bing_id, bing_secret)

    return translator.translate(word, to_lang="en", from_lang="de")


def get_translation(wiktionary_object, word):
    try:
        return wiktionary_object.translation()["en"]
    except KeyError:
        return bing_translator(word)


def prompt(string, valid_responses):
    answer = input(string).strip().lower()

    if answer in valid_responses:
        return answer
    else:
        prompt(string, valid_responses)


def write_file(file, data_list):
    with file.open("a", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile, dialect=csv.excel_tab)
        writer.writerow(data_list)


def parse_args():
    args = docopt.docopt(__doc__, version=__version__, options_first=True)

    options = {}

    if not args["-o"]:
        options["output"] = pathlib.Path.home() / "Dropbox" / "words.csv"
    else:
        options["output"] = pathlib.Path(args["-o"]).expanduser().absolute()

    options["word"] = args["<word>"]

    return options


def main():
    options = parse_args()

    print("Looking for word: {}".format(options["word"]), flush=True)

    chosen_word = options["word"]

    try:
        wiktionary = parse_word(chosen_word)
    except WordNotFoundError:
        translation = bing_translator(options["word"])
        print("Could not find word {}! It could mean >>{}<<.".format(
            chosen_word,
            translation
        ), flush=True, file=sys.stderr)

        print(flush=True)
        answer = prompt("Add word to file? [Y/n] ", "yn")

        if answer == "y" or not answer:
            write_file(
                options["output"],
                [
                    chosen_word,
                    translation,
                    None, None, None, None, None, None, None,
                ]
            )
        raise SystemExit(1)

    if wiktionary.is_conjugated():
        new_word = wiktionary.basic_form()
        print("Word {} is in conjugated form, trying {} instead...".format(chosen_word, new_word), flush=True)

        try:
            wiktionary = parse_word(new_word)
            chosen_word = new_word
        except WordNotFoundError:
            print("Could not find word {}! Please try again!".format(new_word), flush=True, file=sys.stderr)
            raise SystemExit(1)

    elif wiktionary.is_a_declension():
        new_word = wiktionary.basic_form()
        print("Word {} is a declension, trying {} instead...".format(options["word"], new_word), flush=True)

        try:
            wiktionary = parse_word(new_word)
            chosen_word = new_word
        except WordNotFoundError:
            print("Could not find word {}! Please try again!".format(new_word), flush=True, file=sys.stderr)
            raise SystemExit(1)

    elif wiktionary.is_partizip_ii():
        new_word = wiktionary.basic_form()
        print("Word {} is in partizip II form, trying {} instead...".format(options["word"], new_word), flush=True)

        try:
            wiktionary = parse_word(new_word)
            chosen_word = new_word
        except WordNotFoundError:
            print("Could not find word {}! Please try again!".format(new_word), flush=True, file=sys.stderr)
            raise SystemExit(1)

    print("Word type: {}".format(wiktionary.word_type()), flush=True)

    data = []

    if wiktionary.word_type() == "Substantiv":
        overview = wiktionary.overview()

        if overview["Genus"] == "m":
            genus = "der"
        elif overview["Genus"] == "f":
            genus = "die"
        else:
            genus = "das"

        print("Basic form: {} {}".format(genus, overview["Nominativ Singular"]))

        translation = get_translation(wiktionary, overview["Nominativ Singular"])
        print("Translation: {}".format(translation), flush=True)

        print("Plural: {}".format(overview["Nominativ Plural"]), flush=True)

        print("Genitiv: {}".format(overview["Genitiv Singular"]), flush=True)

        print("Dativ: {}".format(overview["Dativ Singular"]), flush=True)

        print("Akkusativ: {}".format(overview["Akkusativ Singular"]), flush=True)

        data = [
            overview["Nominativ Singular"],
            "{} {}".format(genus, overview["Nominativ Singular"]),
            translation,
            overview["Nominativ Plural"],
            overview["Genitiv Singular"],
            overview["Dativ Singular"],
            overview["Akkusativ Singular"],
            None,
            None
        ]

    elif wiktionary.word_type() == "Verb":
        overview = wiktionary.overview()

        translation = get_translation(wiktionary, overview["Präsens_ich"])
        print("Translation: {}".format(translation), flush=True)

        print("Präsens (ich): {}".format(overview["Präsens_ich"]), flush=True)

        print("Präsens (du): {}".format(overview["Präsens_du"]), flush=True)

        print("Präteritum (ich): {}".format(overview["Präteritum_ich"]), flush=True)

        print("Partizip II: {}".format(overview["Partizip II"]), flush=True)

        print("Imperativ: {}".format(overview["Imperativ Singular"]), flush=True)

        print("Hilfsverb: {}".format(overview["Hilfsverb"]), flush=True)

        data = [
            chosen_word,
            translation,
            overview["Präsens_ich"],
            overview["Präsens_du"],
            overview["Präteritum_ich"],
            overview["Partizip II"],
            overview["Imperativ Singular"],
            overview["Hilfsverb"],
            None
        ]

    elif wiktionary.word_type() == "Adjektiv":
        overview = wiktionary.overview()

        translation = get_translation(wiktionary, chosen_word)
        print("Translation: {}".format(translation), flush=True)

        print("Komparativ: {}".format(overview.get("Komparativ", None)), flush=True)

        print("Superlativ: {}".format(overview.get("Superlativ", None)), flush=True)

        print("Beispiele: {}".format(wiktionary.examples()), flush=True)

        data = [
            chosen_word,
            translation,
            overview.get("Komparativ", None),
            overview.get("Superlativ", None),
            wiktionary.examples().get(1, None),
            wiktionary.examples().get(2, None),
            wiktionary.examples().get(3, None),
            None,
            None
        ]

    elif wiktionary.word_type() == "Adverb":
        translation = get_translation(wiktionary, chosen_word)
        print("Translation: {}".format(translation), flush=True)

        example = wiktionary.meanings().get(1, None)
        if example is not None:
            if example[0] is not None:
                example = "<i>{}</i> {}".format(example)
            else:
                example = example[1]
        print("Bedeutungen: {}".format(example), flush=True)

        print("Synonyme: {}".format(wiktionary.synonyms()[1]), flush=True)

        print("Beispiele: {}".format(wiktionary.examples()[1]), flush=True)

        data = [
            chosen_word,
            translation,
            example,
            wiktionary.synonyms().get(1, None),
            wiktionary.examples().get(1, None),
            wiktionary.examples().get(2, None),
            wiktionary.examples().get(3, None),
            None,
            None
        ]

    elif wiktionary.word_type() == "Pronominaladverb":
        translation = get_translation(wiktionary, chosen_word)
        print("Translation: {}".format(translation), flush=True)

        example = wiktionary.meanings().get(1, None)
        if example is not None:
            if example[0] is not None:
                example = "<i>{}</i> {}".format(example)
            else:
                example = example[1]
        print("Bedeutungen: {}".format(example), flush=True)

        print("Synonyme: {}".format(wiktionary.synonyms()[1]), flush=True)

        print("Beispiele: {}".format(wiktionary.examples()[1]), flush=True)

        data = [
            chosen_word,
            translation,
            example,
            wiktionary.synonyms().get(1, None),
            wiktionary.examples().get(1, None),
            wiktionary.examples().get(2, None),
            wiktionary.examples().get(3, None),
            None,
            None
        ]

    elif wiktionary.word_type() == "Konjunktion":
        translation = get_translation(wiktionary, chosen_word)
        print("Translation: {}".format(translation), flush=True)

        example = wiktionary.meanings().get(1, None)
        if example is not None:
            if example[0] is not None:
                example = "<i>{}</i> {}".format(example)
            else:
                example = example[1]
        print("Bedeutungen: {}".format(example), flush=True)

        print("Synonyme: {}".format(wiktionary.synonyms()), flush=True)

        print("Beispiele: {}".format(wiktionary.examples()[1]), flush=True)

        data = [
            chosen_word,
            translation,
            example,
            wiktionary.synonyms().get(1, None),
            wiktionary.examples().get(1, None),
            wiktionary.examples().get(2, None),
            wiktionary.examples().get(3, None),
            None,
            None
        ]

    elif wiktionary.word_type() == "Indefinitpronomen":
        translation = get_translation(wiktionary, chosen_word)
        print("Translation: {}".format(translation), flush=True)

        example = wiktionary.meanings().get(1, None)
        if example is not None:
            if example[0] is not None:
                example = "<i>{}</i> {}".format(example)
            else:
                example = example[1]
        print("Bedeutungen: {}".format(example), flush=True)

        print("Synonyme: {}".format(wiktionary.synonyms()), flush=True)

        print("Beispiele: {}".format(wiktionary.examples()[1]), flush=True)

        data = [
            chosen_word,
            translation,
            example,
            wiktionary.synonyms().get(1, None),
            wiktionary.examples().get(1, None),
            wiktionary.examples().get(2, None),
            wiktionary.examples().get(3, None),
            None,
            None
        ]

    elif wiktionary.word_type() == "Subjunktion":
        translation = get_translation(wiktionary, chosen_word)
        print("Translation: {}".format(translation), flush=True)

        example = wiktionary.meanings().get(1, None)
        if example is not None:
            if example[0] is not None:
                example = "<i>{}</i> {}".format(example)
            else:
                example = example[1]
        print("Bedeutungen: {}".format(example), flush=True)

        print("Synonyme: {}".format(wiktionary.synonyms()), flush=True)

        print("Beispiele: {}".format(wiktionary.examples()[1]), flush=True)

        data = [
            chosen_word,
            translation,
            example,
            wiktionary.synonyms().get(1, None),
            wiktionary.examples().get(1, None),
            wiktionary.examples().get(2, None),
            wiktionary.examples().get(3, None),
            None,
            None
        ]

    else:
        print("No additional information is available!", flush=True)
        raise SystemExit(1)

    print(flush=True)
    answer = prompt("Add word to file? [Y/n] ", "yn")

    if answer == "y" or not answer:
        write_file(options["output"], data)


if __name__ == "__main__":
    main()
