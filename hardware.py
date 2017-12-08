import argparse
from command import Command
from config import Config
import json
import logging
from time import time, sleep
import wiringpi


class Hardware(object):
    def __init__(self, config):
        """
        :param config:
        :type config: Config
        """
        self.channels = {}
        wiringpi.wiringPiSetup()

        # Setup Channels
        for _id, channel_settings in config.settings['channels'].items():
            channel = Channel(_id, channel_settings['pin'], channel_settings['active_low'])
            self.channels[_id] = channel

    def set_all_channels_to_value(self, value):
        [c.set_pin_state(value) for c in self.channels.values()]

    def set_channel_value(self, channel_id, value):
        """
        Write a value out to the relay
        :param channel_id:
        :type channel_id: int
        :param value:
        :type value: int
        :return:
        """
        self.channels[str(channel_id)].set_pin_state(value)

    def execute_command(self, command):
        """
        Process all channel changes defined in command
        :param command:
        :type command: Command
        """
        changes = command.changes
        sleep(command.timeout)

        if len(changes) == 1 and '*' == changes.keys()[0]:
            self.set_all_channels_to_value(changes.values()[0])
        else:
            for channel, val in changes.items():
                self.set_channel_value(channel, val)

    def play_script(self, script):
        """
        Execute commands
        :param script:
        :type script: Command[]
        :return: int time_lost
        """
        # Code takes time to execute.. record it here to keep the midi command playback in sync with the music
        time_lost = 0

        for command in script:
            logging.debug(json.dumps({'command': command.__dict__, 'time_lost': time_lost}))
            t = time()

            # Timeout wait, but catch back up in sync
            if command.timeout:
                time_lost_diff = command.timeout - time_lost

                # Sleep or Sync
                if time_lost_diff < 0:  # Time lost > timeout, don't sleep
                    time_lost -= command.timeout
                elif time_lost_diff > 0:  # timeout is greater than time lost, sleep & get in-sync
                    time_lost = 0
                    t += time_lost_diff
                    command.timeout = time_lost_diff
                else:  # in-sync if we don't sleep
                    time_lost = 0

            # Write pin values out
            self.execute_command(command)

            # Update time lost
            time_lost += time() - t

        return time_lost


class Channel(object):
    def __init__(self, channel_id, pin_id, active_low_mode):
        self.channel_id = channel_id
        self.pin_id = pin_id
        self.active_low_mode = active_low_mode

        self.is_output = True
        self.set_pin_mode(is_output=True)

    def set_pin_mode(self, is_output):
        self.is_output = is_output
        wiringpi.pinMode(self.pin_id, 1 if is_output else 0)

    def set_pin_state(self, pin_value):
        """
        :param pin_value:
        :type pin_value: int one of 1 (on) or 0 (off)
        """
        if self.active_low_mode:
            pin_value = 1 - pin_value

        wiringpi.digitalWrite(self.pin_id, pin_value)
        logging.debug({
            'channel': self.channel_id,
            'pin': self.pin_id,
            'value': pin_value
        })


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    hw = Hardware(Config())

    parser.add_argument('--status', help='Set the status of all lights. One of [on, off]', required=True)

    args = parser.parse_args()
    if args.status:
        hw.set_all_channels_to_value(1 if args.status.lower() == 'on' else 0)
