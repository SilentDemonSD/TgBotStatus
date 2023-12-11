## TgBotStatus
A Simple Telegram Status Updater to Pretify All your Bots for your Channel in single Status..

## ***Deploy***
- Only Deployable on Workflows
- Fork & Star and Enable `Actions` -> `Run Workflow`

## ***Features***
- Sequential Status Check
- Progress on Checking 
- Calculate Ping Time
- Available Bots
- Fresh Clean UI
- Set Custom Hosts for Each Bots

## ***Config SetUp***:
- `APP_ID`: Authenticate your Telegram account, get this from https://my.telegram.org.
- `API_HASH`: Authenticate your Telegram account, get this from https://my.telegram.org.
- `SESSION`: Telethon User Session to Access Bots, Generate from [Here](https://colab.research.google.com/drive/1wjYvtwUo5zDsUvukyafAR9Of-2NYkKsu)
- `BOTS`: Username of Bots Separated by single Space ( without @ )
  > bot01Bot bot02Bot
- `HOSTS`: Hosts corresponding to Bots List Var separated by single Space
  > host host host2
- `CHANNEL_ID`: Channel ID of the Message in which Msg ID is to be Edited
- `MESSAGE_ID`: Message ID of the Message to Edit
- `CHANNEL_NAME`: Any Channel Description or Just Name
- `TIME_ZONE`: Time Zone for Sync with your Local Time

## ***Cron Job Workflow***:
- Format for Msg Update Interval
  - `*/5 * * * *`: Update Every 5mins Interval
  - `0 */2 * * *`: Update Every 2hrs Interval

## ***Credits***
- SilentDemonSD (Developer)
- Based on `xditya/BotStatus`
