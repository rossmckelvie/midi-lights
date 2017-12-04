import argparse
import logging
import config
from mido import MidiFile
import os
from pathlib2 import Path
import multiprocessing
from subprocess import Popen
import time

parser = argparse.ArgumentParser()

parser.add_argument('--loglevel', default='INFO', help='Log level. Defaults to INFO')
parser.add_argument('--midi', required=True, help='Path the midi file to read', default='./music/carol_of_the_bells.midi')
parser.add_argument('--song', required=True, help='Path the music file to read', default='./music/carol_of_the_bells.wav')
parser.add_argument('--song-delay', help='Seconds to delay start of the song', default=0, type=float)

args = parser.parse_args()

logging.basicConfig(
    level=args.loglevel,
    format='[%(levelname)s] (%(processName)-10s) %(message)s',
)


class MidiPlayer(object):
    def __init__(self):
        self.config = config.Config()
        self.start_time = None

    def run(self, midi_path, song_path, song_delay):
        logging.debug("Master process starting")

        # Validate input files
        for file_path in [midi_path, song_path]:
            if not Path(file_path).is_file():
                msg = "%s is not a file.". format(file_path)
                logging.error(msg)
                raise RuntimeError("msg")

        # Open Midi File
        mid = MidiFile(midi_path)

        processes = {
            'midi': multiprocessing.Process(
                name='MidiLights',
                target=self.process_midi,
                args=(mid,)
            ),

            'song': multiprocessing.Process(
                name='SongPlayer',
                target=self.process_song,
                args=(song_path, song_delay)
            )
        }

        # Start processes
        self.start_time = time.time()
        [process.start() for process in processes.values()]

        # Catch keyboard interrupt
        while multiprocessing.active_children():
            try:
                time.sleep(0.1)
            except KeyboardInterrupt:
                logging.error("Killing processes")
                [process.terminate() for process in processes.values()]

    def process_midi(self, midi_file):
        logging.debug("Starting MIDI processing: {}".format(midi_file))

        t = 0
        for msg in midi_file:
            t += msg.time
            time.sleep(msg.time)

            now = time.time()

            if msg.is_meta:
                logging.debug("Meta midi message: {}".format(msg))
                continue
            logging.debug("Message: {}".format(msg))

            note_str = self.config.get_note_str(msg.note)
            note_enabled = str(msg.type) == str('note_on')

            logging.info({
                't': t,
                'time': now - self.start_time,
                'note_str': note_str,
                'note_enabled': note_enabled
            })

        logging.debug("Midi processing complete")

    def process_song(self, song_path, song_delay):
        logging.info("Playing song: {} in {} seconds".format(song_path, song_delay))
        time.sleep(song_delay)

        command = self.play_mp3_command(song_path)
        logging.info("Music Player detected: {}".format(command))

        t = time.time()
        music_player = Popen(command, shell=True)

        while not music_player.poll():
            now = time.time()
            logging.info({'t': time.time() - t, 'time': now - self.start_time})

            time.sleep(1)

        logging.debug("Song processing complete")

    @staticmethod
    def play_mp3_command(song_path):
        file_name, file_extension = os.path.splitext(song_path)

        """
        Generate the command based on file extension
        :param file_extension:
        :return: string command to execute for Popen
        """
        player_map = {
            '.wav': 'aplay {}'.format(song_path),
            '.mp3': 'mpg123 {}'.format(song_path)
        }

        if file_extension not in player_map.keys():
            raise RuntimeError("Player for %s not configured.".format(file_extension))

        return player_map[file_extension.lower()]


if __name__ == "__main__":
    player = MidiPlayer()
    player.run(args.midi, args.song, args.song_delay)
