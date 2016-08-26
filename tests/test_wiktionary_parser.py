# -*- coding: utf-8 -*-

import pytest
import pathlib
import pickle
from pprint import pprint

from wiktionary_parser import WiktionaryParser, Continue


@pytest.fixture(scope="module")
def markup_Haus():
    file = pathlib.Path(__file__).parent / "Haus.bin"
    with file.open("rb") as file:
        markup = pickle.load(file, encoding="utf-8")
        return (line.strip() for line in markup.split("\n") if line.strip())


def test__find_alternative_word(markup_Haus):
    w = WiktionaryParser("")
    with pytest.raises(Continue):
        for line in markup_Haus:
            w._find_alternative_word(line)
    assert w._data == {"alternative": "haus"}


def test__find_type_of_word(markup_Haus):
    w = WiktionaryParser("")
    with pytest.raises(Continue):
        for line in markup_Haus:
            w._find_type_of_word(line)
    assert w._data == {"type": "Substantiv"}


def test__parse_word_overview(markup_Haus):
    w = WiktionaryParser("")
    def lines():
        return markup_Haus
    w._lines = lines
    for line in markup_Haus:
        try:
            w._parse_word_overview(line)
        except Continue:
            break
    assert w._data == {'overview': {'Genitiv Plural': 'Häuser', 'Nominativ Plural': 'Häuser', 'Dativ Singular': 'Haus', 'Genitiv Singular': 'Hauses', 'Dativ Singular*': 'Hause', 'Akkusativ Singular': 'Haus', 'Akkusativ Plural': 'Häuser', 'Nominativ Singular': 'Haus', 'Genus': 'n', 'Dativ Plural': 'Häusern'}}


def test__find_overview_line():
    w = WiktionaryParser("")
    w._find_overview_line("|Nominativ Plural=Häuser") == ("Nominativ Plural", "Häuser")


def test__find_audio(markup_Haus):
    w = WiktionaryParser("")
    with pytest.raises(Continue):
        for line in markup_Haus:
            w._find_audio(line)
    w._data = {'audio': 'De-Haus.ogg'}


def test__find_word_meanings(markup_Haus):
    w = WiktionaryParser("")
    def lines():
        return markup_Haus
    w._lines = lines
    for line in markup_Haus:
        try:
            w._find_word_meanings(line)
        except Continue:
            break
    assert w._data == {'meanings': {1: (None, 'zu einem bestimmten Zweck erbautes Gebäude'), 2: (None, 'zum Wohnen dienendes und genutztes Gebäude'), 3: (None, 'aus mehreren Räumen bestehender, abgetrennter Bereich innerhalb eines unter beschriebenen Gebäudes, in dem sich eine oder mehrere Personen ständig aufhalten können, leben'), 4: ('ugs.', 'Gesamtheit der Bewohner in dem unter beschriebenen Gebäude'), 5: (None, 'Gesamtheit der Personen, die sich in einem bestimmten Amt, in einer bestimmten Stellung oder Tätigkeit in einem unter beschriebenen Gebäude aufhalten oder dort einer Beschäftigung nachgehen'), 6: (None, 'gesetzgebende Körperschaft der Volksvertretung'), 7: ('gehoben', 'im selben unter beschriebenen Gebäude/im selben unter beschriebenen Bereich lebende Gemeinschaft aus einem Elternpaar oder einem Elternteil samt mindestens einem Kind'), 8: (None, 'Hauswesen der unter beschriebenen Gemeinschaft'), 9: (None, 'eine Reihe von adligen (angesehenen) Persönlichkeiten, Herrschern hervorgebrachtes Geschlecht'), 10: ('ugs., scherzhaft', 'Mensch, Person'), 11: ('ugs., va., fachsprachlich, Zoologie', 'bestimmte Tiere (vor allem Weichtiere wie Gastropoden) umgebende feste, panzerartige, schützende Umhüllung'), 12: ('Astrologie, fachsprachlich', 'Tierkreiszeichen in seiner Zuordnung zu einem Planeten'), 13: ('Astrologie, fachsprachlich', 'einer der zwölf Abschnitte, in die der Tierkreis eingeteilt ist'), 14: ('Handwerk, fachsprachlich', 'mittlerer Teil eines Hammerkopfes'), 15: ('Curling, fachsprachlich', 'die drei konzentrischen Kreise, in denen Punkte erzielt werden können, die vom Kreis mit dem Radius von 6′ umschlossene Fläche')}}


def test__find_word_examples(markup_Haus):
    w = WiktionaryParser("")
    def lines():
        return markup_Haus
    w._lines = lines
    for line in markup_Haus:
        try:
            w._find_word_examples(line)
        except Continue:
            break
    assert w._data == {'examples': {1: '„‚Wir dürften in München die größte Auswahl haben‘, sind sie überzeugt und auch davon, dass ihr Haus besten Service bietet.“', 2: '„Was macht denn so ein IOC-Mitglied? Es besucht kandidierende Möchtegern-Olympiastädte. Kostenloses Reisen, Beherbergung in den nobelsten Häusern, festliche Anlässe, piekfeine Verpflegung, Geschenke (keine Bestechung versteht sich) entgegennehmen und schlussendlich eine fast unkündbare Anstellung auf Lebzeiten geniessen… Keine Frage, wer es in dieses Gremium schafft, hat ausgesorgt.“', 3: '„Bei Bedarf bekommen sie eine Brille angepasst - auf Kosten des Hauses.“', 4: '„Wer noch mehr Anwendungen will, dem stehen zusätzliche Kuren, Massagen und Spezialitäten des Hauses zur Auswahl.“', 5: '„»[…] Ich bedauere, er ist zurzeit nicht im Haus, und ich kann Ihnen leider nicht sagen, wann er wieder zurück sein wird.« »Das verstehe ich nicht. Sie wissen nicht, wo Ihr Chef ist und wann er wieder im Büro sein wird?«“', 6: 'Das Haus steht seit 1898.', 7: '„Für Wochen schloss er sich in seinem Zimmer ein und wagte kaum einen Schritt vors Haus.“', 8: '„Der Neu-Multimillionär will seinen Job behalten, aber mit der Familie (Frau, 2 Kinder) aus der kleinen Mietwohnung in ein Haus im Grünen umziehen.“', 9: 'Mein Haus wird gerade renoviert.', 10: 'Kommst du mit nach Hause?', 11: '„Das ganze Haus war auf den Kopf gestellt, die Betten ungemacht, auf dem Tisch stand eine halbgegessene Mahlzeit.“', 12: '„Ich sagte nadelspitz: »Siehst du, das hast du nun davon: ich komme nicht mit nach Haus …«“', 13: '„Das Haus ist vollständig eingerichtet, im Wohnzimmer gibt es diesen riesig großen Schreibtisch aus dunkelbraunem Holz mit einer grünen Ledereinlage auf der Oberfläche.“', 14: '„Unser Haus versammelte sich im Betsale.“', 15: 'Er ist durchaus in der Lage, ein großes Haus zu leiten.', 16: '„Befürchtete etwa Thomas Mann, daß der Schwiegersohn und Nachfolger Samuel Fischers, der seit 1928 als Geschäftsführer des berühmten Verlages tätige Gottfried Bermann Fischer ihn, den in den Jahren der Emigration (und natürlich auch später) prominentesten Autor des Hauses schlechterdings übervorteilen wollte? Aber sicher.“', 17: '„Angeblich wurde sie vom Geheimdienst MIT geführt, beteiligt waren nach Angaben des türkischen Außenministers Mevlüt auch sein Haus sowie die türkische Armee.“', 18: '„Binnen weniger Stunden entschärften beide Häuser des Parlaments einen umstrittenen Artikel und stärkten so die Demokratie.“', 19: 'Dies ist ein ehrenwertes Haus.', 20: 'Sie kam aus gutem Hause.', 21: "„Ein höherer Kanzleibeamter des Hauses'' Hochstätter tritt ein, eine würdige Erscheinung, der Zuverlässigkeit mit Gewandtheit verbindet. Er wendet sich zwar respektvoll, aber doch bestimmt an den Sohn des ''Hauses: Der Herr Vater läßt zur Unterschrift bitten, Herr Felix.“", 22: '„»Den Gang einer Mutter« nannte sie etwas pathetisch ihren Besuch, der den Nebenzweck hatte, Ulrich wieder für ihr Haus zu gewinnen, nachdem er in der Parallelaktion, wie man hörte, so große Erfolge hatte.“', 23: '„Als sie die schmale Kost verzehrt hatten, legten sie sich zu Bett: aber am Morgen trieb er sie schon ganz früh heraus, weil sie das Haus besorgen sollte.“', 24: '„Sie brachte eine schöne Mitgift ins Haus und hinterließ ihrem Mann, kaum dass 1793 der einzige Sohn Karl August geboren war, bei ihrem frühen Tod Anno 1794 ein reiches Vermögen.“', 25: 'Man sieht es ihm nicht an, aber er kommt aus einem königlichen Haus.', 26: '„Ist er wirklich der Prinz aus regierendem Hause, den ruchlose Verwandte in der Wildnis ausgesetzt haben?“', 27: '„Eigentlich wollen sie nur zeigen, was für gelehrte, gescheite Häuser, für geistreiche Köpfe, für enorme Könner sie sind.“', 28: '„Es war ein hochgelehrtes Haus, berühmt als Orgelspieler und stets etwas stutzerhaft gekleidet mit Cut und gestreifter Hose.“', 29: '„Herr Müller-Andreä jedoch lebt, er ist sogar obenauf, ein flottes Haus, eine fidele Nummer.“', 30: '„Sonst war der Koch ja ein patentes Haus.“', 31: '„Die ältere Tochter vom Hauptmann, sie war wohl fast dreißig, war ein lustiges Haus.“', 32: '„Sie, die sonst ein fideles Haus war, haderte mit allen Menschen, die es eigentlich gut mit ihr meinten.“', 33: 'Die Schnecke trägt ihr Haus mit sich.', 34: '„Zur ersten Stufe gehörte die Kauri, Cypraea moneta; zur zweiten Stufe ein rund geschliffenes, durchbohrtes Muschelkügelchen; zur dritten Stufe zylinderförmiger Purpurwampum und das langgezogene Gehäuse des Cerithium muscarium, und zur vierten das ebenfalls gewundene Haus der Vivipara georgiana, einer Süßwasserschnecke, dazu kleine Hirschhornstücke, die halb rot halb grün gefärbt sind.“', 35: '„Für die Beschäftigung Jonathan Leverkühns mit der Naturwissenschaft werden im Roman zwölf Beispiele gegeben: das Blaulicht auf den Falterflügeln mit der Frage, ob das Himmelblau Trug sei, der Glasflügler Haetera Esmeralda, der Blattschmetterling, der sich seiner Umgebeung anpaßt und daher nicht sichtbar ist, der Schmetterling, der durch Schönheit und Ungenießbarkeit gekennzeichnet ist, die Nachahmung dessen durch einen weiteren Schmetterling, der den Betrachter täuscht, das Haus der Schnecken und Muscheln, die schöne, aber giftige Kegelschnecke, die Strich-Ornamentik auf den Schneckenhäusern, die sichtbare Musik, die Eisblumen, der fressende Tropfen und die toten Gewächse der Kristalle.“', 36: '„Die Häuser der Meeresschnecken wurden bei wichtigen Zeremonien wie Fanfaren eingesetzt.“', 37: "„ Es bestehen systematische Analogien zwischen Planeten, Zeichen, Häusern'' und Winkelbeziehungen: Jedes ''Haus ist beispielsweise einem Tierkreiszeichen zugeordnet.“", 38: 'Jedes der zwölf astrologischen Häuser entspricht einem bestimmten Bereich des alltäglichen Lebens, auf denen die Energie eines Planeten zum Ausdruck kommt.', 39: '„Ausgehend vom Aszendenten und den zwei Hauptachsen, werden nun die zwölf astrologischen Häuser berechnet.“', 40: '„Hammer mit verbreiterter, stumpfer Finne, hohem, unregelmäßig ausgewölbtem Haus und schlankem Hammerteil mit gestauchter Bahn.“', 41: '„Der alte Nagelstock, an dem die Nägel nicht wie üblich mit dem Haus des Hammers eingeschlagen werden, sondern zur Erschwernis mit der Finne, also mit der schmalen Seite des Hammers, war bereits voll mit Nägeln.“', 42: '„Pro Stein, der näher zur Mitte des Hauses liegt als der Stein des Gegners, gibt es einen Punkt.“', 43: '„Während beim Curling in ein Haus gespielt wird, visiert der Eisstockschütze die so genannte Daube an, die aus Gummi besteht und deren Durchmesser knapp acht Zentimeter beträgt.“', 44: '„Im Curling gilt es, den Stein ins Haus zu schieben – deshalb gelten erfolgreiche Curler als «häusliche Typen».“', 45: '„Viertes End im Finale der 18. Internationalen Herb-Lackhoff-Trophy: Der letzte rote Stein von Skip Uwe Saile passt, bleibt wie berechnet im Haus liegen und bringt den Curling Club Mannheim gegenüber dem Team Solothurn I mit 4:3 in Führung.“', 46: '„Da Curling immer abwechselnd von einer auf die andere Seite gespielt wird, gibt es pro Rink zwei Häuser.“'}}

def test___find_translation_line():
    w = WiktionaryParser("")
    word = w._find_translation_line("*{{en}}: [1, 2, 4, 6, 9, 12, 13, 15] {{Ü|en|house}};")
    assert word == "house"

def test__find_word_translation(markup_Haus):
    w = WiktionaryParser("")
    def lines():
        return markup_Haus
    w._lines = lines
    for line in markup_Haus:
        try:
            w._find_word_translation(line)
        except Continue:
            break
    assert w._data == {"translation": "house"}