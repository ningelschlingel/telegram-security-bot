# telegram-security-bot
Motion activated videos via telegram

## Introduction

This telegram-security-bot is made to be run on a Raspberry Pi zero W with a PiCamera and a RCWL-0516 radar-motion-sensor.
When motion is detected, it informs authorized users via textmessage and starts the videorecording. When no furhter movements can be detected, the recording is stopped and also sent.
To be somewhat sure, that no unauthorized users get access to these video-recordings, the bot is configured to allow basic user administration.

## Installation

### Raspberry Pi Setup

Whether you are using an already set up Pi or a new one, make sure that you activate the camera and ssh if needed in the `raspi-config`.

## Hardware Setup

### Required Parts:
- Raspberry Pi zero W
- Raspberry Pi (zero) camera
- RCWL-0516 radar-sensor

The camera is simply plugged in with the enclosed ribbon cable. If you're buying a camera for this project, keep in mind that Pi Zero camera cables dont fit the bigger Pi's and vice versa.
The radar-sensor in my case has five pins which I soldered onto the Pi as follows:

- 3V3 <-> None
- GND <-> GROUND (PIN 6)  
- OUT <-> GPIO 4 (PIN 7)  
- VIN <-> 5V     (PIN 2)  
- CDS <-> None

This may vary, so make sure to look into the pinout. If your want to use another GPIO Pin, make sure to adjust the [config.py](https://github.com/ningelsohn/telegram-security-bot/blob/main/config.py) accordingly.

