# ----------------------------------------------------------------------
# Tests: NLP - spaCy - Greek
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

from tests.tests_nlp.tests_spacy import test_spacy

def test_spacy_ell():
    results_pos_tag = [('Η', 'DET'), ('ελληνική', 'ADJ'), ('γλώσσα', 'NOUN'), ('ανήκει', 'VERB'), ('στην', 'ADP'), ('ινδοευρωπαϊκή', 'ADJ'), ('οικογένεια[9', 'NOUN'), (']', 'NOUN'), ('και', 'CCONJ'), ('αποτελεί', 'VERB'), ('το', 'DET'), ('μοναδικό', 'ADJ'), ('μέλος', 'NOUN'), ('του', 'DET'), ('ελληνικού', 'ADJ'), ('κλάδου', 'NOUN'), (',', 'PUNCT'), ('ενώ', 'SCONJ'), ('είναι', 'AUX'), ('η', 'DET'), ('επίσημη', 'ADJ'), ('γλώσσα', 'NOUN'), ('της', 'DET'), ('Ελλάδας', 'PROPN'), ('και', 'CCONJ'), ('της', 'DET'), ('Κύπρου', 'PROPN'), ('.', 'PUNCT')]

    test_spacy.wl_test_spacy(
        lang = 'ell',
        results_sentence_tokenize_trf = ['Η ελληνική γλώσσα ανήκει στην ινδοευρωπαϊκή οικογένεια[9] και αποτελεί το μοναδικό μέλος του ελληνικού κλάδου, ενώ είναι η επίσημη γλώσσα της Ελλάδας και της Κύπρου.', 'Ανήκει επίσης στο βαλκανικό γλωσσικό δεσμό.', 'Στην ελληνική γλώσσα, έχουμε γραπτά κείμενα ήδη από τον 15ο αιώνα π.', 'Χ..', 'Σαν Παγκόσμια Ημέρα Ελληνικής Γλώσσας, κάθε έτος, έχει καθιερωθεί η 9η Φεβρουαρίου.', 'Έχει την μακροβιότερη καταγεγραμμένη ιστορία από οποιαδήποτε άλλη ζωντανή ινδοευρωπαϊκή γλώσσα με τουλάχιστον 3.400 χρόνια γραπτής ιστορίας.[10]', 'Γράφεται με το ελληνικό αλφάβητο, το οποίο χρησιμοποιείται αδιάκοπα (αρχικά με τοπικές παραλλαγές, μετέπειτα υπό μια, ενιαία μορφή) εδώ και περίπου 2.600 χρόνια.[11][12]', 'Προηγουμένως η ελληνική γλώσσα γραφόταν με τη Γραμμική Β και το κυπριακό συλλαβάριο.[13]', 'Το ελληνικό αλφάβητο προέρχεται από το φοινικικό αλφάβητο, με κάποιες προσαρμογές.', 'Στο ελληνικό αλφάβητο βασίζεται το λατινικό, το κυριλλικό, το αρμενικό, το κοπτικό, το γοτθικό και πολλά άλλα αλφάβητα.'],
        results_sentence_tokenize_lg = ['Η ελληνική γλώσσα ανήκει στην ινδοευρωπαϊκή οικογένεια[9] και αποτελεί το μοναδικό μέλος του ελληνικού κλάδου, ενώ είναι η επίσημη γλώσσα της Ελλάδας και της Κύπρου.', 'Ανήκει επίσης στο βαλκανικό γλωσσικό δεσμό.', 'Στην ελληνική γλώσσα, έχουμε γραπτά κείμενα ήδη από τον 15ο αιώνα π.', 'Χ.. Σαν Παγκόσμια Ημέρα Ελληνικής Γλώσσας, κάθε έτος, έχει καθιερωθεί η 9η Φεβρουαρίου.', 'Έχει την μακροβιότερη καταγεγραμμένη ιστορία από οποιαδήποτε άλλη ζωντανή ινδοευρωπαϊκή γλώσσα με τουλάχιστον 3.400 χρόνια γραπτής ιστορίας.[10] Γράφεται με το ελληνικό αλφάβητο, το οποίο χρησιμοποιείται αδιάκοπα (αρχικά με τοπικές παραλλαγές, μετέπειτα υπό μια, ενιαία μορφή) εδώ και περίπου 2.600 χρόνια.[11][12] Προηγουμένως η ελληνική γλώσσα γραφόταν με τη Γραμμική Β και το κυπριακό συλλαβάριο.[13]', 'Το ελληνικό αλφάβητο προέρχεται από το φοινικικό αλφάβητο, με κάποιες προσαρμογές.', 'Στο ελληνικό αλφάβητο βασίζεται το λατινικό, το κυριλλικό, το αρμενικό, το κοπτικό, το γοτθικό και πολλά άλλα αλφάβητα.'],
        results_word_tokenize = ['Η', 'ελληνική', 'γλώσσα', 'ανήκει', 'στην', 'ινδοευρωπαϊκή', 'οικογένεια[9', ']', 'και', 'αποτελεί', 'το', 'μοναδικό', 'μέλος', 'του', 'ελληνικού', 'κλάδου', ',', 'ενώ', 'είναι', 'η', 'επίσημη', 'γλώσσα', 'της', 'Ελλάδας', 'και', 'της', 'Κύπρου', '.'],
        results_pos_tag = results_pos_tag,
        results_pos_tag_universal = results_pos_tag,
        results_lemmatize = ['ο', 'ελληνικός', 'γλώσσα', 'ανήκω', 'σε ο', 'ινδοευρωπαϊκός', 'οικογένεια[9', ']', 'και', 'αποτελώ', 'ο', 'μοναδικός', 'μέλος', 'ο', 'ελληνικός', 'κλάδος', ',', 'ενώ', 'είμαι', 'ο', 'επίσημος', 'γλώσσα', 'ο', 'Ελλάδα', 'και', 'ο', 'Κύπρος', '.'],
        results_dependency_parse = [('Η', 'γλώσσα', 'det', 2), ('ελληνική', 'γλώσσα', 'amod', 1), ('γλώσσα', 'ανήκει', 'nsubj', 1), ('ανήκει', 'ανήκει', 'ROOT', 0), ('στην', 'οικογένεια[9', 'case', 2), ('ινδοευρωπαϊκή', 'οικογένεια[9', 'amod', 1), ('οικογένεια[9', 'ανήκει', 'obl', -3), (']', 'οικογένεια[9', 'nmod', -1), ('και', 'αποτελεί', 'cc', 1), ('αποτελεί', 'ανήκει', 'conj', -6), ('το', 'μέλος', 'det', 2), ('μοναδικό', 'μέλος', 'amod', 1), ('μέλος', 'αποτελεί', 'obj', -3), ('του', 'κλάδου', 'det', 2), ('ελληνικού', 'κλάδου', 'amod', 1), ('κλάδου', 'μέλος', 'nmod', -3), (',', 'γλώσσα', 'punct', 5), ('ενώ', 'γλώσσα', 'mark', 4), ('είναι', 'γλώσσα', 'cop', 3), ('η', 'γλώσσα', 'det', 2), ('επίσημη', 'γλώσσα', 'amod', 1), ('γλώσσα', 'ανήκει', 'conj', -18), ('της', 'Ελλάδας', 'det', 1), ('Ελλάδας', 'γλώσσα', 'nmod', -2), ('και', 'Κύπρου', 'cc', 2), ('της', 'Κύπρου', 'det', 1), ('Κύπρου', 'Ελλάδας', 'conj', -3), ('.', 'ανήκει', 'punct', -24)]
    )

if __name__ == '__main__':
    test_spacy_ell()
