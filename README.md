# 📸 &nbsp; Telegram Security Bot
**Motion activated surveillance videos via telegram**

- [Introduction](#--introduction)
- [Features](#--features)
- [Installation](#--installation)
  - [Raspberry Pi setup](#raspberry-pi-setup)
  - [Clone Project](#clone-project)
  - [Create your Telegram-Bot](#create-your-telegram-bot)
  - [What are you up to?](#what-are-you-up-to)
  - [Script setup](#script-setup)
  - [Manual setup](#manual-setup)
- [Hardware setup](#--hardware-setup)
  - [Required parts](#required-parts)
  - [Wiring](#wiring)
- [Usage](#--usage)
  - [Commands](#commands)
    - [Example](#example)
    - [/activate - Activate token](#activate-token)
    - [/leave - Leave](#leave)
    - [/users - Show registered users](#show-users)
    - [/banned - Show banned users](#show-banned-users)
    - [/token - Generate token](#generate-token)
    - [/cleartokens Clear tokens](#clear-tokens)
    - [/pause - Pause](#pause-surveillance)
    - [/unpause - Unpause](#unpause-surveillance)
    - [/ban - Ban user](#ban-user)
    - [/unban - Unban user](#unban-user)
    - [/clear - Clear all](#clear)
  - [Roles](#roles)


# 🚀 &nbsp; Introduction

This telegram security bot is designed to run on a Raspberry Pi zero W with a PiCamera and a RCWL-0516 radar motion sensor.

When motion is detected, it notifies authorized users via textmessage and starts the videorecording.
When no further movements can be detected, the recording is stopped and sent.
To be somewhat sure that no unauthorized users get access to these recordings, the bot allows basic user administration.

# 🧳 &nbsp; Features

- Get security camera footage anywhere via telegram
- Create activation tokens to give other users access
- Manage users
- Pause and resume surveillance 

# 📁 &nbsp; Installation

### Raspberry Pi setup

Whether you are using an already set up Pi or a new one, make sure that you activate the camera and if needed ssh in the `raspi-config`.

### Clone Project

  ```
  git clone https://github.com/ningelsohn/telegram-security-bot.git
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

# 🛠 &nbsp; Hardware setup

### Required Parts:
- Raspberry Pi zero W
- Raspberry Pi (zero) camera
- RCWL-0516 radar-sensor

### General

Make sure that the Pi has permanent access to the internet.  
Even though the Pi can run on a battery, a power supply is clearly preferable since the video recordings increase the power consumption significantly.

### Wiring

The camera is simply plugged in with the enclosed ribbon cable. If you're buying a camera for this project, keep in mind that Pi Zero camera cables dont fit the bigger Pi's and vice versa.
The radar-sensor in my case has five pins which are soldered onto the Pi as follows:

RCWL-0516 Pin | Raspberry Pi Zero W
--------------|------------------------
3V3           | 
GND           | PIN 6 (GROUND)
OUT           | PIN 7 (GPIO 4)
VIN           | PIN 2 (5V)
CDS           |

This may vary, so make sure to look into the pinout. If your want to use another GPIO Pin, make sure to adjust the [config.py](https://github.com/ningelsohn/telegram-security-bot/blob/main/config.py#L5) accordingly.
If you are interested in more details about the RCWL-0516, you should check [this](http://www.rogerclark.net/investigating-a-rcwl-9196-rcwl-0516-radar-motion-detector-modules/) out.

**In my case the sensor was misfiring a lot when it was pressed tightly together with the Pi.  
Keeping a little distance has solved the problem.**

# 🌟 &nbsp; Usage

Now that your bot is up and runnning, you should register yourself as the owner as long as the `OWNER_ACTIVATION_TOKEN` is valid.

### Commands

The following commands are documented with a specific format.
The first section is the name of the command. This will trigger the handler for this specific command. 
The second section is a parameter for this command. The majority of the commands don't require parameters.
The last section specifies the role which is required to call this command. 
The roles are strictly ordered and each role has the permissions of the respective subordinate roles.


```
/command <PARAM_NAME> *ROLE
```

---

#### Activate token

Use the `/activate` command to register as a new user. 
The token determines your authorizations.

```
/activate <TOKEN> *OPEN_ROLE
```

Usually a token is only valid for one day, so register promptly after receiving one.

Example: `/activate HG3TL4NZE9M7`

---

#### Leave

Use the `/leave` command to unsubscribe. As the owner, you cant leave.
If you change your mind, you will need a new activation token.

```
/leave
```

Usually a token is only valid for one day, so register promptly after receiving one.

Example: `/activate HG3TL4NZE9M7`

---

#### Show users

Use the `/users` command to get a list of all registered users.

```
/users *MOD_ROLE
```

Example: `/users`

---

#### Show banned users

Use the `/banned` command to get a list of all banned users.

```
/banned *MOD_ROLE
```

Example: `/banned`

---

#### Generate token

Use the `/token` command to generate new tokens.
This is the only way to give other users access to the surveillance.

```
/token <ROLE_OPTION> *ADMIN_ROLE
```

This request will yields a two-step query to determine the role and validity period.
You can only create tokens for roles that have less authority than your own.
Take a look into the [role table](#roles) for a rough feature overview.

Example: `/token`

---

#### Clear tokens

Use the `/cleartokens` command to remove all pending tokens.

```
/cleartokens *ADMIN_ROLE
```

Currently this is the only option of invalidating tokens.

Example: `/cleartokens`

---

#### Pause surveillance

Use the `/pause` command to pause the motion activated surveillance.

```
/pause *ADMIN_ROLE
```

If at the moment of pausing the camera is active, the recording will continue and you will receive it as usual.

Example: `/pause`

---

#### Unpause surveillance

Use the `/unpause` command to unpause motion activated surveillance..

```
/unpause *ADMIN_ROLE
```

If at the moment of unpausing a previously detected motion is still ongoing, this will not trigger a new recording. Only after the motion stopped the surveillance is active again.

Example: `/unpause`

---

#### Ban user

Use the `/ban` command to ban an active user.

```
/ban *ADMIN_ROLE
```

This will yield a query in which you can select the user to be banned.
Only users with less powerful roles are shown.

Example: `/ban`

---

#### Unban user

Use the `/unban` command to unban an banned user.

```
/ban *ADMIN_ROLE
```

This will yield a query in which you can select the user to be unbanned.
Only users with less powerful roles are shown.

Example: `/unban`

---

#### Clear

Use the `/clear` command to clear all registered users and currently pending tokens.

```
/clear *OWNER_ROLE
```

Example: `/clear`

---

### Roles

role level | role name   | role          | features                                                                   
-----------| ------------| ------------- |-----------------------------------------------------------------------------
4          | OWNER_ROLE  | owner         | text & video notifications, create new tokens (-a, -m, -s) , manage users  
3          | ADMIN_ROLE  | admin         | text & video notifications, create new tokens (-m, -s) , manage users      
2          | MOD_ROLE    | mod           | text notifications, manage users                                           
1          | SUB_ROLE    | subscriber    | text notifications                                                         
0          | OPEN_ROLE   |               | activate token                                                            


