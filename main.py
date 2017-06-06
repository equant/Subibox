from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
from kivy.uix.widget import Widget

from kivy.properties import StringProperty, ListProperty, ObjectProperty

import sqlite3
import random

import MusicSearch
#from mutagen.easyid3 import EasyID3

musicSearch = MusicSearch.Search()
analyzer    = MusicSearch.StringAnalyzer()


# Create both screens. Please note the root.manager.current: this is how
# you can control the ScreenManager from kv. Each screen has by default a
# property manager that gives you the instance of the ScreenManager used.
Builder.load_string("""
<AlbumScreen>:
    id: album_screen
    GridLayout:
        id: button_layout
        rows: 3
        Button:
            text: '$'
        Button:
            text: '%'
        Button:
            text: 'C'
        Button:
            text: '!'
        Button:
            text: '@'
        Button:
            text: 'F'
        Button:
            text: '#'
        Button:
            text: '*'
        Button:
            id: next_button
            text: 'Back To Main Menu'
            on_release: root.manager.current = 'menu'

<LibraryScreen>:
    id: library_screen
    BoxLayout:
        orientation: 'vertical'
        Label:
            text: ''
        Label:
            id: search_string_label
            text: 'Type Something...'
            font_size: 48
        Label:
            text: ''
#        Button:
#            text: 'Goto settings'
#            on_release: root.manager.current = 'settings'
#        Button:
#            text: 'View Album Screen'
#            on_release: root.manager.current = 'albums'

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


class LibraryScreen(ProtoScreen):
    search_string    = StringProperty()
    last_result_df   = None  # This is a Pandas dataframe( 'name', 'id', 'score' )
    last_artist_name = StringProperty()  # This is a Pandas dataframe( 'name', 'id', 'score' )

    def __init__(self, *args, **kwargs):
        super(LibraryScreen, self).__init__(*args, **kwargs)
        self.bind(last_artist_name=self.set_search_label)

    def handle_input(self, input_string):
        if input_string is None:
            self.manager.get_screen('albums').albums = ["poop", "ship", "destroyer"] + [self.last_result['name'][0]]
            #self.manager.ids.album_screen.albums = ["poop", "ship", "destroyer"] + [self.last_result]
            self.manager.current = 'albums'
        else:
            self.search_string += input_string
        result = musicSearch.artist_search(self.search_string)
        if result is None:
            self.search_string = ""
        else:
            self.last_result = result
            self.last_artist_name = result['name'][0]

    def set_search_label(self, instance, value):
        #print("HERE WE ARE: {}".format(value))
        self.ids.search_string_label.text = value


    def on_pre_enter(self):
        self.search_string = ""
        

class SettingsScreen(ProtoScreen):
    pass


class AlbumScreen(ProtoScreen):
    albums = ListProperty()
    def on_enter(self):
        grid_layout_widget = self.ids.button_layout
        print("Rows: {}".format(grid_layout_widget.rows))
        for button in self.walk():
            print("{} -> {}".format(button, button.id))
            button.color = [random.random() for _ in range(3)] + [1]
        for button, string in zip(reversed(self.ids.button_layout.children), self.albums):
            button.text = string
            print("BUTTON DEBUG: {} : {}".format(button, string))
        #self.ids.layout.ids.foo.text = self.albums[-1] 
        if len(self.albums) > 0:
            print(self.albums)


class MyManager(ScreenManager):
    def get_screen(self, name):
        for _ in self.screens:
            print("Looking for screen: {} / {}".format(name, _.name))
            if _.name == name:
                return _
        return None



class SubiboxApp(App):

    def get_screen(self, name):
        for _ in self.sm.screens:
            print("Looking for screen: {} / {}".format(name, _.name))
            if _.name == name:
                return _
        return None


    def build(self):
        # Create the screen manager
        self.sm = ScreenManager()
        self.sm.transition = FadeTransition()
        self.sm.add_widget(LibraryScreen(name='menu'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        self.sm.add_widget(AlbumScreen(name='albums'))
        Window.bind(on_key_down=self._on_keyboard_down)
        return self.sm

    def _on_keyboard_down(self, *args):
        print("Got a key down event: {}".format(args))
        self.sm.current_screen.handle_input(args[3])
        return True


if __name__ == '__main__':
    SubiboxApp().run()
