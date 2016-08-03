import os.path
import re

from libsyntyche.common import read_json, parse_stylesheet, read_file, make_sure_config_exists

class ExportError(Exception):
    pass

try:
    from pluginlib import GUIPlugin
except ImportError:
    class GUIPlugin:
        pass

class UserPlugin(GUIPlugin):
    def __init__(self, objects, get_path):
        super().__init__(objects, get_path)
        self.pluginpath = get_path()
        self.configpath = objects['settingsmanager'].get_config_directory()
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
        try:
            text = export_chapter(arg, self.textarea.toPlainText,
                                    self.chaptersidebar.get_chapter_text,
                                    self.settings['formats'])
        except ExportError as e:
            self.error(str(e))
        else:
            from PyQt4 import QtGui
            clipboard = QtGui.QApplication.clipboard()
            clipboard.setText(text)
            self.print_('Text exported to clipboard')


def export_chapter(arg, get_text, get_chapter_text, formats):
    if not arg:
        raise ExportError('No export format specified')
    # Get a specific chapter to export
    if re.match(r'.+?:(\d+)$', arg):
        arg, chapter = arg.rsplit(':',1)
        if not chapter:
            raise ExportError('No chapter specified')
        text = get_chapter_text(int(chapter))
        if not text:
            raise ExportError('Nothing to export')
    # Otherwise the whole text
    else:
        text = get_text()
    # Get rid of excess blank lines
    text = re.sub(r'\n(?:[ \t]*\n)+', '\n\n', text)
    # Format the text
    if not arg in formats:
        raise ExportError('Export format not recognized')
    else:
        for x in formats[arg]:
            if len(x) == 2:
                text = re.sub(x[0], x[1], text)
            elif len(x) == 3:
                text = replace_in_selection(x[0], x[1], x[2], text)
        return text.strip('\n\t ')


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
