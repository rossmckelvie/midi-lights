import json


class Config(object):
    def __init__(self):
        with open('config.json', 'r') as f:
            self.settings = json.load(f)

    def get_note_str(self, midi_numerical_note):
        return self.settings['midi_notes'][str(midi_numerical_note)]

    def channels_for_note(self, note_str):
        return self.settings['note_channel_map'][note_str]
