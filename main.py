#!/usr/bin/env python3
from asyncio import sleep
from logging import basicConfig, INFO, getLogger
from time import time
from datetime import datetime
from itertools import zip_longest

from pytz import utc, timezone
from decouple import config
from telethon import TelegramClient, functions
from telethon.sessions import StringSession

basicConfig(level=INFO, format="[%(levelname)s] %(asctime)s - %(message)s")
log = getLogger("TgBotStatus")

try:
    APP_ID = config("APP_ID", cast=int)
    API_HASH = config("API_HASH")
    SESSION = config("SESSION")
    LIST_BOTS = config("BOTS")
    LIST_HOSTS = config("HOSTS")
    CHANNEL_ID = config("CHANNEL_ID", cast=int)
    MESSAGE_ID = config("MESSAGE_ID", cast=int)
    CHANNEL_NAME = config("CHANNEL_NAME", default="FZX Paradox")
    TIME_ZONE = config("TIME_ZONE", default="Asia/Kolkata")
except BaseException as ex:
    log.info(ex)
    exit(1)

BOTS = LIST_BOTS.split()
HOSTS = LIST_HOSTS.split()

log.info("Connecting BotClient")
try:
    client = TelegramClient(StringSession(SESSION), api_id=APP_ID, api_hash=API_HASH).start()
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

async def check_bots():
    start_time = time()
    bot_stats = {}
    log.info("[CHECK] Started Periodic Bot Status checks...")
    header_msg = f"__**{CHANNEL_NAME} Bot Status :**__\n\n"
    status_message = header_msg + """• **Avaliable Bots :** __Checking...__

• `Currently Ongoing Periodic Check`

"""
    try:
        await client.edit_message(CHANNEL_ID, MESSAGE_ID, status_message + f"""**Status Update Stats:**
┌ **Bots Verified :** 0 out of {len(BOTS)}
├ **Progress :** [○○○○○○○○○○] 0%
└ **Time Elasped :** 0s""")
    except BaseException as e:
        log.warning("[EDIT] Unable to edit message in the channel!")
        log.error(e)
        return

    bot_no, avl_bots = 0, 0
    for bot, host in zip_longest(BOTS, HOSTS):
        if bot is None:
            break
        pre_time = time()
        try:
            sent_msg = await client.send_message(bot, "/start")
            await sleep(10)
            history = await client(
                functions.messages.GetHistoryRequest(
                    peer=bot, offset_id=0, offset_date=None, add_offset=0, limit=1, max_id=0, min_id=0, hash=0,
                )
            )
            if sent_msg.id == history.messages[0].id:
                bot_stats[bot] = {"response_time": None, "status": "❌", "host": host or "Unknown"}
            else:
                resp_time = history.messages[0].date.timestamp() - pre_time
                avl_bots += 1
                bot_stats[bot] = {"response_time": f"`{round(resp_time * 1000, 2)}ms`", "status": "✅", "host": host or "Unknown"}
        except BaseException:
            bot_stats[bot] = {"response_time": None, "status": "❌", "host": host or "Unknown"}
        
        await client.send_read_acknowledge(bot)
        log.info(f"[CHECK] Checked @{bot} - {bot_stats[bot]['status']}.")
        bot_no += 1
        
        await client.edit_message(CHANNEL_ID, MESSAGE_ID, status_message + f"""**Status Update Stats:**
┌ **Bots Verified :** {bot_no} out of {len(BOTS)}
├ **Progress :** {progress_bar(bot_no, len(BOTS))}
└ **Time Elasped :** {round(time() - start_time, 2)}s""")

    end_time = time()
    log.info("[CHECK] Completed periodic checks.")

    status_message = header_msg + f"• **Avaliable Bots :** {avl_bots} out of {len(BOTS)}\n\n"
    for bot, value in bot_stats.items():
        if bot_stats[bot]["response_time"] is None:
            status_message += f"""┌ **Bot :** @{bot}
├ **Status :** {bot_stats[bot]['status']}
└ **Host :** {bot_stats[bot]['host']}
            
"""
        else:
            status_message += f"""┌ **Bot :** @{bot}
├ **Ping :** {bot_stats[bot]['response_time']}
├ **Status :** {bot_stats[bot]['status']}
└ **Host :** {bot_stats[bot]['host']}
            
"""

    total_time = end_time - start_time
    status_message += f"• **Last Periodic Checked in {round(total_time, 2)}s**\n\n"
    
    current_time = datetime.now(utc).astimezone(timezone(TIME_ZONE))
    status_message += f"""• **Last Check Details :**
┌ **Time :** `{current_time.strftime('%H:%M:%S')} hrs`
├ **Date :** `{current_time.strftime('%d %B %Y')}`
└ **Time Zone :** `{TIME_ZONE} (UTC {current_time.strftime('%z')})`

__○ Auto Status Update in 5 mins Interval__"""

    try:
        await client.edit_message(CHANNEL_ID, MESSAGE_ID, status_message)
    except BaseException as e:
        log.warning("[EDIT] Unable to edit message in the channel!")
        log.error(e)
        return


client.loop.run_until_complete(check_bots())
