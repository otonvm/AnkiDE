# -*- coding: utf-8 -*-

import re
import attr
from isplit import isplit


@attr.s
class WiktionaryParser:
    _markup = attr.ib(validator=attr.validators.instance_of(str))
    _word_data = attr.ib(init=False, default=attr.Factory(dict))
    _block_sequence_num = attr.ib(init=False)
    _markup_by_line = attr.ib(init=False, default=None)

    def _clean_line(self, line):
        line = line.strip()
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

    def _ready_markup_generator(self):
        self._markup_by_line = (self._clean_line(line) for line in
                                isplit(self._markup, "\n") if line.strip())

    def _get_matches(self, pattern):
        self._ready_markup_generator()

        for line in self._markup_by_line:
            match = re.match(pattern, line)

            try:
                return match.group(1) if len(match.groups()) == 1 else match.groups()
            except AttributeError:
                continue

    def _get_matches_for_block(self, label, block_start_pattern, line_pattern):
        self._ready_markup_generator()

        self._word_data[label] = {}

        for line in self._markup_by_line:
            if re.match(block_start_pattern, line):

                for block_line in self._markup_by_line:
                    if block_line.startswith("{{"):
                        return

                    match = re.match(line_pattern, block_line)

                    try:
                        self._word_data[label][match.group(1)] = match.group(2)
                    except AttributeError:
                        continue

    def _get_numbered_matches_for_block(self, label, block_start_pattern, line_pattern, notes_pattern=None):
        self._ready_markup_generator()

        self._word_data[label] = {}

        number = 0

        for line in self._markup_by_line:
            if re.match(block_start_pattern, line):

                for block_line in self._markup_by_line:
                    if block_line.startswith("{{"):
                        return

                    number += 1

                    line_match = re.match(line_pattern, block_line)
                    if line_match:
                        if notes_pattern is not None:
                            notes_match = re.match(notes_pattern, line_match.group(1))

                            if notes_match:
                                notes, text = notes_match.groups()
                                notes = notes.replace("|", ", ")

                                self._word_data[label][number] = (notes, text)

                            else:
                                self._word_data[label][number] = (None, line_match.group(1))

                        else:
                            self._word_data[label][number] = line_match.group(1)

    def word_type(self):
        try:
            self._word_data["type"]
        except KeyError:
            self._word_data["type"] = self._get_matches(r"^===\s\{\{Wortart\|([\w\s]+)\|Deutsch\}\}")
        finally:
            return self._word_data["type"]

    def is_conjugated(self):
        return self._data["type"] == "Konjugierte Form"

    def basic_form(self):
        try:
            self._word_data["basic form"]
        except KeyError:
            self._word_data["basic form"] = self._get_matches(r"^\{\{Grundformverweis Konj\|(\w+)\}\}")
        finally:
            return self._word_data["basic form"]

    def alternative_word(self):
        try:
            self._word_data["alternative"]
        except KeyError:
            self._word_data["alternative"] = self._get_matches(r"^\{\{Siehe\sauch\|'''\[\[([\w]+)\]\]'''\}\}$")
        finally:
            return self._word_data["alternative"]

    def overview(self):
        try:
            self._word_data["overview"]
        except KeyError:
            self._get_matches_for_block(
                label="overview",
                block_start_pattern=r"^\{\{Deutsch\s\w+\sÜbersicht$",
                line_pattern=r"^\|([a-zA-zäöü\s*,]+)=(\w+)$",
            )
        finally:
            return self._word_data["overview"]

    def audio(self):
        try:
            self._word_data["audio"]
        except KeyError:
            self._word_data["audio"] = self._get_matches(r"^:\{\{Hörbeispiele\}\} \{\{Audio\|([\w\-.]+)[}|\w]+")
        finally:
            return self._word_data["audio"]

    def meanings(self):
        try:
            self._word_data["meanings"]
        except KeyError:
            self._get_numbered_matches_for_block(
                label="meanings",
                block_start_pattern=r"^\{\{Bedeutungen\}\}$",
                line_pattern=r"^:\[\d+\]\s(.*)$",
                notes_pattern=r"^\{\{K\|([\w.|]+)\}\}\s(.*)$"
            )
        finally:
            return self._word_data["meanings"]

    def examples(self):
        try:
            self._word_data["examples"]
        except KeyError:
            self._get_numbered_matches_for_block(
                label="examples",
                block_start_pattern="^\{\{Beispiele\}\}$",
                line_pattern=r"^:\[[\s\d,\]]+(.*)$"
            )
        finally:
            return self._word_data["examples"]

    def translation(self):
        try:
            self._word_data["translation"]
        except KeyError:
            self._get_matches_for_block(
                label="translation",
                block_start_pattern=r"^\{\{Ü-Tabelle\|Ü-links=$",
                line_pattern=r"^\*\{\{(en)\}\}.*?\|([\w\s']+)\}\}",
            )
        finally:
            return self._word_data["translation"]

    def word_data(self):
        return self._word_data
