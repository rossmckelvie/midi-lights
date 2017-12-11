import json
from os import path


class Config(object):
    def __init__(self):
        basepath = path.dirname(__file__)
        filepath = path.abspath(path.join(basepath, "..", "config.json"))

        with open(filepath, 'r') as f:
            self.settings = json.load(f)

    def channels_for_note(self, note_str):
        return self.settings['note_channel_map'][note_str]
