import argparse
import logging
import wiringpi
from config import Config


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
        for channel, val in command.changes.items():
            self.set_channel_value(channel, val)


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


class Command(object):
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    hw = Hardware()

    parser.add_argument('--status', help='Set the status of all lights. One of [on, off]')

    args = parser.parse_args()
    if args.status:
        hw.set_all_channels_to_value(1 if args.status.lower() == 'on' else 0)
