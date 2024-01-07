#!/usr/bin/env python3
from asyncio import sleep
from logging import basicConfig, INFO, getLogger
from json import loads as json_loads
from time import time
from os import getenv, path as ospath 
from datetime import datetime

from pytz import utc, timezone
from dotenv import load_dotenv
from requests import get as rget
from pyrogram import Client
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.raw import functions

basicConfig(level=INFO, format="[%(levelname)s] %(asctime)s - %(message)s")
log = getLogger(__name__)

if CONFIG_ENV_URL := getenv('CONFIG_ENV_URL'):
    try:
        res = rget(CONFIG_ENV_URL)
        if res.status_code == 200:
            log.info("Downloading .env from CONFIG_ENV_URL")
            with open('.env', 'wb+') as f:
                f.write(res.content)
        else:
            log.error(f"Failed to Download .env due to Error Code {res.status_code}")
    except Exception as e:
        log.error(f"CONFIG_ENV_URL: {e}")

if CONFIG_JSON_URL := getenv('CONFIG_JSON_URL'):
    try:
        res = rget(CONFIG_JSON_URL)
        if res.status_code == 200:
            log.info("Downloading config.json from CONFIG_JSON_URL")
            with open('config.json', 'wb+') as f:
                f.write(res.content)
        else:
            log.error(f"Failed to download config.json due to Error Code {res.status_code}")
    except Exception as e:
        log.error(f"CONFIG_JSON_URL: {e}")

load_dotenv('.env', override=True)

API_ID = int(getenv("API_ID", 0))
API_HASH = getenv("API_HASH")
PYRO_SESSION = getenv('PYRO_SESSION')
if PYRO_SESSION is None:
    log.error('PYRO_SESSION is not set')
    exit(1)
if not ospath.exists('config.json'):
    log.error("config.json not Found!")
    exit(1)
try:
    config = json_loads(open('config.json', 'r').read())
    bots = config['bots']
    channels = config['channels']
except Exception as e:
    log.error(str(e))
    log.error("Error: config.json is not valid")
    exit(1)

HEADER_MSG = getenv("HEADER_MSG", "Telegram Bot Status:")
FOOTER_MSG = getenv("FOOTER_MSG", "Join FZX Paradox at @FZXParadox")
TIME_ZONE = getenv("TIME_ZONE", "Asia/Kolkata")

log.info("Connecting pyroBotClient")
try:
    client = Client("TgBotStatus", api_id=API_ID, api_hash=API_HASH, session_string=PYRO_SESSION)
except BaseException as e:
    log.warning(e)
    exit(1)

def progress_bar(current, total):
    pct = current/total * 100
    pct = float(str(pct).strip('%'))
    p = min(max(pct, 0), 100)
    cFull = int(p // 8)
    p_str = '●' * cFull
    p_str += '○' * (12 - cFull)
    return f"[{p_str}] {round(pct, 2)}%"
    
def get_readable_time(seconds):
    periods = [('d', 86400), ('h', 3600), ('m', 60), ('s', 1)]
    result = ''
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f'{int(period_value)}{period_name}'
    return result
    
SIZE_UNITS   = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']
    
def get_readable_file_size(size_in_bytes):
    if size_in_bytes is None:
        return '0B'
    index = 0
    while size_in_bytes >= 1024 and index < len(SIZE_UNITS) - 1:
        size_in_bytes /= 1024
        index += 1
    return f'{size_in_bytes:.2f}{SIZE_UNITS[index]}' if index > 0 else f'{size_in_bytes}B'

    
async def bot_info(user_id):
    try:
        return (await client.get_users(user_id)).mention
    except Exception:
        return ''
    
async def editMsg(chat_id, message_id, text):
    try:
        return await client.edit_message_text(int(chat_id), int(message_id), text)
    except FloodWait as f:
        await sleep(f.value * 1.2)
        await editMsg(chat_id, message_id, text)
    except MessageNotModified:
        pass

async def editStatusMsg(status_msg):
    _channels = channels.values()
    if len(_channels) == 0:
        log.warning("No channels found")
        exit(1)
    for channel in _channels:
        log.info(f"Updating Channel ID : {channel['chat_id']} & Message ID : {channel['message_id']}")
        await sleep(1.5)
        try:
            await editMsg(channel['chat_id'], channel['message_id'], status_msg)
        except Exception as e:
            log.error(str(e))
            continue

async def check_bots():
    start_time = time()
    bot_stats = {}
    totalBotsCount = len(bots.keys())
    log.info("Starting Periodic Bot Status checks...")
    
    header_msg = f"__**{HEADER_MSG}**__\n\n"
    status_message = header_msg + """• **Avaliable Bots :** __Checking...__

• `Currently Ongoing Periodic Check`

"""
    await editStatusMsg(status_message + f"""**Status Update Stats:**
┌ **Bots Verified :** 0 out of {totalBotsCount}
├ **Progress :** [○○○○○○○○○○] 0%
└ **Time Elasped :** 0s""")

    bot_no, avl_bots = 0, 0
    for bot, bdata in bots.items():
        if not bot or not bdata:
            break
        bot_stats.setdefault(bot, {})
        bot_stats[bot]['host'] = bdata['host']
        pre_time = time()
        if bdata.get('base_url_of_bot'):
            resp = rget(f"{bdata['base_url_of_bot']}/status")
            if resp.status_code == 200:
                bot_stats[bot]["status_data"] = resp.json()
        try:
            sent_msg = await client.send_message(bdata['bot_uname'], "/start")
            await sleep(10)
            history_msgs = await client.invoke(
                functions.messages.GetHistory(
                    peer=await client.resolve_peer(bdata['bot_uname']), offset_id=0, offset_date=0, add_offset=0, limit=1, max_id=0, min_id=0, hash=0,
                )
            )
            if sent_msg.id == history_msgs.messages[0].id:
                bot_stats[bot]["status"] = "❌"
            else:
                resp_time = history_msgs.messages[0].date - int(pre_time)
                avl_bots += 1
                bot_stats[bot]["response_time"] = f"`{round(resp_time * 1000, 2)}ms`"
                bot_stats[bot]["status"] = "✅"
            await client.read_chat_history(bdata['bot_uname'])
        except Exception as e:
            log.info(str(e))
            bot_stats[bot]["status"] = "❌"
        
        log.info(f"Checked {bdata['bot_uname']} & Status : {bot_stats[bot]['status']}.")
        bot_no += 1
        
        await editStatusMsg(status_message + f"""**Status Update Stats:**
┌ **Bots Checked :** {bot_no} out of {totalBotsCount}
├ **Progress :** {progress_bar(bot_no, totalBotsCount)}
└ **Time Elasped :** {round(time() - start_time, 2)}s""")

    end_time = time()
    log.info("Completed periodic checks.")

    status_message = header_msg + f"• **Avaliable Bots :** {avl_bots} out of {totalBotsCount}\n\n"
    for bot in bot_stats.keys():
        status_message += f"┌ **Bot :** {await bot_info(bdata['bot_uname'])} ( @{bdata['bot_uname']} )"
        if (stdata := bot_stats[bot].get('status_data')):
            try:
                status_message += f'├ **Commit Date :** {stdata["commit_date"]}\n'
            except:
                pass
            try:
                status_message += f'├ **Bot Uptime :** {get_readable_time(stdata["on_time"])}\n'
            except:
                pass
            try:
                status_message += f'├ **Alive :** {get_readable_time(stdata["uptime"])}\n'
            except:
                pass
            try:
                status_message += f'├ **Up :** {get_readable_size(stdata["network"]["sent"])} '
                status_message += f'| **DL :** {get_readable_size(stdata["network"]["recv"])}\n'
                status_message += f'├ **Free Disk :** {get_readable_size(stdata["free_disk"])} / {get_readable_size(stdata["total_disk"])}\n'
            except:
                status_message += '├ **Something went Wrong!**'
        
        if bot_stats[bot].get("response_time"):
            status_message += f"├ **Ping :** {bot_stats[bot]['response_time']}\n"
        status_message += f"""├ **Status :** {bot_stats[bot]['status']}
└ **Host :** {bot_stats[bot]['host']}
            
"""

    total_time = end_time - start_time
    status_message += f"• **Last Periodic Checked in {round(total_time, 2)}s**\n\n"
    
    current_time = datetime.now(utc).astimezone(timezone(TIME_ZONE))
    status_message += f"""• **Last Check Details :**
┌ **Time :** `{current_time.strftime('%H:%M:%S')} hrs`
├ **Date :** `{current_time.strftime('%d %B %Y')}`
└ **Time Zone :** `{TIME_ZONE} (UTC {current_time.strftime('%z')})`

__○ Auto Status Update in 5 mins Interval__

{FOOTER_MSG}"""
    await editStatusMsg(status_message)

async def main():
    async with client:
        await check_bots()
        
client.run(main())
