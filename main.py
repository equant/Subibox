from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
#from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.core.window import Window
#from kivy.uix.widget import Widget

from kivy.properties import StringProperty, ListProperty #, ObjectProperty

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
<SubiLabel>:
    text: "Foo"
    font_size: 48
    canvas:
        Color:
            rgba: [1,0,0,0.5]
        Rectangle:
            pos: self.pos  # incorrect
            size: self.size

<AlbumArt>:
    source: 'assets/images/default_cover.jpg'
    orientation: "vertical"
    Image:
        id: album_image
        source: self.source
        #y: self.parent.y + self.parent.height - 200
        #x: self.parent.x
    SubiLabel:
        id: dial_label
        #size_hint_y: None
        #height: 110
        pos_hint: {'x': 0, 'y': 0}
        size_hint_y: 0.15
        size_hint_x: 0.15

        
<AlbumScreen>:
    id: album_screen
    GridLayout:
        id: album_layout
        rows: 3

        AlbumArt:
            id: 1
            text: "1"
        AlbumArt:
            id: 2
            text: "2"
        AlbumArt:
            id: 3
            text: "3"

        AlbumArt:
            id: 4
            text: "4"
        AlbumArt:
            id: 5
            text: "5"
        AlbumArt:
            id: 6
            text: "6"

        AlbumArt:
            id: 7
            text: "7"
        AlbumArt:
            id: 8
            text: "8"
        AlbumArt:
            id: 9
            text: "9"

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

class AlbumArt(RelativeLayout):
    def build(self):
        return self


class SubiLabel(Label):
    #background_color = ListProperty([1,0,0,0.8])
    #text = StringProperty("A")
    def build(self):
        return self


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

    def on_pre_enter(self):
        self.search_string = ""

    def handle_input(self, input_string):

        if input_string is None:
            self.switch_to_album_screen()
            return

        self.search_string += input_string
        result = musicSearch.artist_search(self.search_string)
        if result is None:
            self.search_string = ""
        else:
            self.last_result = result
            self.last_artist_name = result['name'][0]


    # -- bound to self.last_artist_name
    def set_search_label(self, instance, value):
        self.ids.search_string_label.text = value
        
    # -- Due to pressing "enter" in self.handle_input()
    def switch_to_album_screen(self):
        print("DEBUG: MS: {}".format(self.last_result_df))
        self.manager.get_screen('albums').albums = musicSearch.get_artist_albums(5)
        self.manager.current = 'albums'

class SettingsScreen(ProtoScreen):
    pass


class AlbumScreen(ProtoScreen):
    """
    Album Dataframe: id, full_album_name, album_year, album_path, album_art
    """

    albums      = None
    album_pages = None
    page = 1

    def __init__(self, *args, **kwargs):
        super(AlbumScreen, self).__init__(*args, **kwargs)
        #self.bind(albums=self.new_albums)

    def handle_input(self, input_string):
        if input_string in "123456789":
            print("PLAY: {}".format(self.album_pages.iloc[int(input_string)-1][1]))
        if input_string == "0": 
            print("Should go To Operator Screen!")
            self.manager.current = 'library'


    def on_pre_enter(self):
        if self.album_pages is None:
            self.make_album_pages(self.albums)
        grid_layout_widget = self.ids.album_layout
        #for button, string in zip(reversed(self.ids.button_layout.children), self.albums):
        for album_widget, i in zip(reversed(grid_layout_widget.children), range(len(grid_layout_widget.children))):
            pass
            #print("DEBUG: album_pages: {}".format(self.album_pages))
            #if self.album_pages.iloc[i] is not None:
                #album_widget.ids['album_image'].source = self.album_pages.iloc[i][4]
                #album_widget.ids['dial_label'].text = str(i+1)

    def new_albums(self, a, b):
        print("DEBUG: Running bind method for AlbumScreen.albums")
        self.album_pages = self.albums[0:9]
        #self.album_pages = self.make_album_pages(self.albums)

    def make_album_pages(self, a):
        """
        This splits the album array/list into pages...
        a = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
        make_album_pages(a)
        [[1, 2, 3, 4, 5, 6, 7, 8, 9],
         [10, 11, 12, 13, 14, 15, 16, 17, 18],
         [19, 20]]
        """
        #n = 9   # Number of albums per page.
        #pages = [a[x:x+n] for x in range(0, len(a), n)]
        #self.album_pages = pages
        print("DEBUG: Making album pages")
        print("albums: {}".format(self.albums))
        print("album_pages: {}".format(self.album_pages))
        self.album_pages = self.albums[0:9]
        return

    def set_albums(self, albums):
        for button, i in zip(grid_layout_widget.children, range(len(grid_layout_widget.children))):
            if albums.iloc[i] is not None:
                button.text = albums.iloc[i][1]



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
        self.sm.add_widget(LibraryScreen(name='library'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        self.sm.add_widget(AlbumScreen(name='albums'))
        Window.bind(on_key_down=self._on_keyboard_down)
        return self.sm

    def _on_keyboard_down(self, *args):
        #print("Got a key down event: {}".format(args))
        self.sm.current_screen.handle_input(args[3])
        return True


if __name__ == '__main__':
    SubiboxApp().run()


# CRUFT

#for button in self.walk():
#    #print("{} -> {}".format(button, button.id))
#    button.color = [random.random() for _ in range(3)] + [1]
