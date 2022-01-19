# ----------------------------------------------------------------------
# Wordless: Main Window
# Copyright (C) 2018-2022  Ye Lei (叶磊)
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------

import copy
import csv
import os
import pickle
import platform
import re
import subprocess
import sys
import time
import traceback

# Fix working directory on macOS
if getattr(sys, '_MEIPASS', False):
    if platform.system() == 'Darwin':
        os.chdir(sys._MEIPASS)

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import matplotlib
import nltk
import requests
import pythainlp
import underthesea.file_utils

# Use Qt backend for Matplotlib
matplotlib.use('Qt5Agg')

if getattr(sys, '_MEIPASS', False):
    # Modify path of NLTK's data files
    nltk.data.path = [os.path.join(os.getcwd(), 'nltk_data')]

    # Modify path of PyThaiNLP's data files
    PYTHAINLP_DEFAULT_DATA_DIR = os.path.realpath(pythainlp.tools.PYTHAINLP_DEFAULT_DATA_DIR)
    pythainlp.corpus._CORPUS_DB_PATH = os.path.join(PYTHAINLP_DEFAULT_DATA_DIR, pythainlp.corpus._CORPUS_DB_FILENAME)
    pythainlp.tools.path.get_pythainlp_data_path = lambda: PYTHAINLP_DEFAULT_DATA_DIR

    # Modify path of Underthesea's data files
    underthesea.file_utils.UNDERTHESEA_FOLDER = '.underthesea'

from wl_checking import wl_checking_misc
from wl_dialogs import wl_dialogs, wl_dialogs_misc, wl_msg_boxes
from wl_settings import wl_settings, wl_settings_default, wl_settings_global
from wl_utils import wl_misc, wl_threading
from wl_widgets import wl_boxes, wl_labels, wl_layouts, wl_tables

import wl_file_area
import wl_overview
import wl_concordancer
import wl_concordancer_parallel
import wl_wordlist
import wl_ngram
import wl_collocation
import wl_colligation
import wl_keyword

class Wl_Loading(QSplashScreen):
    def __init__(self):
        super().__init__(QPixmap(wl_misc.get_normalized_path('imgs/wl_loading.png')))

        msg_font = QFont('Times New Roman')
        msg_font.setPixelSize(14)

        self.setFont(msg_font)
        self.show_message(self.tr('Initializing Wordless ...'))

    def show_message(self, message):
        self.showMessage(
            f' {message}',
            color = Qt.white,
            alignment = Qt.AlignLeft | Qt.AlignBottom
        )

    def fade_in(self):
        self.setWindowOpacity(0)
        self.show()

        while self.windowOpacity() < 1:
            self.setWindowOpacity(self.windowOpacity() + 0.05)

            time.sleep(0.025)

    def fade_out(self):
        while self.windowOpacity() > 0:
            self.setWindowOpacity(self.windowOpacity() - 0.05)

            time.sleep(0.025)

class Wl_Main(QMainWindow):
    def __init__(self, loading_window):
        super().__init__()

        self.loading_window = loading_window
        self.threads_check_updates = []

        # Email
        self.email = 'blkserene@gmail.com'
        self.email_html = '<a href="mailto:blkserene@gmail.com">blkserene@gmail.com</a>'

        # Version numbers
        self.ver = wl_misc.get_wl_ver()
        self.ver_major, self.ver_minor, self.ver_patch = wl_misc.split_wl_ver(self.ver)

        # Title
        self.setWindowTitle(self.tr(f'Wordless'))

        # Icon
        self.setWindowIcon(QIcon(wl_misc.get_normalized_path('imgs/wl_icon.ico')))

        self.loading_window.show_message(self.tr('Loading settings ...'))

        # Default settings
        wl_settings_default.init_settings_default(self)

        # Custom settings
        path_settings = wl_misc.get_normalized_path('wl_settings.pickle')

        if os.path.exists(path_settings):
            with open(path_settings, 'rb') as f:
                settings_custom = pickle.load(f)

            if wl_checking_misc.check_custom_settings(settings_custom, self.settings_default):
                self.settings_custom = settings_custom
            else:
                self.settings_custom = copy.deepcopy(self.settings_default)
        else:
            self.settings_custom = copy.deepcopy(self.settings_default)

        # Global settings
        wl_settings_global.init_settings_global(self)

        # Settings
        self.wl_settings = wl_settings.Wl_Settings(self)

        self.loading_window.show_message(self.tr('Initializing main window ...'))

        # Menu
        self.init_menu()

        # Work Area & File Area
        self.init_central_widget()

        # Status Bar
        self.statusBar().showMessage(self.tr('Ready!'))

        self.statusBar().setFixedHeight(22)
        self.statusBar().setStyleSheet('''
            QStatusBar {
                background-color: #D0D0D0;
            }
        ''')

        self.load_settings()

        # Fix layout on macOS
        if platform.system() == 'Darwin':
            self.fix_macos_layout(self)

        self.loading_window.show_message(self.tr('Starting Wordless ...'))

    def fix_macos_layout(self, parent):
        for widget in parent.children():
            if widget.children():
                self.fix_macos_layout(widget)
            else:
                if isinstance(widget, QWidget) and not isinstance(widget, QPushButton):
                    widget.setAttribute(Qt.WA_LayoutUsesWidgetRect)

    def closeEvent(self, event):
        if self.settings_custom['general']['misc']['confirm_on_exit']:
            dialog_confirm_exit = wl_dialogs_misc.Wl_Dialog_Confirm_Exit(self)
            result = dialog_confirm_exit.exec_()

            if result == QDialog.Accepted:
                self.save_settings()

                event.accept()
            elif result == QDialog.Rejected:
                event.ignore()
        else:
            event.accept()

    def init_menu(self):
        menu_file = self.menuBar().addMenu(self.tr('File'))
        menu_prefs = self.menuBar().addMenu(self.tr('Preferences'))
        menu_help = self.menuBar().addMenu(self.tr('Help'))

        # File
        menu_file_open_files = menu_file.addAction(self.tr('Open File(s)...'))
        menu_file_open_files.setStatusTip(self.tr('Open file(s)'))
        menu_file_open_dir = menu_file.addAction(self.tr('Open Folder...'))
        menu_file_open_dir.setStatusTip(self.tr('Open all files in folder'))
        menu_file_reopen = menu_file.addAction(self.tr('Reopen Closed Files'))
        menu_file_reopen.setStatusTip(self.tr('Reopen closed files'))

        menu_file.addSeparator()

        menu_file_reload_selected = menu_file.addAction(self.tr('Reload Selected'))
        menu_file_reload_selected.setStatusTip(self.tr('Reload selected files'))
        menu_file_reload_all = menu_file.addAction(self.tr('Reload All'))
        menu_file_reload_all.setStatusTip(self.tr('Reload all files'))

        menu_file.addSeparator()

        menu_file_select_all = menu_file.addAction(self.tr('Select All'))
        menu_file_select_all.setStatusTip(self.tr('Select all files'))
        menu_file_deselect_all = menu_file.addAction(self.tr('Deselect All'))
        menu_file_deselect_all.setStatusTip(self.tr('Deselect all files'))
        menu_file_invert_selection = menu_file.addAction(self.tr('Invert Selection'))
        menu_file_invert_selection.setStatusTip(self.tr('Invert file selection'))

        menu_file.addSeparator()

        menu_file_close_selected = menu_file.addAction(self.tr('Close Selected'))
        menu_file_close_selected.setStatusTip(self.tr('Close selected file(s)'))
        menu_file_close_all = menu_file.addAction(self.tr('Close All'))
        menu_file_close_all.setStatusTip(self.tr('Close all files'))

        menu_file.addSeparator()

        menu_file_exit = menu_file.addAction(self.tr('Exit...'))
        menu_file_exit.setStatusTip(self.tr('Exit the program'))
        menu_file_exit.triggered.connect(self.close)

        # Preferences
        menu_prefs_settings = menu_prefs.addAction(self.tr('Settings'))
        menu_prefs_settings.setStatusTip(self.tr('Change settings'))
        menu_prefs_settings.triggered.connect(self.wl_settings.load)

        menu_prefs_reset_layouts = menu_prefs.addAction(self.tr('Reset Layouts'))
        menu_prefs_reset_layouts.setStatusTip(self.tr('Reset Layouts'))
        menu_prefs_reset_layouts.triggered.connect(self.prefs_reset_layouts)

        menu_prefs.addSeparator()

        menu_prefs_show_status_bar = menu_prefs.addAction(self.tr('Show Status Bar'))
        menu_prefs_show_status_bar.setCheckable(True)
        menu_prefs_show_status_bar.setStatusTip(self.tr('Show/Hide the status bar'))
        menu_prefs_show_status_bar.triggered.connect(self.prefs_show_status_bar)

        # Help
        menu_help_citing = menu_help.addAction(self.tr('Citing'))
        menu_help_citing.setStatusTip(self.tr('Show information about citing'))
        menu_help_citing.triggered.connect(self.help_citing)

        menu_help_acks = menu_help.addAction(self.tr('Acknowledgments'))
        menu_help_acks.setStatusTip(self.tr('Show acknowldgments'))
        menu_help_acks.triggered.connect(self.help_acks)

        menu_help.addSeparator()

        menu_help_need_help = menu_help.addAction(self.tr('Need Help?'))
        menu_help_need_help.setStatusTip(self.tr('Show help information'))
        menu_help_need_help.triggered.connect(self.help_need_help)

        menu_help_contributing = menu_help.addAction(self.tr('Contributing'))
        menu_help_contributing.setStatusTip(self.tr('Show information about contributing'))
        menu_help_contributing.triggered.connect(self.help_contributing)

        menu_help_donating = menu_help.addAction(self.tr('Donating'))
        menu_help_donating.setStatusTip(self.tr('Show information about donating'))
        menu_help_donating.triggered.connect(self.help_donating)

        menu_help.addSeparator()

        menu_help_check_updates = menu_help.addAction(self.tr('Check for Updates'))
        menu_help_check_updates.setStatusTip(self.tr('Check for updates of Wordless'))
        menu_help_check_updates.triggered.connect(self.help_check_updates)

        menu_help_changelog = menu_help.addAction(self.tr('Changelog'))
        menu_help_changelog.setStatusTip(self.tr('Show Changelog'))
        menu_help_changelog.triggered.connect(self.help_changelog)

        menu_help_about = menu_help.addAction(self.tr('About Wordless'))
        menu_help_about.setStatusTip(self.tr('Show information about Wordless'))
        menu_help_about.triggered.connect(self.help_about)

    # Preferences - Show Status Bar
    def prefs_show_status_bar(self):
        self.settings_custom['menu']['prefs']['show_status_bar'] = self.find_menu_item(self.tr('Show Status Bar')).isChecked()

        if self.settings_custom['menu']['prefs']['show_status_bar']:
            self.statusBar().show()
        else:
            self.statusBar().hide()

    # Preferences - Reset Layouts
    def prefs_reset_layouts(self):
        if wl_msg_boxes.wl_msg_box_reset_layouts(self):
            self.centralWidget().setSizes([self.height() - 210, 210])

    # Help - Citing
    def help_citing(self):
        Wl_Dialog_Citing(self).open()

    # Help - Acknowledgments
    def help_acks(self):
        Wl_Dialog_Acks(self).open()

    # Help - Need Help?
    def help_need_help(self):
        Wl_Dialog_Need_Help(self).open()

    # Help - Contributing
    def help_contributing(self):
        Wl_Msg_Box_Help(self).open()

    # Help - Donating
    def help_donating(self):
        Wl_Dialog_Donating(self).open()

    # Help - Check for Updates
    def help_check_updates(self, on_startup = False):
        dialog_check_updates = Wl_Dialog_Check_Updates(self, on_startup = on_startup)

        if not on_startup:
            dialog_check_updates.open()

    # Help - Changelog
    def help_changelog(self):
        Wl_Dialog_Changelog(self).open()

    # Help - About Wordless
    def help_about(self):
        Wl_Dialog_About(self).open()

    def init_central_widget(self):
        self.wl_file_area = wl_file_area.Wrapper_File_Area(self)
        self.init_work_area()

        # Align work are and file area
        wrapper_file_area = QWidget()

        wrapper_file_area.setLayout(wl_layouts.Wl_Layout())
        wrapper_file_area.layout().addWidget(self.wl_file_area, 0, 0)

        margins = self.wl_file_area.layout().contentsMargins()

        if platform.system() == 'Windows':
            wrapper_file_area.layout().setContentsMargins(0, 0, 2, 0)

            margins.setLeft(margins.left() + 2)
            margins.setRight(margins.right() + 2)
        elif platform.system() == 'Darwin':
            wrapper_file_area.layout().setContentsMargins(2, 0, 2, 0)
            margins.setLeft(margins.left() + 1)
            margins.setRight(margins.right() + 1)
        elif platform.system() == 'Linux':
            wrapper_file_area.layout().setContentsMargins(0, 0, 0, 0)

            margins.setRight(margins.right() + 2)

        self.wl_file_area.layout().setContentsMargins(margins)

        splitter_central_widget = wl_layouts.Wl_Splitter(Qt.Vertical, self)
        splitter_central_widget.addWidget(self.wl_work_area)
        splitter_central_widget.addWidget(wrapper_file_area)

        if platform.system() in ['Windows', 'Linux']:
            splitter_central_widget.setHandleWidth(1)
        elif platform.system() == 'Darwin':
            splitter_central_widget.setHandleWidth(2)

        splitter_central_widget.setObjectName('splitter-central-widget')
        splitter_central_widget.setStyleSheet('''
            QSplitter#splitter-central-widget {
                padding: 4px 6px;
            }
        ''')

        splitter_central_widget.setStretchFactor(0, 1)

        self.setCentralWidget(splitter_central_widget)

    def init_work_area(self):
        self.wl_work_area = QTabWidget(self)

        self.wl_work_area.addTab(
            wl_overview.Wrapper_Overview(self),
            self.tr('Overview')
        )
        self.wl_work_area.addTab(
            wl_concordancer.Wrapper_Concordancer(self),
            self.tr('Concordancer')
        )
        self.wl_work_area.addTab(
            wl_concordancer_parallel.Wrapper_Concordancer_Parallel(self),
            self.tr('Concordancer')
        )
        self.wl_work_area.addTab(
            wl_wordlist.Wrapper_Wordlist(self),
            self.tr('Wordlist')
        )
        self.wl_work_area.addTab(
            wl_ngram.Wrapper_Ngram(self),
            self.tr('N-gram')
        )
        self.wl_work_area.addTab(
            wl_collocation.Wrapper_Collocation(self),
            self.tr('Collocation')
        )
        self.wl_work_area.addTab(
            wl_colligation.Wrapper_Colligation(self),
            self.tr('Colligation')
        )
        self.wl_work_area.addTab(
            wl_keyword.Wrapper_Keyword(self),
            self.tr('Keyword')
        )

        self.wl_work_area.currentChanged.connect(self.work_area_changed)
        
        self.load_settings_work_area()

    def load_settings_work_area(self):
        # Current tab
        work_area_cur = self.settings_custom['work_area_cur']

        for i in range(self.wl_work_area.count()):
            if self.wl_work_area.tabText(i) == work_area_cur:
                self.wl_work_area.setCurrentIndex(i)

                break

        # Parallel mode
        # * Do not use "setTabVisible" on macOS which is only available for Qt 5.15+
        if platform.system() in ['Windows', 'Linux']:
            if self.settings_custom['concordancer']['parallel_mode']:
                self.wl_work_area.setTabVisible(1, False)
            else:
                self.wl_work_area.setTabVisible(2, False)
        elif platform.system() == 'Darwin':
            self.concordancer = self.wl_work_area.widget(1)
            self.concordancer_parallel = self.wl_work_area.widget(2)

            if self.settings_custom['concordancer']['parallel_mode']:
                self.wl_work_area.removeTab(1)
            else:
                self.wl_work_area.removeTab(2)

        self.work_area_changed()

    def work_area_changed(self):
        # Current tab
        self.settings_custom['work_area_cur'] = self.wl_work_area.tabText(self.wl_work_area.currentIndex())
        
        # Parallel mode
        if platform.system() in ['Windows', 'Linux']:
            if self.wl_work_area.count() == 8:
                if self.wl_work_area.currentIndex() == 1 and self.settings_custom['concordancer']['parallel_mode']:
                    self.wl_work_area.widget(2).checkbox_parallel_mode.setChecked(True)

                    self.wl_work_area.setTabVisible(1, False)
                    self.wl_work_area.setTabVisible(2, True)

                    self.wl_work_area.setCurrentIndex(2)
                elif self.wl_work_area.currentIndex() == 2 and not self.settings_custom['concordancer_parallel']['parallel_mode']:
                    self.wl_work_area.widget(1).checkbox_parallel_mode.setChecked(False)

                    self.wl_work_area.setTabVisible(1, True)
                    self.wl_work_area.setTabVisible(2, False)

                    self.wl_work_area.setCurrentIndex(1)
        elif platform.system() == 'Darwin':
            if self.wl_work_area.count() == 7 and self.wl_work_area.currentIndex() == 1:
                if self.wl_work_area.widget(1) == self.concordancer and self.settings_custom['concordancer']['parallel_mode']:
                    self.concordancer_parallel.checkbox_parallel_mode.setChecked(True)

                    self.wl_work_area.removeTab(1)
                    self.wl_work_area.insertTab(1, self.concordancer_parallel, self.tr('Concordancer'))
                elif self.wl_work_area.widget(1) == self.concordancer_parallel and not self.settings_custom['concordancer_parallel']['parallel_mode']:
                    self.concordancer.checkbox_parallel_mode.setChecked(False)

                    self.wl_work_area.removeTab(1)
                    self.wl_work_area.insertTab(1, self.concordancer, self.tr('Concordancer'))

                self.wl_work_area.setCurrentIndex(1)

    def load_settings(self):
        settings = self.settings_custom

        # Fonts
        self.setStyleSheet(f'''
            font-family: {settings['general']['font_settings']['font_family']};
            font-size: {settings['general']['font_settings']['font_size']}px;
        ''')

        # Menu
        self.find_menu_item(self.tr('Show Status Bar')).setChecked(settings['menu']['prefs']['show_status_bar'])

        # Layouts
        self.centralWidget().setSizes(settings['layouts']['central_widget'])

    def save_settings(self):
        # Clear history of closed files
        self.settings_custom['file_area']['files_closed'].clear()

        # Layouts
        self.settings_custom['layouts']['central_widget'] = self.centralWidget().sizes()

        with open('wl_settings.pickle', 'wb') as f:
            pickle.dump(self.settings_custom, f)

    def find_menu_item(self, text, menu = None):
        menu_item = None

        if not menu:
            menu = self.menuBar()

        for action in menu.actions():
            if menu_item:
                break

            if action.menu():
                menu_item = self.find_menu_item(text, menu = action.menu())
            else:
                if action.text() == text:
                    menu_item = action

        return menu_item

    def restart(self):
        if getattr(sys, '_MEIPASS', False):
            if platform.system() == 'Windows':
                subprocess.Popen([wl_misc.get_normalized_path('Wordless.exe')])
            elif platform.system() == 'Darwin':
                subprocess.Popen([wl_misc.get_normalized_path('Wordless')])
            elif platform.system() == 'Linux':
                subprocess.Popen([wl_misc.get_normalized_path('Wordless')])
        else:
            if platform.system() == 'Windows':
                subprocess.Popen(['python', wl_misc.get_normalized_path(__file__)])
            elif platform.system() == 'Darwin':
                subprocess.Popen(['python3', wl_misc.get_normalized_path(__file__)])
            elif platform.system() == 'Linux':
                subprocess.Popen(['python3.8', wl_misc.get_normalized_path(__file__)])

        self.save_settings()
        sys.exit(0)

class Wl_Dialog_Citing(wl_dialogs.Wl_Dialog_Info):
    def __init__(self, main):
        super().__init__(
            main,
            title = main.tr('Citing'),
            width = 450,
            no_buttons = True
        )

        self.label_citing = wl_labels.Wl_Label_Dialog(
            self.tr('''
                <div>
                    If you publish work that uses Wordless, please cite as follows.
                </div>
            '''),
            self
        )

        self.label_citation_sys = QLabel(self.tr('Citation System:'), self)
        self.combo_box_citation_sys = wl_boxes.Wl_Combo_Box(self)
        self.text_edit_citing = QTextEdit(self)
    
        self.button_copy = QPushButton(self.tr('Copy'), self)
        self.button_close = QPushButton(self.tr('Close'), self)
    
        self.combo_box_citation_sys.addItems([
            self.tr('APA (7th Edition)'),
            self.tr('MLA (8th Edition)')
        ])
    
        self.button_copy.setFixedWidth(100)
        self.button_close.setFixedWidth(100)
    
        self.text_edit_citing.setFixedHeight(100)
        self.text_edit_citing.setReadOnly(True)
    
        self.combo_box_citation_sys.currentTextChanged.connect(self.citation_sys_changed)
    
        self.button_copy.clicked.connect(self.copy)
        self.button_close.clicked.connect(self.accept)
    
        layout_citation_sys = wl_layouts.Wl_Layout()
        layout_citation_sys.addWidget(self.label_citation_sys, 0, 0)
        layout_citation_sys.addWidget(self.combo_box_citation_sys, 0, 1)
    
        layout_citation_sys.setColumnStretch(2, 1)
    
        self.wrapper_info.layout().addWidget(self.label_citing, 0, 0, 1, 2)
        self.wrapper_info.layout().addLayout(layout_citation_sys, 1, 0, 1, 2)
        self.wrapper_info.layout().addWidget(self.text_edit_citing, 2, 0, 1, 2)
    
        self.wrapper_buttons.layout().addWidget(self.button_copy, 0, 0)
        self.wrapper_buttons.layout().addWidget(self.button_close, 0, 1)

        self.load_settings()

        self.set_fixed_height()

    def load_settings(self):
        settings = copy.deepcopy(self.main.settings_custom['menu']['help']['citing'])

        self.combo_box_citation_sys.setCurrentText(settings['citation_sys'])

        self.citation_sys_changed()

    def citation_sys_changed(self):
        settings = self.main.settings_custom['menu']['help']['citing']

        settings['citation_sys'] = self.combo_box_citation_sys.currentText()

        if settings['citation_sys'] == self.tr('APA (7th Edition)'):
            self.text_edit_citing.setHtml(f'Ye, L. (2021). <i>Wordless</i> (Version {self.main.ver}) [Computer software]. Github. https://github.com/BLKSerene/Wordless')
        elif settings['citation_sys'] == self.tr('MLA (8th Edition)'):
            self.text_edit_citing.setHtml(f'Ye Lei. <i>Wordless</i>, version {self.main.ver}, 2021. <i>Github</i>, https://github.com/BLKSerene/Wordless.')

    def copy(self):
        self.text_edit_citing.setFocus()
        self.text_edit_citing.selectAll()
        self.text_edit_citing.copy()

class Wl_Dialog_Acks(wl_dialogs.Wl_Dialog_Info):
    def __init__(self, main):
        super().__init__(
            main,
            title = main.tr('Acknowledgments'),
            width = 650
        )

        self.label_acks = wl_labels.Wl_Label_Dialog(
            self.tr('''
                <div>
                    I would like to extend my sincere gratitude to the following open-source projects without which this project would not have been possible:
                </div>
            '''),
            self
        )
        self.table_acks = wl_tables.Wl_Table(
            self,
            headers = [
                self.tr('Name'),
                self.tr('Version'),
                self.tr('Authors'),
                self.tr('License')
            ]
        )

        self.table_acks.setFixedHeight(300)

        self.wrapper_info.layout().addWidget(self.label_acks, 0, 0)
        self.wrapper_info.layout().addWidget(self.table_acks, 1, 0)

        self.set_fixed_height()

        # Load acknowledgments
        acks = []

        with open(r'wl_acks.csv', 'r', encoding = 'utf_8', newline = '') as f:
            reader = csv.reader(f)

            for row in reader:
                name = row[0]
                home_page = row[1]
                ver = row[2]
                authors = row[3]
                license = row[4]
                license_url = row[5]

                acks.append([name, home_page, ver, authors, license, license_url])

        self.table_acks.clear_table()

        self.table_acks.blockSignals(True)
        self.table_acks.setUpdatesEnabled(False)

        self.table_acks.setRowCount(len(acks))

        for i, (name, home_page, ver, authors, license, licence_url) in enumerate(acks):
            name = f'<a href="{home_page}">{name}</a>'
            license = f'<a href="{licence_url}">{license}</a>'

            self.table_acks.setCellWidget(i, 0, wl_labels.Wl_Label_Html(name, self))
            self.table_acks.setCellWidget(i, 1, wl_labels.Wl_Label_Html_Centered(ver, self))
            self.table_acks.setCellWidget(i, 2, wl_labels.Wl_Label_Html(authors, self))
            self.table_acks.setCellWidget(i, 3, wl_labels.Wl_Label_Html_Centered(license, self))

        self.table_acks.blockSignals(False)
        self.table_acks.setUpdatesEnabled(True)

class Wl_Dialog_Need_Help(wl_dialogs.Wl_Dialog_Info):
    def __init__(self, main):
        super().__init__(
            main,
            title = main.tr('Need Help?'),
            width = 550,
            height = 450
        )

        self.label_need_help = wl_labels.Wl_Label_Dialog(
            self.tr('''
                <div>
                    If you encounter a problem, find a bug, or require any further information, feel free to ask questions, submit bug reports, or provide feedback by <a href="https://github.com/BLKSerene/Wordless/issues/new">creating an issue</a> on Github if you fail to find the answer by searching <a href="https://github.com/BLKSerene/Wordless/issues">existing issues</a> first.
                </div>

                <div>
                    If you need to post sample texts or other information that cannot be shared or you do not want to share publicly, you may send me an email.
                </div>
            '''),
            self
        )

        self.table_need_help = wl_tables.Wl_Table(
            self,
            headers = [
                self.tr('Channel'),
                self.tr('Contact Information')
            ],
            cols_stretch = [
                self.tr('Contact Information')
            ]
        )

        self.table_need_help.setFixedHeight(300)
        self.table_need_help.setRowCount(3)
        self.table_need_help.verticalHeader().setHidden(True)

        self.table_need_help.setCellWidget(0, 0, wl_labels.Wl_Label_Html_Centered(self.tr('Documentation'), self))
        self.table_need_help.setCellWidget(0, 1, wl_labels.Wl_Label_Html('<a href="https://github.com/BLKSerene/Wordless#documentation">https://github.com/BLKSerene/Wordless#documentation</a>', self))
        self.table_need_help.setCellWidget(1, 0, wl_labels.Wl_Label_Html_Centered(self.tr('Email'), self))
        self.table_need_help.setCellWidget(1, 1, wl_labels.Wl_Label_Html(self.main.email_html, self))
        self.table_need_help.setCellWidget(2, 0, wl_labels.Wl_Label_Html_Centered(self.tr('<a href="https://www.wechat.com/en/">WeChat</a><br>Official Account'), self))
        self.table_need_help.setCellWidget(2, 1, wl_labels.Wl_Label_Html_Centered('<img src="imgs/wechat_official_account.jpg">', self))

        self.wrapper_info.layout().addWidget(self.label_need_help, 0, 0)
        self.wrapper_info.layout().addWidget(self.table_need_help, 1, 0)

class Wl_Msg_Box_Help(wl_msg_boxes.Wl_Msg_Box):
    def __init__(self, main):
        super().__init__(
            main,
            icon = QMessageBox.Information,
            title = main.tr('Contributing'),
            text = main.tr('''
                <div>
                    If you have an interest in helping the development of Wordless, you may contribute bug fixes, enhancements, or new features by <a href="https://github.com/BLKSerene/Wordless/pulls">creating a pull request</a> on Github.
                </div>
                <div>
                    Besides, you may contribute by submitting enhancement proposals or feature requests, write tutorials or <a href ="https://github.com/BLKSerene/Wordless/wiki">Github Wiki</a> for Wordless, or helping me translate Wordless and its documentation to other languages.
                </div>
            ''')
        )

        self.setTextFormat(Qt.RichText)
        self.setTextInteractionFlags(Qt.TextBrowserInteraction)

class Wl_Dialog_Donating(wl_dialogs.Wl_Dialog_Info):
    def __init__(self, main):
        super().__init__(
            main,
            title = main.tr('Donating'),
            width = 450
        )

        self.label_donating = wl_labels.Wl_Label_Dialog(
            self.tr('''
                <div>
                    If you would like to support the development of Wordless, you may donate via <a href="https://www.paypal.com/">PayPal</a>, <a href="https://global.alipay.com/">Alipay</a>, or <a href="https://pay.weixin.qq.com/index.php/public/wechatpay_en">WeChat Pay</a>.
                </div>
            '''),
            self
        )
        self.label_donating_via = QLabel(self.tr('Donating via:'), self)
        self.combo_box_donating_via = wl_boxes.Wl_Combo_Box(self)
        self.label_donating_via_img = wl_labels.Wl_Label_Html('', self)

        self.combo_box_donating_via.addItems([
            self.tr('PayPal'),
            self.tr('Alipay'),
            self.tr('WeChat Pay')
        ])

        self.combo_box_donating_via.currentTextChanged.connect(self.donating_via_changed)

        layout_donating_via = wl_layouts.Wl_Layout()
        layout_donating_via.addWidget(self.label_donating_via, 0, 0)
        layout_donating_via.addWidget(self.combo_box_donating_via, 0, 1)

        layout_donating_via.setColumnStretch(2, 1)

        self.wrapper_info.layout().addWidget(self.label_donating, 0, 0)
        self.wrapper_info.layout().addLayout(layout_donating_via, 1, 0)
        self.wrapper_info.layout().addWidget(self.label_donating_via_img, 2, 0, Qt.AlignHCenter | Qt.AlignVCenter)

        # Calculate height
        donating_via_old = self.main.settings_custom['menu']['help']['donating']['donating_via']

        self.combo_box_donating_via.setCurrentText('PayPal')
        self.donating_via_changed()

        height_donating_via_paypal = self.label_donating_via_img.sizeHint().height()
        self.height_paypal = self.heightForWidth(self.width())

        self.combo_box_donating_via.setCurrentText('Alipay')
        self.donating_via_changed()

        height_donating_via_alipay = self.label_donating_via_img.sizeHint().height()
        self.height_alipay = self.heightForWidth(self.width()) + (height_donating_via_alipay - height_donating_via_paypal)

        self.main.settings_custom['menu']['help']['donating']['donating_via'] = donating_via_old

        self.load_settings()

    def load_settings(self):
        settings = copy.deepcopy(self.main.settings_custom['menu']['help']['donating'])

        self.combo_box_donating_via.setCurrentText(settings['donating_via'])

        self.donating_via_changed()

    def donating_via_changed(self):
        settings = self.main.settings_custom['menu']['help']['donating']

        settings['donating_via'] = self.combo_box_donating_via.currentText()

        if settings['donating_via'] == self.tr('PayPal'):
            self.label_donating_via_img.setText('<a href="https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=V2V54NYE2YD32"><img src="imgs/donating_paypal.gif"></a>')
        elif settings['donating_via'] == self.tr('Alipay'):
            self.label_donating_via_img.setText('<img src="imgs/donating_alipay.png">')
        elif settings['donating_via'] == self.tr('WeChat Pay'):
            self.label_donating_via_img.setText('<img src="imgs/donating_wechat_pay.png">')

        if 'height_alipay' in self.__dict__:
            if settings['donating_via'] == self.tr('PayPal'):
                self.setFixedHeight(self.height_paypal)
            elif settings['donating_via'] in [self.tr('Alipay'), self.tr('WeChat Pay')]:
                self.setFixedHeight(self.height_alipay)

        if platform.system() in ['Windows', 'Linux']:
            self.move_to_center()

class Worker_Check_Updates(QObject):
    worker_done = pyqtSignal(str, str)

    def __init__(self, main):
        super().__init__()

        self.main = main
        self.stopped = False

    def run(self):
        ver_new = ''

        try:
            r = requests.get('https://raw.githubusercontent.com/BLKSerene/Wordless/main/src/VERSION', timeout = 5)

            if r.status_code == 200:
                for line in r.text.splitlines():
                    if line and not line.startswith('#'):
                        ver_new = line.rstrip()

                if self.is_newer_version(ver_new):
                    updates_status = 'updates_available'
                else:
                    updates_status = 'no_updates'
            else:
                updates_status = 'network_err'
        except Exception:
            print(traceback.format_exc())

            updates_status = 'network_err'

        if self.stopped:
            updates_status == ''

        self.worker_done.emit(updates_status, ver_new)

    def is_newer_version(self, ver_new):
        ver_major_new, ver_minor_new, ver_patch_new = wl_misc.split_wl_ver(ver_new)

        if (self.main.ver_major < ver_major_new or
            self.main.ver_minor < ver_minor_new or
            self.main.ver_patch < ver_patch_new):
            return True
        else:
            return False

    def stop(self):
        self.stopped = True

class Wl_Dialog_Check_Updates(wl_dialogs.Wl_Dialog_Info):
    def __init__(self, main, on_startup = False):
        super().__init__(
            main,
            title = main.tr('Check for Updates'),
            width = 480,
            no_buttons = True
        )

        self.on_startup = on_startup

        self.label_checking_status = wl_labels.Wl_Label_Dialog('', self)
        self.label_cur_ver = wl_labels.Wl_Label_Dialog(self.tr(f'Current Version: {self.main.ver}'), self)
        self.label_latest_ver = wl_labels.Wl_Label_Dialog('', self)

        self.checkbox_check_updates_on_startup = QCheckBox(self.tr('Check for updates on startup'), self)
        self.button_try_again = QPushButton(self.tr('Try Again'), self)
        self.button_cancel = QPushButton(self.tr('Cancel'), self)

        self.checkbox_check_updates_on_startup.stateChanged.connect(self.check_updates_on_startup_changed)
        self.button_try_again.clicked.connect(self.check_updates)

        self.wrapper_info.layout().addWidget(self.label_checking_status, 0, 0, 2, 1)
        self.wrapper_info.layout().addWidget(self.label_cur_ver, 2, 0)
        self.wrapper_info.layout().addWidget(self.label_latest_ver, 3, 0)

        self.wrapper_buttons.layout().addWidget(self.checkbox_check_updates_on_startup, 0, 0)
        self.wrapper_buttons.layout().addWidget(self.button_try_again, 0, 2)
        self.wrapper_buttons.layout().addWidget(self.button_cancel, 0, 3)

        self.wrapper_buttons.layout().setColumnStretch(1, 1)

        self.load_settings()

        self.set_fixed_height()

    def check_updates(self):
        self.checking_status_changed('checking')

        self.main.worker_check_updates = Worker_Check_Updates(self.main)
        thread_check_updates = wl_threading.Wl_Thread(self.main.worker_check_updates)

        self.main.threads_check_updates.append(thread_check_updates)

        thread_check_updates.destroyed.connect(lambda: self.main.threads_check_updates.remove(thread_check_updates))

        self.main.worker_check_updates.worker_done.connect(self.checking_status_changed)
        self.main.worker_check_updates.worker_done.connect(thread_check_updates.quit)
        self.main.worker_check_updates.worker_done.connect(self.main.worker_check_updates.deleteLater)

        thread_check_updates.start()

    def stop_checking(self):
        self.main.worker_check_updates.stop()

        self.reject()

    def checking_status_changed(self, status, ver_new = ''):
        # Try Again
        if status == 'network_err':
            self.button_try_again.show()
        else:
            self.button_try_again.hide()

        if status == 'checking':
            self.label_checking_status.set_text(self.tr('''
                <div>
                    Checking for updates...
                </div>
            '''))
            self.label_latest_ver.set_text(self.tr('Latest Version: Checking...'))

            self.button_cancel.setText(self.tr('Cancel'))
            self.button_cancel.disconnect()
            self.button_cancel.clicked.connect(self.stop_checking)
        else:
            if status in ['updates_available', 'no_updates']:
                if status == 'updates_available':
                    self.label_checking_status.set_text(self.tr(f'''
                        <div>
                            Wordless {ver_new} is out, click <a href="https://github.com/BLKSerene/Wordless#download"><b>HERE</b></a> to download the latest version of Wordless.
                        </div>
                    '''))
                    self.label_latest_ver.set_text(self.tr(f'Latest Version: {ver_new}'))
                elif status == 'no_updates':
                    self.label_checking_status.set_text(self.tr('''
                        <div>
                            Hooray, you are using the latest version of Wordless!
                        </div>
                    '''))
                    self.label_latest_ver.set_text(self.tr(f'Latest Version: {self.main.ver}'))
            elif status == 'network_err':
                self.label_checking_status.set_text(self.tr('''
                    <div>
                        A network error has occurred, please check your network settings and try again or <a href="https://github.com/BLKSerene/Wordless/releases">check for updates manually</a>.
                    </div>
                '''))
                self.label_latest_ver.set_text(self.tr('Latest Version: Network error'))

            self.button_cancel.setText(self.tr('OK'))
            self.button_cancel.disconnect()
            self.button_cancel.clicked.connect(self.accept)

        # On startup
        if self.on_startup:
            if status == 'updates_available':
                self.open()
                self.setFocus()
            else:
                self.accept()

    def load_settings(self):
        settings = self.main.settings_custom['general']['update_settings']

        self.checkbox_check_updates_on_startup.setChecked(settings['check_updates_on_startup'])

        self.check_updates()

    def check_updates_on_startup_changed(self):
        settings = self.main.settings_custom['general']['update_settings']

        settings['check_updates_on_startup'] = self.checkbox_check_updates_on_startup.isChecked()

class Wl_Dialog_Changelog(wl_dialogs.Wl_Dialog_Info):
    def __init__(self, main):
        changelog = []

        try:
            with open('CHANGELOG.md', 'r', encoding = 'utf_8') as f:
                for line in f:
                    # Changelog headers
                    if line.startswith('## '):
                        release_ver = re.search(r'(?<=\[)[^\]]+?(?=\])', line).group()
                        release_link = re.search(r'(?<=\()[^\)]+?(?=\))', line).group()
                        release_date = re.search(r'(?<=\- )[0-9?]{2}/[0-9?]{2}/[0-9?]{4}', line).group()

                        changelog.append({
                            'release_ver': release_ver,
                            'release_link': release_link,
                            'release_date': release_date,
                            'changelog_sections': []
                        })

                    # Changelog section headers
                    elif line.startswith('### '):
                        changelog[-1]['changelog_sections'].append({
                            'section_header': line.replace('###', '').strip(),
                            'section_list': []
                        })
                    # Changelog section lists
                    elif line.startswith('- '):
                        line = re.sub(r'^- ', r'', line).strip()
                        
                        changelog[-1]['changelog_sections'][-1]['section_list'].append(line)
        except:
            pass

        changelog_text = f'''
            {main.settings_global['styles']['style_changelog']}
            <body>
        '''

        for release in changelog:
            changelog_text += f'''
                <div class="changelog">
                    <div class="changelog-header"><a href="{release['release_link']}">{release['release_ver']}</a> - {release['release_date']}</div>
                    <hr>
            '''

            for changelog_section in release['changelog_sections']:
                changelog_text += f'''
                    <div class="changelog-section">
                        <div class="changelog-section-header">{changelog_section['section_header']}</div>
                        <ul>
                '''

                for item in changelog_section['section_list']:
                    changelog_text += f'''
                        <li>{item}</li>
                    '''

                changelog_text += f'''
                        </ul>
                    </div>
                '''

            changelog_text += f'''
                </div>
            '''

        changelog_text += f'''
            </body>
        '''

        super().__init__(
            main,
            title = main.tr('Changelog'),
            width = 480,
            height = 420
        )

        text_edit_changelog = wl_boxes.Wl_Text_Browser(self)
        text_edit_changelog.setHtml(changelog_text)

        self.wrapper_info.layout().addWidget(text_edit_changelog, 0, 0)

class Wl_Dialog_About(wl_dialogs.Wl_Dialog_Info):
    def __init__(self, main):
        super().__init__(main, title = main.tr('About Wordless'))

        img_wl_icon = QPixmap('imgs/wl_icon_about.png')
        img_wl_icon = img_wl_icon.scaled(64, 64)

        label_about_icon = QLabel('', self)
        label_about_icon.setPixmap(img_wl_icon)

        label_about_title = wl_labels.Wl_Label_Dialog_No_Wrap(
            self.tr(f'''
                <div style="text-align: center;">
                    <h2>Wordless {main.ver}</h2>
                    <div>
                        An Integrated Corpus Tool with Multilingual Support<br>
                        for the Study of Language, Literature, and Translation
                    </div>
                </div>
            '''),
            self
        )
        label_about_copyright = wl_labels.Wl_Label_Dialog_No_Wrap(
            self.tr('''
                <hr>
                <div style="text-align: center;">
                    Copyright (C) 2018-2022&nbsp;&nbsp;Ye Lei (<span style="font-family: simsun">叶磊</span>)<br>
                    Licensed Under GNU GPLv3<br>
                    All Other Rights Reserved
                </div>
            '''),
            self
        )

        self.wrapper_info.layout().addWidget(label_about_icon, 0, 0)
        self.wrapper_info.layout().addWidget(label_about_title, 0, 1)
        self.wrapper_info.layout().addWidget(label_about_copyright, 1, 0, 1, 2)

        self.wrapper_info.layout().setColumnStretch(1, 1)
        self.wrapper_info.layout().setVerticalSpacing(0)

        self.set_fixed_size()
        self.setFixedWidth(self.width() + 10)

if __name__ == '__main__':
    wl_app = QApplication(sys.argv)

    wl_loading = Wl_Loading()

    wl_loading.raise_()
    wl_loading.fade_in()

    wl_app.processEvents()

    wl_main = Wl_Main(wl_loading)

    wl_loading.fade_out()
    wl_loading.finish(wl_main)

    # Check for updates on startup
    if wl_main.settings_custom['general']['update_settings']['check_updates_on_startup']:
        wl_main.dialog_check_updates = wl_main.help_check_updates(on_startup = True)

    # Show changelog on first startup
    # * Do not do this on macOS since the popped-up changelog window cannot be closed sometimes
    if platform.system() in ['Windows', 'Linux']:
        if wl_main.settings_custom['1st_startup']:
            wl_main.help_changelog()

            wl_main.settings_custom['1st_startup'] = False

    wl_main.showMaximized()

    sys.exit(wl_app.exec_())
    