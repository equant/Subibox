import time, random, sqlite3
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
import numpy as np

from kivy.properties import StringProperty, ListProperty, DictProperty, ObjectProperty

from kivy.core.text import LabelBase
LabelBase.register(name       = "Avenir",
                   fn_regular = "assets/avenir.ttf")
LabelBase.register(name       = "paraaminobenzoic",
                   fn_regular = "assets/paraaminobenzoic.ttf")

emulate_rotary_dial = True

import SubiSearch
import SubiPlay
from RotaryDial import RotaryDial

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print('{} function took {:0.3f} ms'.format(f.__name__, (time2-time1)*1000.0))
        return ret
    return wrap

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


Builder.load_string("""
<SubiLabel>:
    text: "Foo"
    font_size: 96
    font_name: "paraaminobenzoic"
#    canvas:
#        Color:
#            rgba: self.background_color
#        Rectangle:
#            pos: self.pos  # incorrect
#            size: self.size

<AlbumScreen>:
    id: album_screen
    spacing: 10
    padding: 10
    GridLayout:
        id: album_layout
        rows: 3


<PlayingScreen>:
    id: playing_screen
    BoxLayout:
        id: layout
        orientation: 'vertical'
        Label:
            id: artist
            text: self.parent.parent.artist
            font_size: 48
            font_name: "Avenir"
        Label:
            id: album
            text: self.parent.parent.album
            font_size: 48
            font_name: "Avenir"
        Label:
            id: title
            text: self.parent.parent.title
            font_size: 48
            font_name: "Avenir"

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
            font_name: "Avenir"
        Label:
            text: ''

<SettingsScreen>:
    BoxLayout:
        Button:
            text: 'Useless button'
        Button:
            text: 'Back to main screen'
            on_release: root.manager.current = 'menu'
""")

class SubiLabel(Label):
    default_background_color = [1,1,1,0.5]
    default_color = [1,1,1,1]
    background_color = ListProperty([1,1,1,0.5])
    #text = StringProperty("A")
    def build(self):
        return self

class Album(RelativeLayout):
    album = DictProperty()
    
    def __init__(self, *args, **kwargs):
        super(Album, self).__init__(*args, **kwargs)
        self.bind(album=self.album_changed)

    def build(self):
        return self

    def album_changed(self, instance, value):
        if len(self.album['album_art']) > 0:
            # There is an album cover image
            ac = self.album['album_art'].replace('/mnt/jukebox/','/home/equant/')
            print("Found album cover: {}".format(ac))
            album_cover = Image(source=ac, id='album_cover')
        else:
            print("Found no album cover")
            album_cover = Label(text=self.album['full_album_name'], id='album_cover')
            # There is not album cover image
        self.add_widget(album_cover)
        return


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
    last_result_df   = None  # This is not a Pandas dataframe( 'name', 'id', 'score' ) anymore.
    last_artist_name = StringProperty()  # This is a Pandas dataframe( 'name', 'id', 'score' )

    def __init__(self, *args, **kwargs):
        super(LibraryScreen, self).__init__(*args, **kwargs)
        self.bind(last_artist_name=self.set_search_label)

    def on_pre_enter(self):
        self.search_string    = ""
        self.search_list      = []
        self.last_result_df   = None
        self.last_artist_name = ""

    @timing
    def handle_input(self, input_string):

        do_search = False

        if input_string is None:
            # User pressed Return
            self.switch_to_album_screen()
            return

        if emulate_rotary_dial:
            if input_string in "23456789":
                print("DEBUG: rotary input: {}".format(app))
                self.search_list = app.dial.rotaryNumberToList(input_string, self.search_list)
                do_search = True
            if input_string == "1":
                self.switch_to_album_screen()
                return
        else:
            if input_string.isalpha():
                self.search_list[0] += input_string
                do_search = True

        if do_search:
            result, self.search_list = app.musicSearch.artist_search(self.search_list)
            if result is None:
                self.search_list = []
                self.last_result_df = None
            else:
                self.last_result = result
                self.last_artist_name = result[0]['name']


    # -- bound to self.last_artist_name
    #@timing
    def set_search_label(self, instance, value):
        self.ids.search_string_label.text = value
        
    # -- Due to pressing "enter" in self.handle_input()
    def switch_to_album_screen(self):
        artist_id = self.last_result[0]['id']
        self.manager.get_screen('albums').albums = app.musicSearch.get_artist_albums(int(artist_id))
        self.manager.current = 'albums'

class SettingsScreen(ProtoScreen):
    pass



class AlbumScreen(ProtoScreen):
    """
    Album Dataframe: id, full_album_name, album_year, album_path, album_art
    """

    albums      = ObjectProperty()
    album_pages = None
    page = 0
    album_widgets = []


    def __init__(self, *args, **kwargs):
        super(AlbumScreen, self).__init__(*args, **kwargs)
        self.bind(albums=self.update_albums)

    def handle_input(self, input_string):
        if input_string is None:
            # Ignore return keypresses.
            return
        if input_string in "12345678":
            if int(input_string) <= len(self.album_pages[self.page]):
                album = self.album_pages[self.page][int(input_string)-1]
                album_name = album['full_album_name']
                album_path = album['album_path']
                #print("[DEBUG] AlbumScreen.handle_input(): play: {}".format(album_name))
                #print("[DEBUG] AlbumScreen.handle_input(): play: {}".format(album_path))
                app.musicPlay.play_album(album_path)
                self.manager.current = 'playing'
        if input_string == "9": 
            #print("Next Page")
            self.page += 1
            if self.page >= len(self.album_pages):
                self.page = 0
            self.do_album_grid()
        if input_string == "0": 
            print("Should go To Operator Screen!")
            self.manager.current = 'library'


    #def on_pre_enter(self):
        #self.make_album_pages()
        #self.do_album_grid()

#    def do_album_grid(self):
#        if self.album_pages is None:
#            self.make_album_pages()
#        grid_layout_widget = self.ids.album_layout
#        for album_widget, i in zip(reversed(grid_layout_widget.children), range(len(grid_layout_widget.children))):
#            #print("Widget: {}, albums on this page: {}".format(i, len(self.album_pages[self.page])))
#            if len(self.album_pages[self.page]) > i:
#                image_path = self.album_pages[self.page][i]['album_art']
#                if len(image_path) > 3:
#                    album_widget.ids['album_image'].source = image_path
#                    album_widget.ids['dial_label'].text    = str(i+1)
#                    colors = root.musicSearch.get_album_colors(self.album_pages[self.page][i]['id'])
#                    if len(colors) == 3:
#                        album_widget.ids['dial_label'].background_color = rgb_to_color_list(colors[1]['color'], 0.5)
#                        #album_widget.ids['dial_label'].color = [1,1,1,1]
#                        c = 1 - np.array(rgb_to_color_list(colors[1]['color'], 0.2))
#                        #album_widget.ids['dial_label'].color = rgb_to_color_list(colors.color[2], 0.9)
#                        album_widget.ids['dial_label'].color =  c
#                        album_widget.ids['dial_label'].outline_color =  rgb_to_color_list(colors[1]['color'], 0.9)
#                    album_widget.ids['album_image'].color  = [1,1,1,1]
#                else:
#                    self.clear_album_widget(album_widget)
#                    album_widget.ids['dial_label'].text    = str(i+1)
#                    album_widget.ids['dial_label'].color = [1,1,1,1]
#                    album_widget.ids['dial_label'].outline_color =  [.9,.9,.9, 1]
#            else:
#                self.clear_album_widget(album_widget)
#                #album_widget.ids['album_image'].source = ""
#                #album_widget.ids['album_image'].color = [0,0,0,1]
#                #album_widget.ids['dial_label'].text = ""
#        # Last button is next button:
#        if len(self.album_pages) > self.page:
#            album_widget.ids['dial_label'].text = "Next"
#            album_widget.ids['dial_label'].color = [1,1,1,1]
#            album_widget.ids['dial_label'].outline_color =  [.9,.9,.9, 1]
#
#    def clear_album_widget(self, a):
#        a.ids['album_image'].source = ""
#        a.ids['album_image'].color = [0,0,0,1]
#        a.ids['dial_label'].text = ""
#        a.ids['dial_label'].background_color = a.ids['dial_label'].default_background_color
#        a.ids['dial_label'].color = a.ids['dial_label'].default_color

    def clear_album_widgets(self):
        for w in self.album_widgets:
            self.ids.album_layout.remove(w)
        self.album_widgets = []

    def update_albums(self, instance, value):
        self.make_album_pages()
        #self.album_widgets = ListProperty([None]*len(self.album_pages[self.page]))
        #print("FOO: {}".format(self.ids['1']))
        #self.ids['1'].album = self.album_pages[self.page][0]
        #self.ids['2'].album = self.album_pages[self.page][1]
        for idx, album in enumerate(self.album_pages[self.page]):
            a = Album()
            a.album = album
            self.album_widgets.append(a)
            self.ids.album_layout.add_widget(a)

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


class PlayingScreen(ProtoScreen):

    artist = StringProperty()
    album  = StringProperty()
    title   = StringProperty()

    #def __init__(self, *args, **kwargs):
        #super(PlayingScreen, self).__init__(*args, **kwargs)

    def on_pre_enter(self):
        self.current_track_event = Clock.schedule_interval(self.update_track_info, 2.)
    def on_pre_leave(self):
        pass
        self.current_track_event.cancel()


    def handle_input(self, input_string):
        print("PlayScreen.handle_input() got {}".format(input_string))
        if input_string == "1":
            root.musicPlay.pause()
        if input_string == "2":
            self.manager.current = 'albums'
        if input_string == "9":
            root.musicPlay.nextTrack()
        if input_string == "0":
            self.manager.current = 'library'

    def update_track_info(self, event):
        self.current_track_info = root.musicPlay.current_track_info()
        self.artist = self.current_track_info['artist']
        self.album = self.current_track_info['album']
        self.title = self.current_track_info['title']


class MyManager(ScreenManager):
    def get_screen(self, name):
        for _ in self.screens:
            if _.name == name:
                return _
        return None



class SubiboxApp(App):

    def get_screen(self, name):
        for _ in self.sm.screens:
            if _.name == name:
                return _
        return None


    def build(self):
        global app
        app = self
        self.musicSearch = SubiSearch.Search()
        self.musicPlay   = SubiPlay.Play()
        self.dial        = RotaryDial()

        # Create the screen manager
        self.sm = ScreenManager()
        self.sm.transition = FadeTransition()
        self.sm.add_widget(LibraryScreen(name='library'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        self.sm.add_widget(AlbumScreen(name='albums'))
        self.sm.add_widget(PlayingScreen(name='playing'))
        Window.bind(on_key_down=self._on_keyboard_down)
        return self.sm

    def _on_keyboard_down(self, *args):
        self.sm.current_screen.handle_input(args[3])
        return True


if __name__ == '__main__':
    SubiboxApp().run()


# CRUFT

#for button in self.walk():
#    #print("{} -> {}".format(button, button.id))
#    button.color = [random.random() for _ in range(3)] + [1]
