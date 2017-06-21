from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.core.window import Window
#from kivy.uix.widget import Widget
import numpy as np

from kivy.properties import StringProperty, ListProperty #, ObjectProperty

emulate_rotary_dial = True

import sqlite3
import random

import SubiSearch
import SubiPlay
from RotaryDial import RotaryDial
#from mutagen.easyid3 import EasyID3

musicSearch = SubiSearch.Search()
musicPlay   = SubiPlay.Play()
analyzer    = SubiSearch.StringAnalyzer()
dial        = RotaryDial()

def rgb_to_color_list(rgb_string, alpha=1.):
    """
    "#FFFFFF" -> (1.0, 1.0, 1.0, 1.0)
    "000000"  -> (0.0, 0.0, 0.0, 1.0)
    """
    if rgb_string[0] == '#':
        c = rgb_string[1:]
    else:
        c = rgb_string
    return [int(c[i:i+2],16)/255 for i in range(0, len(c), 2)] + [alpha]


# Create both screens. Please note the root.manager.current: this is how
# you can control the ScreenManager from kv. Each screen has by default a
# property manager that gives you the instance of the ScreenManager used.
Builder.load_string("""
<SubiLabel>:
    text: "Foo"
    font_size: 96
#    canvas:
#        Color:
#            rgba: self.background_color
#        Rectangle:
#            pos: self.pos  # incorrect
#            size: self.size

<AlbumArt>:
    source: 'assets/images/default_cover.jpg'
    orientation: "vertical"
    Image:
        id: album_image
        source: self.source
        SubiLabel:
            id: dial_label
            font_size: self.parent.height/3
            pos_hint: {'x': 0.5, 'y': 0}
            #size_hint_y: None
            #size_hint_x: None
            #width: self.parent.width
            #height: self.parent.height
            outline_color: [0,1,0,1]
            outline_width: 3

        
<AlbumScreen>:
    id: album_screen
    spacing: 10
    padding: 10
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
        id: layout
        orientation: 'vertical'
        Label:
            text: ''
        Label:
            id: search_string_label
            text: 'Dial Something...'
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
#class AlbumArt(BoxLayout):
    def build(self):
        return self


class SubiLabel(Label):
    default_background_color = [1,1,1,0.5]
    default_color = [1,1,1,1]
    background_color = ListProperty([1,1,1,0.5])
    #text = StringProperty("A")
    def build(self):
        return self


class ProtoScreen(Screen):

    def handle_input(self, input_string):
        pass


class LibraryScreen(ProtoScreen):
    """
    search list contains a list of search strings.  It is a list because the rotary dial interface results in multiple search string
    possibilities...
        foo = RotaryDial.RotaryDial()
        search_list = []
        search_list = foo.appendNumberToList("3", search_list)
        search_list = foo.appendNumberToList("9", search_list)
        search_list = foo.appendNumberToList("5", search_list)
        In [24]: search_list
        Out[24]:
        ['dwj',
         'dwl',
         'dw5',
         'dxk',
         'dxl',
         'dx5',
         'dyk',
         'dyl',
         ...

    """
    search_list      = ListProperty()
    search_string    = StringProperty()
    last_result_df   = None  # This is a Pandas dataframe( 'name', 'id', 'score' )
    last_artist_name = StringProperty()  # This is a Pandas dataframe( 'name', 'id', 'score' )

    def __init__(self, *args, **kwargs):
        print("Begin Library Screen init()")
        super(LibraryScreen, self).__init__(*args, **kwargs)
        self.bind(last_artist_name=self.set_search_label)
        print("End Library Screen init()")

    def on_pre_enter(self):
        print("Begin Library Screen on_pre_enter()")
        self.search_string    = ""
        self.search_list      = []
        self.last_result_df   = None
        self.last_artist_name = ""
        print("End Library Screen on_pre_enter()")

    def handle_input(self, input_string):

        do_search = False

        if input_string is None:
            # User pressed Return
            self.switch_to_album_screen()
            return

        if emulate_rotary_dial:
            if input_string in "23456789":
                print("DEBUG: rotary input: {}".format(input_string))
                self.search_list = dial.rotaryNumberToList(input_string, self.search_list)
                do_search = True
            if input_string == "1":
                self.switch_to_album_screen()
                return
        else:
            if input_string.isalpha():
                self.search_list[0] += input_string
                do_search = True

        if do_search:
            result = musicSearch.artist_search(self.search_list)
            if result is None:
                self.search_list = []
                self.last_result_df = None
            else:
                self.last_result = result
                self.last_artist_name = result['name'][0]


    # -- bound to self.last_artist_name
    def set_search_label(self, instance, value):
        self.ids.search_string_label.text = value
        
    # -- Due to pressing "enter" in self.handle_input()
    def switch_to_album_screen(self):
        artist_id = self.last_result['id'][0]
        self.manager.get_screen('albums').albums = musicSearch.get_artist_albums(int(artist_id))
        self.manager.current = 'albums'

class SettingsScreen(ProtoScreen):
    pass


class AlbumScreen(ProtoScreen):
    """
    Album Dataframe: id, full_album_name, album_year, album_path, album_art
    """

    albums      = None
    album_pages = None
    page = 0


    def __init__(self, *args, **kwargs):
        super(AlbumScreen, self).__init__(*args, **kwargs)

    def handle_input(self, input_string):
        if input_string is None:
            # Ignore return keypresses.
            return
        if input_string in "12345678":
            album = self.album_pages[self.page].iloc[int(input_string)-1]
            album_name = album[1]
            album_path = album[3]
            print("[DEBUG] AlbumScreen.handle_input(): play: {}".format(album_name))
            print("[DEBUG] AlbumScreen.handle_input(): play: {}".format(album_path))
            musicPlay.play_album(album_path)
        if input_string == "9": 
            print("Next Page")
            self.page += 1
            if self.page >= len(self.album_pages):
                self.page = 0
            self.do_album_grid()
        if input_string == "0": 
            print("Should go To Operator Screen!")
            self.manager.current = 'library'


    def on_pre_enter(self):
        self.make_album_pages()
        self.do_album_grid()


    def do_album_grid(self):
        if self.album_pages is None:
            self.make_album_pages()
        grid_layout_widget = self.ids.album_layout
        for album_widget, i in zip(reversed(grid_layout_widget.children), range(len(grid_layout_widget.children))):
            print("Widget: {}, albums on this page: {}".format(i, len(self.album_pages[self.page])))
            if len(self.album_pages[self.page]) > i:
                image_path = self.album_pages[self.page].album_art.iloc[i]
                if len(image_path) > 3:
                    album_widget.ids['album_image'].source = image_path
                    album_widget.ids['dial_label'].text    = str(i+1)
                    colors = musicSearch.get_album_colors(self.album_pages[self.page].id.iloc[i])
                    album_widget.ids['dial_label'].background_color = rgb_to_color_list(colors.color[1], 0.5)
                    #album_widget.ids['dial_label'].color = [1,1,1,1]
                    c = 1 - np.array(rgb_to_color_list(colors.color[1], 0.2))
                    #album_widget.ids['dial_label'].color = rgb_to_color_list(colors.color[2], 0.9)
                    album_widget.ids['dial_label'].color =  c
                    album_widget.ids['dial_label'].outline_color =  rgb_to_color_list(colors.color[1], 0.9)
                    album_widget.ids['album_image'].color  = [1,1,1,1]
                else:
                    self.clear_album_widget(album_widget)
                    album_widget.ids['dial_label'].text    = str(i+1)
                    album_widget.ids['dial_label'].color = [1,1,1,1]
                    album_widget.ids['dial_label'].outline_color =  [.9,.9,.9, 1]
            else:
                self.clear_album_widget(album_widget)
                #album_widget.ids['album_image'].source = ""
                #album_widget.ids['album_image'].color = [0,0,0,1]
                #album_widget.ids['dial_label'].text = ""
        # Last button is next button:
        if len(self.album_pages) > self.page:
            album_widget.ids['dial_label'].text = "Next"
            album_widget.ids['dial_label'].color = [1,1,1,1]
            album_widget.ids['dial_label'].outline_color =  [.9,.9,.9, 1]

    def clear_album_widget(self, a):
        a.ids['album_image'].source = ""
        a.ids['album_image'].color = [0,0,0,1]
        a.ids['dial_label'].text = ""
        a.ids['dial_label'].background_color = a.ids['dial_label'].default_background_color
        a.ids['dial_label'].color = a.ids['dial_label'].default_color

    def make_album_pages(self, n=8):
        """
        a : The array
        n : number of albums per pages

        This splits the album array/list into pages...
        a = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
        make_album_pages(a)
        [[1, 2, 3, 4, 5, 6, 7, 8, 9],
         [10, 11, 12, 13, 14, 15, 16, 17, 18],
         [19, 20]]

        What this code does...
        (1) Split albums up into pages of 8 albums.

        What we may want to do in the future...
            Next *and* Back?  Dynamically only if needed.  Mabye back only if there are > x albums?
        """
        n = 8   # Number of albums per page.
        a = self.albums
        pages = [a[x:x+n] for x in range(0, len(a), n)]
        self.album_pages = pages
        return




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
        print("Building SubiboxApp")
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
