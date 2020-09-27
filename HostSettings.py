import sublime
import sublime_plugin

import socket


class CustomFontListener(sublime_plugin.EventListener):
    hostname = socket.gethostname()

    def on_new(self, view):
        if self.hostname in ("MacBook.local"):
            view.settings().set("font_size", 14)
            view.settings().set("line_padding_bottom", 0)

    on_load = on_new






























