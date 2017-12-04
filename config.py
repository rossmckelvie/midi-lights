class Config(object):

    def get_note_str(self, midi_numerical_note):
        return {
            '60': 'C3',
            '62': 'D3',
            '64': 'E3',
            '65': 'F3',
            '67': 'G3',
            '69': 'A3',
            '71': 'B3',
            '72': 'C4',
            '74': 'D4',
            '76': 'E4',
            '77': 'F4',
            '79': 'G4',
            '81': 'A4',
            '83': 'B4',
            '84': 'C5',
            '86': 'D5',
            '88': 'E5',
            '89': 'F5',
            '91': 'G5',
            '93': 'A5',
            '95': 'B5',
            '96': 'C6',
            '98': 'D6',
            '100': 'E6',
            '101': 'E6'
        }[str(midi_numerical_note)]

    def channels_for_note(self, note_str):
        return {
            'C3': [1],  # C3
            'D3': [2],  # D3
            'E3': [3],  # E3
            'F3': [4],  # F3
            'G3': [5],  # G3
            'A3': [6],  # A3
            'B3': [7],  # B3
            'C4': [8],  # C4
            'D4': [1, 2],  # D4
            'E4': [3, 4],  # E4
            'F4': [5, 6],  # F4
            'G4': [7, 8],  # G4
            'A4': [1, 3],  # A4
            'B4': [2, 4],  # B4
            'C5': [5, 7],  # C5
            'D5': [6, 8],  # D5
            'E5': [1, 8],  # E5
            'F5': [2, 7],  # F5
            'G5': [3, 6],  # G5
            'A5': [1, 2, 3, 4, 5, 6, 7, 8],  # A5
            'B5': [2, 3, 4, 5, 6, 7],  # B5
            'C6': [3, 4, 5, 6],   # C6
            'D6': [1, 2, 3, 6, 7, 8],  # D6
            'E6': [1, 4, 5, 8]  # E6
        }[note_str]

