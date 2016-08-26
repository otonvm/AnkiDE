# -*- coding: utf-8 -*-

import re
import attr
import requests


class Continue(Exception):
    pass


@attr.s
class WiktionaryParser:
    _markup = attr.ib(validator=attr.validators.instance_of(str))
    _data = attr.ib(init=False, default=attr.Factory(dict))
    _block_sequence_num = attr.ib(init=False)
    _lines = attr.ib(init=False)

    def _clean_line(self, line):
        # remove bold tags:
        line = re.sub(r"'''(.+)'''", r"\1", line)
        # remove italics:
        line = re.sub(r"''(.+)''", r"\1", line)
        # remove links:
        line = re.sub(r"\[\[([\w]+)\]\]", r"\1", line)
        # more links:
        line = re.sub(r"\[\[[^|]+\|([^\]]+)\]\]", r"\1", line)
        # footnotes:
        line = re.sub(r"<sup>\[\d+\]</sup>", "", line)
        # references:
        line = re.sub(r"<ref.+?</ref>", "", line)
        # more references:
        line = re.sub(r"<ref.+?/>", "", line)
        # cleanup multiple spaces:
        line = re.sub(r"\s\s+", " ", line)

        return line

    def basic_form(self):
        print(self._data["conjugated"])
        if self._data["conjugated"]:
            for line in self._lines:
                print(self._lines)
                match = re.match(r"^\{\{.*?\|(\w+)\}\}$", line)
                if match:
                    self._data["basic form"] = match.group(1)

    def _is_conjugated(self, line):
        if "Konjugierte Form" in line:
            self._data["conjugated"] = True

    def _find_alternative_word(self, line):
        match = re.match(r"^\{\{Siehe\sauch\|'''\[\[([\w]+)\]\]'''\}\}$", line)
        if match:
            self._data["alternative"] = match.group(1)
            raise Continue

    def _find_type_of_word(self, line):
        match = re.match(r"^===\s\{\{Wortart\|(\w+)\|Deutsch\}\}", line)
        if match:
            self._data["type"] = match.group(1)
            raise Continue

    def _find_overview_line(self, line):
        match = re.match(r"^\|([a-zA-zäöü\s*,]+)=(\w+)$", line)

        if match:
            return match.groups()
        else:
            raise Continue

    def _find_word_overview(self, line):
        if re.match(r"^\{\{Deutsch\s\w+\sÜbersicht$", line):
            self._data["overview"] = {}

            # loop until next block:
            for line in self._lines:
                if line.startswith("{{"):
                    break

                line = self._clean_line(line)

                try:
                    label, text = self._find_overview_line(line)
                except Continue:
                    continue

                self._data["overview"][label] = text

            raise Continue

    def _find_audio(self, line):
        match = re.match(r"^:\{\{Hörbeispiele\}\} \{\{Audio\|([\w\-.]+)[}|\w]+", line)
        if match:
            self._data["audio"] = match.group(1)
            raise Continue

    def _find_notes_in_meaning_line(self, line):
        match = re.match(r"^\{\{K\|([\w.|]+)\}\}\s(.*)$", line)
        if match:
            notes, rest = match.groups()
            # transform | to ,
            notes = notes.replace("|", ", ")
            return notes, rest
        else:
            return None, line

    def _find_meaning_line(self, line):
        match = re.match(r"^:\[\d+\]\s(.*)$", line)
        if match:
            self._block_sequence_num += 1
            text = match.group(1)
            notes, text = self._find_notes_in_meaning_line(text)
            return self._block_sequence_num, notes, text
        else:
            raise Continue

    def _find_word_meanings(self, line):
        if line == "{{Bedeutungen}}":
            self._data["meanings"] = {}
            self._block_sequence_num = 0

            # loop until next block:
            for line in self._lines:
                if line.startswith("{{"):
                    break

                line = self._clean_line(line)

                try:
                    number, notes, text = self._find_meaning_line(line)
                except Continue:
                    continue

                self._data["meanings"][int(number)] = (notes, text)

            raise Continue

    def _find_example_line(self, line):
        match = re.match(r"^:\[[\s\d,\]]+(.*)$", line)
        if match:
            self._block_sequence_num += 1
            return self._block_sequence_num, match.group(1)
        else:
            raise Continue

    def _find_word_examples(self, line):
        if line == "{{Beispiele}}":
            self._data["examples"] = {}
            self._block_sequence_num = 0

            # loop until next block:
            for line in self._lines:
                if line.startswith("{{"):
                    break

                line = self._clean_line(line)

                try:
                    number, text = self._find_example_line(line)
                except Continue:
                    continue

                self._data["examples"][int(number)] = text

            raise Continue

    def _find_translation_line(self, line):
        match = re.match(r"^\*\{\{en\}\}.*?\|([\w\s']+)\}\}", line)
        if match:
            return match.group(1)
        else:
            raise Continue

    def _find_word_translation(self, line):
        if line == "==== Übersetzungen ====":
            # loop until next block:
            for line in self._lines:
                if line.startswith("{{") and "Tabelle" not in line:
                    break

                line = self._clean_line(line)

                try:
                    text = self._find_translation_line(line)
                except Continue:
                    continue

                self._data["translation"] = text

            raise Continue

    def parse(self):
        self._lines = (line.strip() for line in self._markup.split("\n") if line.strip())

        for line in self._lines:
            line = self._clean_line(line)

            try:
                self._is_conjugated(line)
                self._find_alternative_word(line)
                self._find_type_of_word(line)
                self._find_word_overview(line)
                self._find_audio(line)
                self._find_word_meanings(line)
                self._find_word_examples(line)
                self._find_word_translation(line)
            except Continue:
                continue

    def data(self):
        return self._data

word = "ohrfeige"
w = WiktionaryParser(requests.get(r"https://de.wiktionary.org/wiki/{}?action=raw".format(word)).text)
w.parse()
from pprint import pprint
pprint(w.data())
print(w.basic_form())