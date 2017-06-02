from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.widget import Widget

from kivy.properties import StringProperty

import sqlite3

import musicSearch
#from mutagen.easyid3 import EasyID3

search = musicSearch.MusicSearch()

# Create both screens. Please note the root.manager.current: this is how
# you can control the ScreenManager from kv. Each screen has by default a
# property manager that gives you the instance of the ScreenManager used.
Builder.load_string("""
<AlbumScreen>:
    GridLayout:
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
            text: 'z'
            on_press: root.manager.current = 'menu'

<SearchScreen>:
    BoxLayout:
        Label:
            text: 'Test'
        Button:
            text: 'Goto settings'
            on_press: root.manager.current = 'settings'
        Button:
            text: 'Quit'
            on_press: root.manager.current = 'albums'

<SettingsScreen>:
    BoxLayout:
        Button:
            text: 'My settings button'
        Button:
            text: 'Back to menu'
            on_press: root.manager.current = 'menu'
""")

class MyKeyboardListener(Widget):

    def __init__(self, **kwargs):
        super(MyKeyboardListener, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        if self._keyboard.widget:
            # If it exists, this widget is a VKeyboard object which you can use
            # to change the keyboard layout.
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print('The key', keycode, 'have been pressed')
        print(' - text is %r' % text)
        print(' - modifiers are %r' % modifiers)

        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        if keycode[1] == 'escape':
            keyboard.release()

        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True

class ProtoScreen(Screen):

    def handle_input(self, input_string):
        #print("Key!")
        pass


class SearchScreen(ProtoScreen):
    search_string = StringProperty()

    def handle_input(self, input_string):
        self.search_string += input_string
        print("Here it is: {}".format(self.search_string))

    def on_enter(self):
        self.search_string = ""


class SettingsScreen(ProtoScreen):
    pass

class AlbumScreen(ProtoScreen):
    pass


class SubeboxApp(App):

    def build(self):
        # Create the screen manager
        self.sm = ScreenManager()
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
    SubeboxApp().run()
