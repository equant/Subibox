from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
from kivy.uix.widget import Widget

from kivy.properties import StringProperty

import sqlite3
import random

import musicSearch
#from mutagen.easyid3 import EasyID3

search   = musicSearch.MusicSearch()
analyzer = musicSearch.Analyzer()


# Create both screens. Please note the root.manager.current: this is how
# you can control the ScreenManager from kv. Each screen has by default a
# property manager that gives you the instance of the ScreenManager used.
Builder.load_string("""
<AlbumScreen>:
    GridLayout:
        id: layout
        rows: 3
        Button:
            text: 'A'
        Button:
            text: 'B'
        Button:
            text: 'C'
        Button:
            text: '!'
        Button:
            text: '@'
        Button:
            text: '#'
        Button:
            text: 'x'
        Button:
            text: 'y'
        Button:
            text: 'Back To Main Menu'
            on_release: root.manager.current = 'menu'

<SearchScreen>:
    BoxLayout:
        Label:
            text: 'Test'
        Button:
            text: 'Goto settings'
            on_release: root.manager.current = 'settings'
        Button:
            text: 'View Album Screen'
            on_release: root.manager.current = 'albums'

<SettingsScreen>:
    BoxLayout:
        Button:
            text: 'Useless button'
        Button:
            text: 'Back to main screen'
            on_release: root.manager.current = 'menu'
""")


class ProtoScreen(Screen):

    def handle_input(self, input_string):
        #print("Key!")
        pass


class SearchScreen(ProtoScreen):
    search_string = StringProperty()

    def handle_input(self, input_string):
        self.search_string += input_string
        print("Here it is: {}".format(self.search_string))
        print("Here it is analyzed: {}".format(analyzer.analyze(self.search_string)))
        search.search(self.search_string)


    def on_enter(self):
        self.search_string = ""


class SettingsScreen(ProtoScreen):
    pass

class AlbumScreen(ProtoScreen):
    def on_enter(self):
        grid_layout_widget = self.ids.layout
        print("Rows: {}".format(grid_layout_widget.rows))
        for button in self.walk():
            print("{} -> {}".format(button, button.id))
            button.color = [random.random() for _ in range(3)] + [1]


class SubiboxApp(App):

    def build(self):
        # Create the screen manager
        self.sm = ScreenManager()
        self.sm.transition = FadeTransition()
        self.sm.add_widget(SearchScreen(name='menu'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        self.sm.add_widget(AlbumScreen(name='albums'))
        Window.bind(on_key_down=self._on_keyboard_down)
        self._connect_to_database()
        return self.sm

    def _on_keyboard_down(self, *args):
        #print("Got a key down event: {}".format(args))
        self.sm.current_screen.handle_input(args[3])
        return True

    def _connect_to_database(self):
        try:
            dsn = 'dbTools/id3.sqlite'
            self.database = sqlite3.connect(dsn)
            self.database.row_factory = sqlite3.Row
            self.database.text_factory = str
        except:
            print("Database totally didn't work. :(")


if __name__ == '__main__':
    SubiboxApp().run()
