import argparse
import logging
from time import sleep
import wiringpi


class Hardware(object):
    def __init__(self, gpio_pins=range(0, 8), active_low_mode=False):
        self.channels = {}
        wiringpi.wiringPiSetup()

        # Setup Channels
        channel_id = 0
        for pin in gpio_pins:
            channel_id += 1

            channel = Channel(channel_id, pin, active_low_mode)
            self.channels[str(channel_id)] = channel

    def debug_flash(self, cached_status):
        self.set_all_channels_to_value(0)
        sleep(0.1)
        self.set_all_channels_to_value(1)
        sleep(0.1 if cached_status else 0.4)
        self.set_all_channels_to_value(0)

    def set_all_channels_to_value(self, value):
        [c.set_pin(value) for c in self.channels.values()]

    def set_channel_value(self, channel_id, value):
        self.channels[str(channel_id)].set_pin(value)


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

    def set_pin(self, pin_value):
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

    parser.add_argument('--status', help='Set the status of all lights')

    args = parser.parse_args()

    hw = Hardware()

    if args.status:
        if args.status.lower() == 'on':
            hw.set_all_channels_to_value(1)
        else:
            hw.set_all_channels_to_value(0)



