# midi-lights
Choreographed Christmas Lights Controller for the Raspberry Pi

## Powered by MIDI
MIDI files can be used to choreograph Christmas lights to music! midi-lights runs on a Raspberry Pi and the same hardware setup that works with [LightShow Pi](http://lightshowpi.org/): a relay that toggles the power to 8 outlets. GPIO pins 0-7 are mapped to channels 1-8 of the relay.

A MIDI file contains a list of messages, each with a note, note status (`on` or `off`), and a time to wait before changing the status. A mapping of notes to lights allows the entire show to be choreographed with a keyboard.

If you don't like MIDI, the cached command list from a midi file is stored as JSON. This file is what is sent to the remotes
## Usage  
Create a `config.json` file, a sample is provided. Modify to fit your setup.

#### Choreograph a song
`python choreograph.py --song=wizards`

#### Launch a node & wait for instructions
`python hardware_server.py --node=upstairs`  
Note: you will have to launch a master node server. The play process below will make a request to localhost to kick off the song

#### Play a choreographed song
`python play.py --song=wizards`  
MIDI Note-to-Channel mappings are defined in config.json

#### Turn all lights on or off
`python hardware.py --toggle on`
