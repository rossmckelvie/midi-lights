# midi-lights
Choreographed Christmas Lights Controller for the Raspberry Pi

## Powered by MIDI
MIDI files can be used to choreograph Christmas lights to music! midi-lights runs on a Raspberry Pi and the same hardware setup that works with [LightShow Pi](http://lightshowpi.org/): a relay that toggles the power to 8 outlets. GPIO pins 0-7 are mapped to channels 1-8 of the relay.

A MIDI file contains a list of messages, each with a note, note status (`on` or `off`), and a time to wait before changing the status. A mapping of notes to lights allows the entire show to be choreographed with a keyboard.

If you don't like MIDI, the cached command list from a midi file is stored as JSON. This file is what is sent to the remotes, and the midi file is not required for playing (only for running choreograph.py)

## Usage  
Create a `config.json` file, a sample is provided. Modify to fit your setup. Install packages from `src/requirements.txt`

#### Choreograph a song
`./bin/choreograph wizards` or `python src/choreograph.py --song=wizards`  

This generates the JSON command files

#### Launch a node & wait for instructions
`./bin/nodeup upstairs` or `python src/hardware_server.py --node=upstairs`  

Note: you will have to launch a master node server. The play process below will make a request to localhost to kick off the song

#### Play a choreographed song
`./bin.play wizards` or `python src/play.py --song=wizards`  

MIDI Note-to-Channel mappings are defined in config.json

#### Turn all lights on or off
`./bin/hardware on` or `python src/hardware.py --toggle off`  
