# Pedalboard GUI

This is a Gradio frontend GUI for the [Spotify Pedalboard](https://github.com/spotify/pedalboard) library. This is intended for demo purposes.

## Usage

1. Start the GUI with `python pedalboard_gui.py`. If everything is set up properly, the GUI will automatically open in a browser window at URL `http://127.0.0.1:7680/`
2. Upload / record the audio you want to process
3. Enable the effects you want to apply to the audio, then click Submit. The order that effects get applied roughly corresponds with the GUI layout (top to bottom, then left to right)
4. Your audio output should appear at the bottom of the GUI. You can download it by clicking the Download icon in the top right of the output audio zone.

## Environment

All you need is Python >= 3.8 with pedalboard and gradio installed `pip install -U pedalboard gradio`

## Features

All effects from the Pedalboard API are currently in the GUI except the following:

- External Plugins, VST3Plugin
- Convolution, IIRFilter: need to figure out best user friendly way to incorperate the convolution waveform upload into the GUI
