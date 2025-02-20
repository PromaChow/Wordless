# ----------------------------------------------------------------------
# Tests: NLP - Stanza - Kyrgyz
# Copyright (C) 2018-2025  Ye Lei (叶磊)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------

from tests.tests_nlp.tests_stanza import test_stanza

def test_stanza_kir():
    test_stanza.wl_test_stanza(
        lang = 'kir',
        results_sentence_tokenize = ['Кыргыз тили — Кыргыз Республикасынын мамлекеттик тили, түрк тилдери курамына, анын ичинде кыргыз-кыпчак же тоо-алтай тобуна кирет.', 'Кыргыз Республикасынын түптүү калкынын, Кытайдагы, Өзбекстан, Тажикстан, Республикасында Ооганстан, Түркия, Орусияда жашап жаткан кыргыздардын эне тили.', '2009 ж. өткөн элди жана турак-жай фондун каттоонун жыйынтыгында Кыргыз Республикасында кыргыз тилин 3 830 556 адам өз эне тили катары көрсөтүшкөн жана 271 187 адам кыргыз тилин экинчи тил катары биле тургандыгы аныкталган[1].', 'Бул КРсындагы калктын 76% кыргыз тилинде сүйлөйт дегенди билдирет.', 'Кыргыз тилинде 1 720 693 адам орус тилин дагы билише тургандыгын көргөзүшкөн[2].', 'Бул 2 109 863 адам кыргыз тилинде гана сүйлөй билишет дегенди билдирет.', 'Болжолдуу эсеп менен дүйнө жүзү боюнча кыргыз тилинде 6 700 000 адам сүйлөйт.'],
        results_word_tokenize = ['Кыргыз', 'тили', '—', 'Кыргыз', 'Республикасынын', 'мамлекеттик', 'тили', ',', 'түрк', 'тилдеринин', 'курамына', ',', 'анын', 'ичинде', 'кыргыз-кыпчак', 'же', 'тоо-алтай', 'тобуна', 'кирет', '.'],
        results_pos_tag = [('Кыргыз', 'PROP'), ('тили', 'NN'), ('—', 'PCT'), ('Кыргыз', 'PROP'), ('Республикасынын', 'NN'), ('мамлекеттик', 'ADJ'), ('тили', 'NN'), (',', 'PCT'), ('түрк', 'PROP'), ('тилдеринин', 'NN'), ('курамына', 'NN'), (',', 'PCT'), ('анын', 'PRP'), ('ичинде', 'YADJ'), ('кыргыз-кыпчак', 'PROP'), ('же', 'ADV'), ('тоо-алтай', 'NN'), ('тобуна', 'NN'), ('кирет', 'VB'), ('.', 'PCT')],
        results_pos_tag_universal = [('Кыргыз', 'PROPN'), ('тили', 'NOUN'), ('—', 'PUNCT'), ('Кыргыз', 'PROPN'), ('Республикасынын', 'NOUN'), ('мамлекеттик', 'NOUN'), ('тили', 'NOUN'), (',', 'PUNCT'), ('түрк', 'PROPN'), ('тилдеринин', 'NOUN'), ('курамына', 'NOUN'), (',', 'PUNCT'), ('анын', 'PRON'), ('ичинде', 'ADJ'), ('кыргыз-кыпчак', 'PROPN'), ('же', 'ADV'), ('тоо-алтай', 'NOUN'), ('тобуна', 'NOUN'), ('кирет', 'VERB'), ('.', 'PUNCT')],
        results_lemmatize = ['Кыргыз', 'тили', '—', 'Кыргыз', 'Республика', 'мамлекет', 'тили', ',', 'түрк', 'тил', 'курам', ',', 'ал', 'ич', 'кыргыз-кыпчак', 'же', 'тоо-алтай', 'тобу', 'кирет', '.'],
        results_dependency_parse = [('Кыргыз', 'тили', 'nmod:poss', 1), ('тили', 'тили', 'nmod', 5), ('—', 'тили', 'punct', -1), ('Кыргыз', 'Республикасынын', 'nmod', 1), ('Республикасынын', 'тили', 'obl', 2), ('мамлекеттик', 'тили', 'amod', 1), ('тили', 'кирет', 'nmod', 12), (',', 'тили', 'punct', -1), ('түрк', 'курамына', 'nmod', 2), ('тилдеринин', 'курамына', 'nmod', 1), ('курамына', 'кирет', 'nmod', 8), (',', 'курамына', 'punct', -1), ('анын', 'ичинде', 'nmod:poss', 1), ('ичинде', 'кирет', 'obl', 5), ('кыргыз-кыпчак', 'кирет', 'nmod', 4), ('же', 'кыргыз-кыпчак', 'advmod', -1), ('тоо-алтай', 'тобуна', 'nmod', 1), ('тобуна', 'кирет', 'obl', 1), ('кирет', 'кирет', 'root', 0), ('.', 'кирет', 'punct', -1)]
    )

if __name__ == '__main__':
    test_stanza_kir()
