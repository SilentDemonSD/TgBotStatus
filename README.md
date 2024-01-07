## TgBotStatus
A Simple Telegram Status Updater to Pretify All your Bots for your Channel in single Status..

---

## ***Features***
- _Sequential Status Check_
- _Progress Bar on Checking_
- _Calculate Ping Time of Response_
- _Show Available/Working Bots_
- _Fresh Clean UI_
- _Set Custom Host for Each Bot(s)_
- _Support for MLTB Advanced Status (More Status Details)_

---

## ***Repo Config SetUp***:

### _`.env` File SetUp :_
- `API_ID`: Authenticate your Telegram account, get this from https://my.telegram.org.
- `API_HASH`: Authenticate your Telegram account, get this from https://my.telegram.org.
- `PYRO_SESSION`: Pyrogram User Session to Access Bots, Generate from [Here](https://colab.research.google.com/drive/1wjYvtwUo5zDsUvukyafAR9Of-2NYkKsu)
- `HEADER_MSG` : Put Header Msg for 1st Line. 
  > Default: Telegram Bot Status :
- `TIME_ZONE`: Time Zone for Sync with your Local Time
  > Default: Asia/Kolkata

### _`config.json` File SetUp :_
- _Sections are Divided into 2 Parts_:
  1. Bots Details:
    `bot1`: Indentifier Name (Can be Anything But Unique for Every Bot)

    |Variable|Value|Required|
    |:---:|:---:|:---:|
    |`base_url_of_bot`|If MLTB bot, give Base URL of it.|(Optional)|
    |`host`|Host name where you have deployed|*Required|
    |`bot_uname`|Bot Username without @|*Required|
    
  2. Chat Details:
    `chat1`: Indentifier Name (Can be Anything But Unique for Every Bot)

    |Variable|Value|Required|
    |:---:|:---:|:---:|
    |`chat_id`|chat id of the Target Channel or Group|*Required|
    |`message_id`|message id of the Message to Edit. If link is https://t.me/cha_uname/123 Here, 123 is the Message ID|*Required|

#### Sample JSON Format
```json
{
  "bots": {
    "bot1": {
      "base_url_of_bot": "http://0.0.0.0",
      "host": "HK",
      "bot_uname": "@botfather"
    },
    "bot2": {
      "host": "Vps",
      "bot_uname": "@botfather"
    }
    ...more
  },
  "channels": {
    "chat1": {
      "chat_id": "-100987654321",
      "message_id": "54321"
    },
    "chat2": {
      "chat_id": "-100123456789",
      "message_id": "12345"
    }
    ...more
  }
}
```

### _Required Config Setup :_
Either Add these URL to these Variables or Directly Add a File on Repo as File name Specified.

- `CONFIG_ENV_URL`: _(Optional if .env provided)_ Direct URL of `.env` file posted on [gist.github.com](https://gist.github.com)
- `CONFIG_JSON_URL`:  _(Optional if config.json provided)_ Direct URL of `config.json` file posted on [gist.github.com](https://gist.github.com)

> NOTE: CONFIG_JSON_URL & CONFIG_ENV_URL will overwrite the existing files if provided.

---

## ***Deploy Guide***
- Only Deployable on Workflows
- Soon Add for Heroku & VPS Users

### _Prerequisites:_
- Setup `config.json` and `.env`
- Send a Dummy Message on the Channel (say 'test') you want to Setup Status and Retrieve the message id of it.

### _Procedure:_
- **Step 1:** _Fork & Star the Repo_
- **Step 2:** _Set Variables in Secrets in Settings Tab_
  > Available Variables: API_ID, API_HASH, PYRO_SESSION, CONFIG_ENV_URL, CONFIG_JSON_URL
- **Step 3:** _Enable `Actions` -> `Select Workflow` -> `Run Workflow`_

---

## ***Advanced MLTB Status***:
_Set the Code in the Required File `wserver.py` at the Last_
**Path :** ./web/wserver.py 

```py
from time import sleep, time
from psutil import boot_time, disk_usage, net_io_counters
from subprocess import check_output
from os import path as ospath

botStartTime = time()
if ospath.exists('.git'):
    commit_date = check_output(["git log -1 --date=format:'%y/%m/%d %H:%M' --pretty=format:'%cd'"], shell=True).decode()
else:
    commit_date = 'No UPSTREAM_REPO'

@app.route('/status', methods=['GET'])
def status():
    bot_uptime = time() - botStartTime
    uptime = time() - boot_time()
    sent = net_io_counters().bytes_sent
    recv = net_io_counters().bytes_recv
    return {
        'commit_date': commit_date,
        'uptime': uptime,
        'on_time': bot_uptime,
        'free_disk': disk_usage('.').free,
        'total_disk': disk_usage('.').total,
        'network': {
            'sent': sent,
            'recv': recv,
        },
    }
```

---

## ***Cron Job Workflow***:
- Format for Tg Message Edit/Update Interval
  - `*/5 * * * *`: Update Every 5mins Interval
  > Due to Github Runner, Working Time Varies from 5min to more..
  - `0 */2 * * *`: Update Every 2hrs Interval

---

## ***Credits***:
- SilentDemonSD (Developer)

## ***References***:
- Based on `xditya/BotStatus`
- Based on `junedkh/ mirror-bot-status`
- Written in PyroFork Framework (Extended Pyrogram)
