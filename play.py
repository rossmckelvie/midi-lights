import argparse
import logging
import config
from hardware import Command, Hardware
import json
from mido import MidiFile
import os
from pathlib2 import Path
import signal
from subprocess import Popen
import time

signal.signal(signal.SIGINT, signal.SIG_IGN)


class MidiLights(object):
    def __init__(self, configuration, hrdwr, disable_caching=False):
        self.config = configuration
        self.start_time = None
        self.hardware = hrdwr
        self.caching_disabled = disable_caching

    def run(self, midi_path, song_path):
        logging.info("Reading MIDI: {}".format(midi_path))
        logging.info("Playing Song: {}".format(song_path))
        logging.info("Cache: {}".format("Disabled" if self.caching_disabled else "Enabled"))

        # Validate input files
        for file_path in [midi_path, song_path]:
            if not Path(file_path).is_file():
                msg = "%s is not a file.". format(file_path)
                logging.error(msg)
                raise RuntimeError("msg")

        # Get script
        cached_status, script = self.midi_commands(midi_path)

        # Start play song
        mp3_command = self.play_mp3_command(song_path)
        music_player = Popen(mp3_command, shell=True)

        # Playback script
        self.play_script(script)

        # Wait for music to complete
        logging.info("MIDI File complete, waiting for music to finish")
        music_player.wait()

        # Turn all of the lights on to end the show!
        logging.info("Merry Christmas!")
        self.hardware.set_all_channels_to_value(1)

    def play_script(self, script):
        """
        Execute (midi) commands
        :param script:
        :type script: Command[]
        :return: int time_lost
        """
        # Code takes time to execute.. record it here to keep the midi command playback in sync with the music
        time_lost = 0

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
            self.hardware.execute_command(command)

            # Update time lost
            time_lost += time.time() - t

        return time_lost

    def midi_commands(self, midi_path):
        """
        Reads a midi file and generates commands before playing music (I was noticing the lights getting out of sync,
        and computing the list of commands before starting music playback fixed that issue. It was also easy to write
        the list out to a JSON file for caching on subsequent executions.

        :param midi_path:
        :return: (cache_found, Command[])
        """
        command = None
        script = []

        # Check for cache and return
        cache_path = "{}.script.json".format(midi_path)
        if Path(cache_path).is_file() and not self.caching_disabled:
            for cmd in json.load(open(cache_path)):
                logging.debug("Loading command from cache: {}".format(cmd))
                command = Command(cmd['timeout'])
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
                command = Command(msg.time)
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
    c = config.Config()
    hw = Hardware(c)

    parser = argparse.ArgumentParser()

    parser.add_argument('--loglevel', default='INFO', help='Log level. Defaults to INFO')
    parser.add_argument('--midi', required=True, help='Path the midi file to read')
    parser.add_argument('--song', required=True, help='Path the music file to read')
    parser.add_argument('--no-cache', action='store_true', default=False, help='Set to disable caching')

    args = parser.parse_args()

    logging.basicConfig(
        level=args.loglevel,
        format='%(asctime)s|%(levelname)s %(message)s',
    )

    try:
        player = MidiLights(c, hw, args.no_cache)
        player.run(args.midi, args.song)
    except Exception as e:
        logging.error("Exception caught: {}".format(e))
        hw.set_all_channels_to_value(0)
        raise e
