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
        self.chaptersidebar = objects['chaptersidebar']
        self.commands = {
            'e': (self.export, 'Export the text to custom format')
        }

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
            arg, chapter = arg.rsplit(':',1)
            if not chapter:
                self.error('No chapter specified')
                return
            text = self.chaptersidebar.get_chapter_text(int(chapter))
            if not text:
                return
        # Otherwise the whole text
        else:
            text = self.textarea.toPlainText()

        if not arg in self.settings['formats']:
            self.error('Export format not recognized')
        else:
            for x in self.settings['formats'][arg]:
                if len(x) == 2:
                    text = re.sub(x[0], x[1], text)
                elif len(x) == 3:
                    text = replace_in_selection(x[0], x[1], x[2], text)
            clipboard = QtGui.QApplication.clipboard()
            clipboard.setText(text.strip('\n\t '))
            self.print_('Text exported to clipboard')

def replace_in_selection(rx, rep, selrx, text):
    chunks = []
    selections = re.finditer(selrx, text)
    for sel in selections:
        x = re.sub(rx, rep, sel.group(0))
        chunks.append((sel.start(), sel.end(), x))
    # Do this backwards to avoid messing up the positions of the chunks
    for start, end, payload in chunks[::-1]:
        text = text[:start] + payload + text[end:]
    return text
