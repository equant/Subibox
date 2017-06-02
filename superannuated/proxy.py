class Proxy():
    playMode  = "lastfm"
    inputMode = "search"
    currentSearchString = ""
    lastfm_scene = ""
    lastfm_menu_scene = ""
    library_scene = ""
    default_startup_scene = lastfm_scene
    #default_font = "Times New Roman"
    default_font = "Avenir LT Std"
    #default_font = "Alte Haas Grotesk"
    #default_font = "Eight Track program 3"
    #default_font = "Day Roman"
    #default_font = "Fontin"
    station_font_size = 64
    track_font_size = 32
    idle = False
    borderPixels = 5


    def test():
        print "this is a test"
        #director.replace( FadeTransition( Proxy.lastfm_scene, duration=1 ) )
