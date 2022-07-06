import os

#: Both token values need to be provided
#: I created another config file:
#:
#:  ___________
#: | secret.py |
#: |___________|__________________________________________
#: |                                                      |
#: | TELEGRAM_API_TOKEN=<TELEGRAM_API_TOKEN>              |
#: | OWNER_ACTIVATION_TOKEN=<OWNER_ACTIVATION_TOKEN>      |
#: | ...                                                  |
#: |______________________________________________________|
#:
#: 
#: And adjusted the config.py:
#:  ___________
#: | config.py |
#: |___________|__________________________________________
#: |                                                      |
#: | TELEGRAM_API_TOKEN=secret.TELEGRAM_API_TOKEN         |
#: | OWNER_ACTIVATION_TOKEN=secret.OWNER_ACTIVATION_TOKEN |
#: | ...                                                  |
#: |______________________________________________________|
#:

TELEGRAM_API_TOKEN='<TELEGRAM_API_TOKEN>'
OWNER_ACTIVATION_TOKEN='<OWNER_ACTIVATION_TOKEN>'

#: GPIO-Pin for motion-detection
#: Attention: GPIO 4 -> Pin 7 
#: Research `Raspberry Pi Zero Pinout` for more information
SENSOR_PIN=4

#: Adjust buffer to keep video going without motion
#: The motion sensor stays on for around 2 seconds after the last movement
#: Every step is roughly 1 second
#: BUFFER_TIME_STEPS=2 would therefore result in around 4 seconds buffer time
#: meaning that the recording will be stopped if for 4 seconds no motion is detected
BUFFER_TIME_STEPS=2

#: Set a max video length since long videos may cause problems while sending
#: This is no exact time, because its done using time.sleep()
#: The rest of the program also takes time
#: MAX_VIDEO_LENGTH=30 results in videos with around 33 to 36 seconds
MAX_VIDEO_LENGTH=30

#: Path to current directory
FILE_PATH=os.path.abspath(__file__).rsplit('/', 1)[0]

#: Name of directory in which the videos will be saved
VIDEO_DIR='videos'

#: PiCamera records in .h264
CAMERA_RECORDING_FORMAT='.h264'

#: But .mp4 is causing less problems with compatibility
CAMERA_CONVERTING_FORMAT='.mp4'

#: Length of user activation tokens
#: With uppercase letters and digits and a length of 12 there are 4738381338321616896 possible tokens
#: I reduced it to 8, 2821109907456 options should do just fine
ACTIVATION_TOKEN_LENGTH=8
