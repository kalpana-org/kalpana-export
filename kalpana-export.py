import os.path
import re

from PyQt4 import QtCore, QtGui

from libsyntyche.common import read_json, parse_stylesheet, read_file, make_sure_config_exists
from pluginlib import GUIPlugin


class UserPlugin(GUIPlugin):
    def __init__(self, objects, get_path):
        super().__init__(objects, get_path)
        self.pluginpath = get_path()
        self.configpath = objects['settings manager'].get_config_directory()
        self.textarea = objects['textarea']
        self.chapterplugin = self.get_chapter_plugin(objects['plugins'])
        self.commands = {
            'e': (self.export, 'Export the text to custom format')
        }

    def get_chapter_plugin(self, plugins):
        for name, p in plugins:
            if name == 'kalpana-chapters':
                return p

    def read_config(self):
        configfile = os.path.join(self.configpath, 'kalpana-export.conf')
        make_sure_config_exists(configfile, os.path.join(self.pluginpath, 'default_config.json'))
        self.settings = read_json(configfile)

    def export(self, arg):
        if not arg:
            self.error('No export format specified')
            return
        # Get a specific chapter to export
        if re.match(r'.+?:(\d+)$', arg):
            if not self.chapterplugin:
                self.error('Chapter plugin not detected')
                return
            arg, chapter = arg.rsplit(':',1)
            if not chapter:
                self.error('No chapter specified')
                return
            text = self.chapterplugin.get_chapter_text(int(chapter))
            if not text:
                return
        # Otherwise the whole text
        else:
            text = self.textarea.toPlainText()

        if not arg in self.settings['formats']:
            self.error('Export format not recognized')
        else:
            for rx, rep in self.settings['formats'][arg]:
                text = re.sub(rx, rep, text)
            clipboard = QtGui.QApplication.clipboard()
            clipboard.setText(text.strip('\n\t '))
            self.print_('Text exported to clipboard')
