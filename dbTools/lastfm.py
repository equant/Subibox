API_KEY = "10cd7614f283ad5b01c303bd7d0be467"
API_SECRET = "9c42e9f3ef480f6b167c69f4f3b72f43"

last = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)

artist = "Bob Dylan"
foo = last.get_artist(artist).get_top_tags()
foo[0].item.name

for thing in foo:
    print("{} : {}".format(thing.item.name, thing.weight))


