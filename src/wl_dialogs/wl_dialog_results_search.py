#
# Wordless: Dialogs - Search in Results
#
# Copyright (C) 2018-2021  Ye Lei (叶磊)
#
# This source file is licensed under GNU GPLv3.
# For details, see: https://github.com/BLKSerene/Wordless/blob/master/LICENSE.txt
#
# All other rights reserved.
#

import copy
import platform
import time

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import nltk

from wl_dialogs import wl_dialog, wl_dialog_misc, wl_msg_box
from wl_text import wl_matching
from wl_widgets import wl_button, wl_layout, wl_msg, wl_widgets
from wl_utils import wl_misc, wl_threading

class Wl_Worker_Results_Search(wl_threading.Wl_Worker):
    def run(self):
        for table in self.dialog.tables:
            results = {}
            search_terms = set()

            for col in range(table.columnCount()):
                if table.cellWidget(0, col):
                    for row in range(table.rowCount()):
                        results[(row, col)] = table.cellWidget(row, col).text_search
                else:
                    for row in range(table.rowCount()):
                        try:
                            results[(row, col)] = table.item(row, col).text_raw
                        except:
                            results[(row, col)] = [table.item(row, col).text()]

            items = [token for text in results.values() for token in text]

            for file in table.settings['files']['files_open']:
                if file['selected']:
                    search_terms_file = wl_matching.match_search_terms(
                        self.main, items,
                        lang = file['lang'],
                        tokenized = file['tokenized'],
                        tagged = file['tagged'],
                        token_settings = table.settings[self.dialog.tab]['token_settings'],
                        search_settings = self.dialog.settings)

                    search_terms |= set(search_terms_file)

            for search_term in search_terms:
                len_search_term = len(search_term)

                for (row, col), text in results.items():
                    for ngram in nltk.ngrams(text, len_search_term):
                        if ngram == search_term:
                            self.dialog.items_found.append([table, row, col])

        self.dialog.items_found = sorted(
            self.dialog.items_found,
            key = lambda item: (id(item[0]), item[1], item[2])
        )

        self.progress_updated.emit(self.tr('Highlighting items ...'))

        time.sleep(0.1)

        self.worker_done.emit()

class Wl_Dialog_Results_Search(wl_dialog.Wl_Dialog):
    def __init__(self, main, tab, table):
        super().__init__(main, main.tr('Search in Results'))

        self.tab = tab
        self.tables = [table]
        self.settings = self.main.settings_custom[self.tab]['search_results']
        self.items_found = []

        (self.label_search_term,
         self.checkbox_multi_search_mode,

         self.stacked_widget_search_term,
         self.line_edit_search_term,
         self.list_search_terms,

         self.label_separator,

         self.checkbox_ignore_case,
         self.checkbox_match_inflected_forms,
         self.checkbox_match_whole_words,
         self.checkbox_use_regex,

         self.checkbox_ignore_tags,
         self.checkbox_match_tags) = wl_widgets.wl_widgets_search_settings(self, self.tab)

        self.button_find_next = QPushButton(self.tr('Find Next'), self)
        self.button_find_prev = QPushButton(self.tr('Find Previous'), self)
        self.button_find_all = QPushButton(self.tr('Find All'), self)
        
        self.button_reset_settings = wl_button.Wl_Button_Reset_Settings(self)
        self.button_clear_hightlights = QPushButton(self.tr('Clear Highlights'), self)
        self.button_close = QPushButton(self.tr('Close'), self)

        self.button_reset_settings.setFixedWidth(130)
        self.button_close.setFixedWidth(80)

        self.checkbox_multi_search_mode.stateChanged.connect(self.search_settings_changed)
        self.line_edit_search_term.textChanged.connect(self.search_settings_changed)
        self.line_edit_search_term.returnPressed.connect(self.button_find_next.click)
        self.list_search_terms.itemChanged.connect(self.search_settings_changed)

        self.checkbox_ignore_case.stateChanged.connect(self.search_settings_changed)
        self.checkbox_match_inflected_forms.stateChanged.connect(self.search_settings_changed)
        self.checkbox_match_whole_words.stateChanged.connect(self.search_settings_changed)
        self.checkbox_use_regex.stateChanged.connect(self.search_settings_changed)

        self.checkbox_ignore_tags.stateChanged.connect(self.search_settings_changed)
        self.checkbox_match_tags.stateChanged.connect(self.search_settings_changed)

        self.button_find_next.clicked.connect(lambda: self.find_next())
        self.button_find_prev.clicked.connect(lambda: self.find_prev())
        self.button_find_all.clicked.connect(lambda: self.find_all())

        self.button_clear_hightlights.clicked.connect(self.clear_highlights)
        self.button_close.clicked.connect(self.reject)

        layout_buttons_right = wl_layout.Wl_Layout()
        layout_buttons_right.addWidget(self.button_find_next, 0, 0)
        layout_buttons_right.addWidget(self.button_find_prev, 1, 0)
        layout_buttons_right.addWidget(self.button_find_all, 2, 0)
        layout_buttons_right.addWidget(self.button_clear_hightlights, 3, 0)

        layout_buttons_right.setRowStretch(4, 1)

        layout_buttons_bottom = wl_layout.Wl_Layout()
        layout_buttons_bottom.addWidget(self.button_reset_settings, 0, 0)
        layout_buttons_bottom.addWidget(self.button_close, 0, 1, Qt.AlignRight)

        self.setLayout(wl_layout.Wl_Layout())
        self.layout().addWidget(self.label_search_term, 0, 0)
        self.layout().addWidget(self.checkbox_multi_search_mode, 0, 1, Qt.AlignRight)
        self.layout().addWidget(self.stacked_widget_search_term, 1, 0, 1, 2)
        self.layout().addWidget(self.label_separator, 2, 0, 1, 2)

        self.layout().addWidget(self.checkbox_ignore_case, 3, 0, 1, 2)
        self.layout().addWidget(self.checkbox_match_inflected_forms, 4, 0, 1, 2)
        self.layout().addWidget(self.checkbox_match_whole_words, 5, 0, 1, 2)
        self.layout().addWidget(self.checkbox_use_regex, 6, 0, 1, 2)

        self.layout().addWidget(self.checkbox_ignore_tags, 7, 0, 1, 2)
        self.layout().addWidget(self.checkbox_match_tags, 8, 0, 1, 2)

        self.layout().addWidget(wl_layout.Wl_Separator(self, orientation = 'Vertical'), 0, 2, 9, 1)

        self.layout().addLayout(layout_buttons_right, 0, 3, 9, 1)

        self.layout().addWidget(wl_layout.Wl_Separator(self), 9, 0, 1, 4)

        self.layout().addLayout(layout_buttons_bottom, 10, 0, 1, 4)

        self.main.wl_work_area.currentChanged.connect(self.reject)

        self.load_settings()

    def load_settings(self, defaults = False):
        if defaults:
            settings = copy.deepcopy(self.main.settings_default[self.tab]['search_results'])
        else:
            settings = copy.deepcopy(self.settings)

        self.checkbox_multi_search_mode.setChecked(settings['multi_search_mode'])

        if not defaults:
            self.line_edit_search_term.setText(settings['search_term'])
            self.list_search_terms.load_items(settings['search_terms'])

        self.checkbox_ignore_case.setChecked(settings['ignore_case'])
        self.checkbox_match_inflected_forms.setChecked(settings['match_inflected_forms'])
        self.checkbox_match_whole_words.setChecked(settings['match_whole_words'])
        self.checkbox_use_regex.setChecked(settings['use_regex'])

        self.checkbox_ignore_tags.setChecked(settings['ignore_tags'])
        self.checkbox_match_tags.setChecked(settings['match_tags'])

        self.search_settings_changed()

    def search_settings_changed(self):
        self.settings['multi_search_mode'] = self.checkbox_multi_search_mode.isChecked()
        self.settings['search_term'] = self.line_edit_search_term.text()
        self.settings['search_terms'] = self.list_search_terms.get_items()

        self.settings['ignore_case'] = self.checkbox_ignore_case.isChecked()
        self.settings['match_inflected_forms'] = self.checkbox_match_inflected_forms.isChecked()
        self.settings['match_whole_words'] = self.checkbox_match_whole_words.isChecked()
        self.settings['use_regex'] = self.checkbox_use_regex.isChecked()

        self.settings['ignore_tags'] = self.checkbox_ignore_tags.isChecked()
        self.settings['match_tags'] = self.checkbox_match_tags.isChecked()

        if 'size_multi' in self.__dict__:
            if self.settings['multi_search_mode']:
                self.setFixedSize(self.size_multi)
            else:
                self.setFixedSize(self.size_normal)

    @wl_misc.log_timing
    def find_next(self):
        self.find_all()

        if self.items_found:
            selected_rows = []

            for table in self.tables:
                table.hide()
                table.blockSignals(True)
                table.setUpdatesEnabled(False)

            for table in self.tables:
                if table.get_selected_rows():
                    selected_rows = [id(table), table.get_selected_rows()]

                    break

            # Scroll to the next found item
            if selected_rows:
                for table in self.tables:
                    table.clearSelection()

                for table, row, _ in self.items_found:
                    # Tables are sorted by their string representations
                    if (id(table) > selected_rows[0] or
                        id(table) == selected_rows[0] and row > selected_rows[1][-1]):
                        table.selectRow(row)
                        table.setFocus()

                        table.scrollToItem(table.item(row, 0))

                        break

                # Scroll to top if this is the last item
                if not any([table.selectedItems() for table in self.tables]):
                    self.tables[0].scrollToItem(table.item(self.items_found[0][1], 0))
                    self.tables[0].selectRow(self.items_found[0][1])
            else:
                self.tables[0].scrollToItem(table.item(self.items_found[0][1], 0))
                self.tables[0].selectRow(self.items_found[0][1])

            for table in self.tables:
                table.blockSignals(False)
                table.setUpdatesEnabled(True)
                table.show()

    @wl_misc.log_timing
    def find_prev(self):
        self.find_all()

        if self.items_found:
            selected_rows = []

            for table in self.tables:
                table.hide()
                table.blockSignals(True)
                table.setUpdatesEnabled(False)

            for table in self.tables:
                if table.get_selected_rows():
                    selected_rows = [id(table), table.get_selected_rows()]

                    break

            # Scroll to the previous found item
            if selected_rows:
                for table in self.tables:
                    table.clearSelection()

                for table, row, _ in reversed(self.items_found):
                    # Tables are sorted by their string representations
                    if (id(table) < selected_rows[0] or
                        id(table) == selected_rows[0] and row < selected_rows[1][-1]):
                        table.selectRow(row)
                        table.setFocus()

                        table.scrollToItem(table.item(row, 0))

                        break

                # Scroll to bottom if this is the first item
                if not any([table.selectedItems() for table in self.tables]):
                    self.tables[-1].scrollToItem(table.item(self.items_found[-1][1], 0))
                    self.tables[-1].selectRow(self.items_found[-1][1])
            else:
                self.tables[-1].scrollToItem(table.item(self.items_found[-1][1], 0))
                self.tables[-1].selectRow(self.items_found[-1][1])

            for table in self.tables:
                table.blockSignals(False)
                table.setUpdatesEnabled(True)
                table.show()

    @wl_misc.log_timing
    def find_all(self):
        def update_gui():
            if self.items_found:
                for table in self.tables:
                    table.hide()
                    table.blockSignals(True)
                    table.setUpdatesEnabled(False)

                for table, row, col in self.items_found:
                    if table.cellWidget(row, col):
                        table.cellWidget(row, col).setStyleSheet('border: 1px solid #E53E3A;')
                    else:
                        table.item(row, col).setForeground(QBrush(QColor('#FFF')))
                        table.item(row, col).setBackground(QBrush(QColor('#E53E3A')))

                for table in self.tables:
                    table.blockSignals(False)
                    table.setUpdatesEnabled(True)
                    table.show()
            else:
                wl_msg_box.wl_msg_box_no_search_results(self.main)

            wl_msg.wl_msg_results_search_success(self.main, self.items_found)

        if (not self.settings['multi_search_mode'] and self.settings['search_term'] or
            self.settings['multi_search_mode'] and self.settings['search_terms']):
            self.clear_highlights()

            dialog_progress = wl_dialog_misc.Wl_Dialog_Progress_Results_Search(self.main)

            worker_results_search = Wl_Worker_Results_Search(
                self.main,
                dialog_progress = dialog_progress,
                update_gui = update_gui,
                dialog = self
            )

            thread_results_search = wl_threading.Wl_Thread(worker_results_search)
            thread_results_search.start_worker()
        else:
            wl_msg_box.wl_msg_box_missing_search_term(self.main)

            wl_msg.wl_msg_results_search_error(self.main)

    def clear_highlights(self):
        if self.items_found:
            for table in self.tables:
                table.hide()
                table.blockSignals(True)
                table.setUpdatesEnabled(False)

            for table, row, col, in self.items_found:
                if table.cellWidget(row, col):
                    table.cellWidget(row, col).setStyleSheet('border: 0')
                else:
                    table.item(row, col).setForeground(QBrush(QColor('#292929')))
                    table.item(row, col).setBackground(QBrush(QColor('#FFF')))

            for table in self.tables:
                table.blockSignals(False)
                table.setUpdatesEnabled(True)
                table.show()

            self.items_found.clear()

    def load(self):
        # Calculate size
        if 'size_multi' not in self.__dict__:
            multi_search_mode = self.settings['multi_search_mode']

            self.checkbox_multi_search_mode.setChecked(False)

            self.adjustSize()
            self.size_normal = self.size()

            self.checkbox_multi_search_mode.setChecked(True)

            self.adjustSize()
            self.size_multi = QSize(self.size_normal.width(), self.size().height())

            self.checkbox_multi_search_mode.setChecked(multi_search_mode)

        self.show()

    def add_tables(self, tables):
        self.tables.extend(tables)
