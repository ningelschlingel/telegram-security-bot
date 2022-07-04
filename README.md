# telegram-security-bot
Motion activated videos via telegram

# Introduction

This telegram-security-bot is made to be run on a Raspberry Pi zero W with a PiCamera and a RCWL-0516 radar-motion-sensor.
When motion is detected, it informs authorized users via textmessage and starts the videorecording. When no furhter movements can be detected, the recording is stopped and also sent.
To be somewhat sure, that no unauthorized users get access to these video-recordings, the bot is configured to allow basic user administration.

# Installation

### Clone Project

  ```
  git clone https://github.com/ningelsohn/wordclock.git
  ```
  
  

### Create your Telegram-Bot

If you're new to telegram-bots, you can find an introduction by telegram [here](https://core.telegram.org/bots).  
get your api-token and insert it in the [config.py](https://github.com/ningelsohn/telegram-security-bot/blob/main/config.py#L4-L5) file along with a self-selected first activation token for you, the owner.  
Once the bot is live, you will be able to register youself with that owner-token and take control,  
so that no unauthorized persons have access to the surveillance videos.



### What are you up to?
You can now choose how to proceed. The [script setup](#script-setup) should be the faster and easier option.  
If you dont want to use `venv` or a `systemd service`  you can jump to the [manual setup](#manual-setup).

### Script setup

  ```bash
  sudo telegram-security-bot/install.sh
  ```
  <details>
  <summary>What does this script do?</summary>
  <br>

  - Setting up virtual python environment and installing dependencies
  - Installing MP4Box for .h264-to-.mp4 converting
  - Adjusting the [.service-file](https://github.com/ningelsohn/telegram-security-bot/blob/main/app.service#L6) according to the app-location
  - Installing and activating systemd service (stars the app automatically)

  </details>
  
Check service status
```bash
systemctl status app.service
```

If no errors occured, you should now be able to [interact with the bot](#usage).

  
### Manual setup

  Navigate into the project directory
  ```bash
  cd {...}/telegram-security-bot
  ```
  
  Optional: Install and activate venv
  ```bash
  python3 -m pip install virtualenv
  python3 -m virtualenv venv
  source venv/bin/activate
  ```
  
  Install python dependencies
  ```bash
  python3 -m pip install -r requirements.txt
  ```
  
  Install MP4Box
  ```bash
  sudo apt-get install gpac 
  ```
  
  <details>
  <summary>Why?</summary>
  <br>

  PiCamera is capturing videos in h264-encoding. While this is no problem for the usage on the pi, MP4 is a more common coding and has caused less compatibility problems. MP4Box is used to convert .h264 videos to .mp4.
  </details>
  
Start the appllication:
```bash
python3 -m app.py
```

If you decide to set up the systemd service on your own, make sure to replace both [placeholders](https://github.com/ningelsohn/telegram-security-bot/blob/main/app.service#L6).


### Raspberry Pi Setup

Whether you are using an already set up Pi or a new one, make sure that you activate the camera and ssh if needed in the `raspi-config`.

# Hardware Setup

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

This may vary, so make sure to look into the pinout. If your want to use another GPIO Pin, make sure to adjust the [config.py](https://github.com/ningelsohn/telegram-security-bot/blob/main/config.py#L5) accordingly.

# Usage



Now that your bot is up and runnning, you should register yourself as the owner as long as the `OWNER_ACTIVATION_TOKEN` is valid.

## Commands

### Example

To understand the following list of commands, take a look at this example.
The first section is the name of the command. This is, what the set up handlers respond to.  

Some commands require additional parameters to funciton properly.
There are required params like `<PARAM_NAME:[<VALUE1>, <VALUE2>]>` and optional params like `<?OPTIONAL_PARAM_NAME:DATATYPE>`.
In both cases, the param has additional information about which values are accepted.
This can either be a datatype like `STRING` or `INTEGER`, or a list of specific values.

Furthermore, the `*ROLE` value indicates which role is required at least to use the command.


```
/command <PARAM_NAME:[<VALUE1>, <VALUE2>]> <?OPTIONAL_PARAM_NAME:DATATYPE> *ROLE
```


### Activate token

Use the `/activate` command to register as a new user. 
The token determines your authorizations.

```
/activate <TOKEN:STRING> *OPEN_ROLE
```

Usually a token is only valid for one day, so register promptly.

Example: `/activate HG3TL4NZE9M7`

### Show users

Use the `/users` command to get a list of all registered users.

```
/users *MOD_ROLE
```

Example: `/users`


### Generate token

Use the `/token` command to generate new tokens.
This is the only way to give other users access to the surveillance.

```
/token <ROLE_OPTION:['-a', '-m', '-s']> <?DAYS_VALID:INTEGER> *ADMIN_ROLE
```

Make sure to provide the required role option: `-a` for admin, `-m` for mod, `-s` for subscribers. 
Per default, every token is only valid for one day. You can pass the optional `DAYS_VALID` parameter to increase the time of validity.
You can only create tokens for roles that have less authority than your own.
Take a look into the [role table](#roles) for a rough feature overview.

Example: `/token -a 3`


### Clear all users

Use the `/clear` command to clear all registered users and currently pending tokens.

```
/clear *OWNER_ROLE
```

Example: `/clear`


## Roles

role level | role name   | role          | features                                                                    | create option
-----------| ------------| ------------- |-----------------------------------------------------------------------------|---------------
4          | OWNER_ROLE  | owner         | text & video notifications, create new tokens (-a, -m, -s) , manage users   | 
3          | ADMIN_ROLE  | admin         | text & video notifications, create new tokens (-m, -s) , manage users       | -a
2          | MOD_ROLE    | mod           | text notifications, manage users                                            | -m
1          | SUB_ROLE    | subscriber    | text notifications                                                          | -s
0          | OPEN_ROLE   |               | activate token                                                              | 


