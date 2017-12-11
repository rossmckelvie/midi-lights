import argparse
import logging
import config
from hardware import Hardware
import json
import os
from pathlib2 import Path
import requests
import signal
from subprocess import Popen
import threading

signal.signal(signal.SIGINT, signal.SIG_IGN)


class MidiLights(object):
    def __init__(self, configuration, hardware, disable_caching=False):
        self.config = configuration
        self.start_time = None
        self.hardware = hardware
        self.caching_disabled = disable_caching

    def run(self, song):
        song_config = self.config.settings['music'][song]

        logging.info("Reading MIDI: {}".format(song_config['midi']))
        logging.info("Playing Song: {}".format(song_config['song']))
        logging.info("Cache: {}".format("Disabled" if self.caching_disabled else "Enabled"))

        # Required Files
        song_path = "music/{}".format(song_config['song'])
        required_files = [song_path]
        for node in self.config.settings['nodes'].keys():
            required_files.append("music/{}".format(song_config['commands'].format(node=node)))

        # Validate input files
        for file_path in required_files:
            if not Path(file_path).is_file():
                msg = "{} is not a file.".format(file_path)
                logging.error(msg)
                raise RuntimeError(msg)

        # Load commands onto remotes & prepare to play
        self.prepare_remotes(song_config)
        threads = []
        for node_name in self.config.settings['nodes'].keys():
            t = threading.Thread(
                name="Play:{}".format(node_name),
                target=self.play_remote,
                args=(node_name,)
            )
            threads.append(t)

        # Play lights
        [t.start() for t in threads]

        # Start play song
        mp3_command = self.play_mp3_command(song_path)
        music_player = Popen(mp3_command, shell=True)

        # Wait for lights to complete
        [t.join() for t in threads]

        # Wait for music to complete
        logging.info("MIDI File complete, waiting for music to finish")
        music_player.wait()

        # Turn all of the lights on to end the show!
        logging.info("Merry Christmas!")
        self.hardware.set_all_channels_to_value(1)

    def play_remote(self, node_name):
        node = self.config.settings['nodes'][node_name]
        url = "http://{}:{}/cmd".format(node['host'], node['port'])

        r = requests.post(url)
        logging.debug("Node finished: {}".format(node_name))
        return r.text

    def prepare_remotes(self, song_config):
        for node_name, node in self.config.settings['nodes'].items():
            commands = json.load(open("music/{}".format(song_config['commands'].format(node=node_name))))
            logging.info("Sending {} commands".format(len(commands)))
            url = "http://{}:{}/cmd".format(node['host'], node['port'])

            r = requests.put(url, json={'commands': commands})
            logging.debug("Prepared Remote {}: {}".format(node_name, r.text))

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
    parser.add_argument('--song', required=True, help='Song to play', choices=c.settings['music'].keys())
    parser.add_argument('--no-cache', action='store_true', default=False, help='Set to disable caching')

    args = parser.parse_args()

    logging.basicConfig(
        level=args.loglevel,
        format='%(asctime)s|%(levelname)s %(message)s',
    )

    try:
        player = MidiLights(c, hw, args.no_cache)
        player.run(args.song)
    except Exception as e:
        logging.error("Exception caught: {}".format(e))
        hw.set_all_channels_to_value(0)
        raise e
