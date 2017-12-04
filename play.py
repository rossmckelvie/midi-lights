import argparse
import logging
import config
from hardware import Hardware
import json
from mido import MidiFile
import os
from pathlib2 import Path
import signal
from subprocess import Popen
import time

parser = argparse.ArgumentParser()

parser.add_argument('--loglevel', default='INFO', help='Log level. Defaults to INFO')
parser.add_argument('--midi', required=True, help='Path the midi file to read')
parser.add_argument('--song', required=True, help='Path the music file to read')

args = parser.parse_args()

logging.basicConfig(
    level=args.loglevel,
    format='%(asctime)s|%(levelname)s %(message)s',
)

signal.signal(signal.SIGINT, signal.SIG_IGN)


class MidiCommand(object):
    def __init__(self, pre_timeout=0):
        self.changes = {}
        self.timeout = pre_timeout

    def set_channel(self, channel_id, pin_value):
        if channel_id in self.changes.keys():
            logging.warn("Channel already set for command: {}".format({
                'channel_id': channel_id,
                'current_value': self.changes[channel_id],
                'new_value': pin_value
            }))

        self.changes[channel_id] = pin_value


class MidiLights(object):
    def __init__(self, configuration, hrdwr):
        self.config = configuration
        self.start_time = None
        self.hardware = hrdwr

    def run(self, midi_path, song_path):
        logging.info("Reading MIDI: {}".format(midi_path))
        logging.info("Playing Song: {}".format(song_path))

        # Validate input files
        for file_path in [midi_path, song_path]:
            if not Path(file_path).is_file():
                msg = "%s is not a file.". format(file_path)
                logging.error(msg)
                raise RuntimeError("msg")

        # Get Hardware
        hardware = Hardware()

        # Get script
        cached_status, script = self.midi_commands(midi_path)
        hardware.debug_flash(cached_status)

        # Code takes time to execute.. record it here to keep the midi command playback in sync with the music
        time_lost = 0

        # Start play song
        command = self.play_mp3_command(song_path)
        music_player = Popen(command, shell=True)

        # Playback script
        for command in script:
            logging.debug(json.dumps({'command': command.__dict__, 'time_lost': time_lost}))
            t = time.time()

            # Timeout wait, but catch back up in sync
            if command.timeout:
                time_lost_diff = command.timeout - time_lost

                # Sleep or Sync
                if time_lost_diff < 0:  # Time lost > timeout, don't sleep
                    time_lost -= command.timeout
                elif time_lost_diff > 0:  # timeout is greater than time lost, sleep & get in-sync
                    time_lost = 0
                    t += time_lost_diff
                    time.sleep(time_lost_diff)
                else:  # in-sync if we don't sleep
                    time_lost = 0

            # Write pin values out
            for channel, val in command.changes.items():
                hardware.set_channel_value(channel, val)

            # Update time lost
            time_lost += time.time() - t

        # Wait for music to complete
        logging.info("MIDI File complete, waiting for music to finish")
        music_player.wait()

        # Turn all of the lights on to end the show!
        logging.info("Merry Christmas!")
        hardware.set_all_channels_to_value(1)

    def midi_commands(self, midi_path):
        """
        Reads a midi file and generates commands before playing music (I was noticing the lights getting out of sync,
        and computing the list of commands before starting music playback fixed that issue. It was also easy to write
        the list out to a JSON file for caching on subsequent executions.

        :param midi_path:
        :return: (cache_found, MidiCommand[])
        """
        command = None
        script = []

        # Check for cache and return
        cache_path = "{}.script.json".format(midi_path)
        if Path(cache_path).is_file():
            for cmd in json.load(open(cache_path)):
                logging.debug("Loading command from cache: {}".format(cmd))
                command = MidiCommand(cmd['timeout'])
                command.changes = cmd['changes']
                script.append(command)
            return True, script

        # Parse midi file and generate commands
        for msg in MidiFile(midi_path):
            if msg.is_meta:
                logging.debug("Meta midi message: {}".format(msg))
                continue

            if msg.time or not command:
                logging.debug("Writing command: {}".format(command))
                command = MidiCommand(msg.time)
                script.append(command)

            note_str = self.config.get_note_str(msg.note)
            note_enabled = 1 if str(msg.type) == str('note_on') else 0

            channel_ids = map(lambda i: str(i), self.config.channels_for_note(note_str))
            logging.debug({
                'note_str': note_str,
                'note_enabled': note_enabled,
                'channel_ids': channel_ids
            })

            for ch_id in channel_ids:
                command.set_channel(ch_id, note_enabled)
        logging.debug("Script: {}".format(json.dumps([c.__dict__ for c in script])))

        # Write commands to file for caching
        with open(cache_path, 'w') as cache_file:
            json.dump([c.__dict__ for c in script], cache_file)

        return False, script

    @staticmethod
    def play_mp3_command(song_path):
        """
        Generate the command to playback the music, based on file extension
        :param song_path: path to music file
        :return: string command to execute to start playback
        """

        file_name, file_extension = os.path.splitext(song_path)

        player_map = {
            '.wav': 'aplay {}'.format(song_path),
            '.mp3': 'mpg123 {}'.format(song_path)
        }

        if file_extension not in player_map.keys():
            raise RuntimeError("Player for %s not configured.".format(file_extension))

        return player_map[file_extension.lower()]


if __name__ == "__main__":
    hw = Hardware()
    try:
        player = MidiLights(config.Config(), hw)
        player.run(args.midi, args.song)
    except Exception as e:
        logging.error("Exception caught: {}".format(e))
        hw.set_all_channels_to_value(0)
        raise e
