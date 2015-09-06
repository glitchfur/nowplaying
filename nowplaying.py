# HexChat nowplaying plugin
# https://github.com/glitchfur/nowplaying

__module_name__ = "nowplaying"
__module_version__ = "1.0"
__module_description__ = "Prints currently playing Spotify track to channel."

import hexchat
import win32gui
from time import time

# CONFIGURATION
# By default, users can only request what you're listening to every 30 seconds.
# To disable this limitation, set this to False.
timelimit = True

class Spotify:
    def __init__(self):
        try:
            self._hwnd = win32gui.FindWindow("SpotifyMainWindow", None)
        except:
            raise self.SpotifyWindowNotFoundException()

    def getCurrentTrack(self):
        return self._parseWindowTitle()['track']

    def getCurrentArtist(self):
        return self._parseWindowTitle()['artist']

    def isPlaying(self):
        return self.getCurrentArtist() != None

    def _parseWindowTitle(self):
        trackinfo = win32gui.GetWindowText(self._hwnd).split(" - ", 1)

        if len(trackinfo) == 1:
            return {'artist': None, 'track': None}

        artist, track = (trackinfo[0], trackinfo[1])
        return {'artist': artist, 'track': track}

    class SpotifyWindowNotFoundException:
        def __str__(self):
            return "Spotify window not found. Is Spotify really running?"

class NowPlaying:
    def __init__(self):
        self.np_hook = hexchat.hook_server("PRIVMSG", self.spotify)
        self.last_run = 0

    def current_nick(self):
        return hexchat.get_info('nick')

    def get_sender_nick(self, word):
        return word[0].split('!')[0][1:]

    def send(self, msg, action=False):
        if action:
            hexchat.command("me %s" % msg)
        else:
            hexchat.command("say %s" % msg)

    def spotify(self, word, word_eol, userdata):
        msg = ' '.join(word[3:])[1:]
        search_str = "%s now playing" % self.current_nick().lower()
        if msg.lower() == search_str:
            hexchat.prnt("\002\00302%s\017 requested what you are playing!\007" %
                self.get_sender_nick(word))
            if time() - self.last_run < 30 and timelimit:
                self.send("You can only see what I play every 30 seconds!")
                return hexchat.EAT_HEXCHAT
            try:
                s = Spotify()
            except:
                self.send("Can't connect to %s's Spotify." % self.current_nick())
                return
            if s.isPlaying():
                self.send("is listening to \002\00302%s\017 by \002\00302%s\017." %
                    (s.getCurrentTrack(), s.getCurrentArtist()), action=True)
            else:
                self.send("isn't currently playing anything.", action=True)
            self.last_run = time()
            return hexchat.EAT_HEXCHAT

np = NowPlaying()