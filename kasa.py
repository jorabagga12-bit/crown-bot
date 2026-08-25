import datetime
import json
import os
import re
import threading
import time
import requests
import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup

# ================= CONFIG =================

BOT_TOKEN = "8887168683:AAFU5xQN389gI1WSOhEom41FY0I4-fRy3fs"
ADMIN_ID = 8407090614  # आपकी Telegram ID

API_URL = "https://nitin-developer-api-paid.nitinshab43.workers.dev/api"
API_KEY = "MY_TEST_KEY_123"

DATA_FILE = "users_data.json"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ================= DATA PERSISTENCE =================

total_lookups = 0


def load_data():
    global total_lookups
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                total_lookups = data.get("total_lookups", 0)
                return data.get("users", {})
        except Exception as e:
            print(f"[!] Error loading data: {e}")
            return {}
    return {}


def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"users": users, "total_lookups": total_lookups},
                f,
                indent=4,
                ensure_ascii=False,
            )
    except Exception as e:
        print(f"[!] Error saving data: {e}")


users = load_data()

# ================= HELPERS =================


def get_user(user_id):
    uid = str(user_id)
    is_new = False
    if uid not in users:
        # 🚨 NEW USER STARTING CREDITS SET TO 5
        users[uid] = {"credits": 5, "lookups": 0}
        save_data()
        is_new = True
    return users[uid], is_new


def auto_delete(chat_id, message_id):
    def delete():
        time.sleep(3600)  # 1 hour
        try:
            bot.delete_message(chat_id, message_id)
        except Exception:
            pass

    threading.Thread(target=delete).start()


# ================= MENU KEYBOARD =================


def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = KeyboardButton("🇮🇳 Indian Number Lookup")
    btn2 = KeyboardButton("💎 My Credits")
    markup.add(btn1, btn2)
    return markup


# ================= START =================


@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    user, is_new = get_user(user_id)

    if is_new and user_id != ADMIN_ID:
        try:
            name = message.from_user.first_name or "Unknown"
            username = (
                f"@{message.from_user.username}"
                if message.from_user.username
                else "No Username"
            )
            admin_msg = f"🔔 <b>NEW USER JOINED!</b>\n\n👤 <b>Name:</b> {name}\n🔗 <b>Username:</b> {username}\n🆔 <b>User ID:</b> <code>{user_id}</code>"
            bot.send_message(ADMIN_ID, admin_msg, parse_mode="HTML")
        except Exception as e:
            print(f"[!] Admin Alert Error: {e}")

    welcome = (
        f"👋 Hello <b>{message.from_user.first_name}</b>!\n"
        f"Welcome to <b>crown👑m4</b> 🔥\n\n"
        "🎁 <b>5 Free Credits</b> to start with.\n"
        "Use the buttons below to lookup Indian numbers.\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📌 <b>How to use:</b>\n"
        "1️⃣ Tap <b>🇮🇳 Indian Number Lookup</b>\n"
        "2️⃣ Send any 10‑digit number\n"
        "3️⃣ Get instant JSON data\n\n"
        "💎 Each lookup costs <b>1 credit</b>.\n"
        "💬 <b>Support:</b> You can send any message here to talk with Admin.\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "⚡ Powered by <b>crown👑m4</b>"
    )

    msg = bot.send_message(
        message.chat.id, welcome, reply_markup=main_menu(), parse_mode="HTML"
    )
    auto_delete(msg.chat.id, msg.message_id)


# ================= BUTTON HANDLERS =================


@bot.message_handler(func=lambda m: m.text == "🇮🇳 Indian Number Lookup")
def lookup_button(message):
    msg = bot.reply_to(message, "📱 Send any 10‑digit Indian number.")
    auto_delete(msg.chat.id, msg.message_id)


@bot.message_handler(func=lambda m: m.text == "💎 My Credits")
def my_credits(message):
    user_id = message.from_user.id
    user, _ = get_user(user_id)
    credits_display = "♾️ Unlimited (Owner)" if user_id == ADMIN_ID else user['credits']
    
    msg = bot.reply_to(
        message,
        f"👤 <b>{message.from_user.first_name}</b>\n"
        f"💎 Credits: <b>{credits_display}</b>\n"
        f"🔍 Lookups: <b>{user['lookups']}</b>",
        parse_mode="HTML",
    )
    auto_delete(msg.chat.id, msg.message_id)


# ================= NUMBER LOOKUP =================


@bot.message_handler(
    func=lambda m: m.text and m.text.isdigit() and len(m.text) == 10
)
def handle_number(message):
    user_id = message.from_user.id
    user, _ = get_user(user_id)

    if user_id != ADMIN_ID and user["credits"] < 1:
        msg = bot.reply_to(
            message, "❌ Not enough credits. Contact admin for more."
        )
        auto_delete(msg.chat.id, msg.message_id)
        return

    number = message.text.strip()
    wait_msg = bot.reply_to(message, "📡 Searching...")

    if user_id != ADMIN_ID:
        try:
            username = (
                f"@{message.from_user.username}"
                if message.from_user.username
                else "No Username"
            )
            admin_log = f"🔍 <b>SEARCH NOTIFICATION</b>\n👤 <b>User:</b> {message.from_user.first_name} ({username})\n🆔 <b>User ID:</b> <code>{user_id}</code>\n📱 <b>Searched:</b> <code>{number}</code>"
            bot.send_message(ADMIN_ID, admin_log, parse_mode="HTML")
        except Exception as e:
            print(f"[!] Admin Alert Error: {e}")

    try:
        url = f"{API_URL}?action=num&number={number}&key={API_KEY}"
        r = requests.get(url, timeout=15)

        if r.status_code != 200:
            bot.edit_message_text(
                f"❌ API Error Code: {r.status_code}",
                message.chat.id,
                wait_msg.message_id,
            )
            return

        api_response = r.json()

        if not api_response:
            bot.edit_message_text(
                "❌ No record found.", message.chat.id, wait_msg.message_id
            )
            return

        if user_id != ADMIN_ID:
            user["credits"] -= 1

        user["lookups"] += 1
        global total_lookups
        total_lookups += 1
        save_data()

        if isinstance(api_response, dict):
            # 👑 Branded completely to Crown
            api_response["owner"] = "crown 👑 m4"
            if "metadata" in api_response and isinstance(
                api_response["metadata"], dict
            ):
                api_response["metadata"]["key_owner"] = "crown"
                api_response["metadata"]["api_key"] = "CROWN_API_KEY"

            if "result" in api_response and isinstance(
                api_response["result"], list
            ):
                for item in api_response["result"]:
                    if isinstance(item, dict):
                        if "aadhar" in item:
                            item["aadhar"] = "[Redacted]"
                        item["telegram"] = "@LIFExPAI"
                        item["channel"] = "https://t.me/LIFExPAI"
                        item["credit"] = "crown 👑 m4"
                        item["developer"] = "crown"

            api_response["telegram"] = "@LIFExPAI"
            api_response["channel"] = "https://t.me/LIFExPAI"
            api_response["credit"] = "crown 👑 m4"

        result = json.dumps(api_response, indent=2, ensure_ascii=False)
        if len(result) > 3500:
            result = result[:3500] + "\n... (truncated)"

        date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        uname = message.from_user.username or "NoUsername"
        rem_credits = "♾️ Unlimited (Owner)" if user_id == ADMIN_ID else user["credits"]

        text = f"""
👑 <b>CROWN 👑 M4 LOOKUP SYSTEM</b> 👑
━━━━━━━━━━━━━━━━━━━━━━━━
📱 <b>SEARCHED NUMBER:</b> <code>{number}</code>
📅 <b>DATE & TIME:</b> <code>{date}</code>
━━━━━━━━━━━━━━━━━━━━━━━━
<pre>{result}</pre>
━━━━━━━━━━━━━━━━━━━━━━━━
👤 <b>USER:</b> @{uname}
💎 <b>REMAINING CREDITS:</b> <code>{rem_credits}</code>

🚀 <b>OFFICIAL TELEGRAM:</b> @LIFExPAI
📢 <b>JOIN CHANNEL:</b> https://t.me/LIFExPAI
⚡ <b>POWERED & CREATED BY:</b> <b>CROWN 👑 M4</b>
━━━━━━━━━━━━━━━━━━━━━━━━
"""
        bot.edit_message_text(
            text, message.chat.id, wait_msg.message_id, parse_mode="HTML"
        )
        auto_delete(message.chat.id, wait_msg.message_id)

    except Exception as e:
        print(f"[!] Error: {e}")
        bot.edit_message_text(
            f"❌ Script Error: {e}", message.chat.id, wait_msg.message_id
        )


# ================= ADMIN COMMANDS =================


@bot.message_handler(commands=["add"])
def add_credits(message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 3:
        msg = bot.reply_to(message, "Usage: /add user_id amount")
        auto_delete(msg.chat.id, msg.message_id)
        return
    uid = args[1]
    try:
        amount = int(args[2])
    except ValueError:
        msg = bot.reply_to(message, "❌ Amount must be an integer.")
        auto_delete(msg.chat.id, msg.message_id)
        return

    user, _ = get_user(uid)
    user["credits"] += amount
    save_data()

    msg = bot.reply_to(message, f"✅ Added {amount} credits to user {uid}.")
    auto_delete(msg.chat.id, msg.message_id)

    try:
        bot.send_message(
            int(uid),
            f"🎉 <b>Admin added {amount} credits to your account!</b>",
            parse_mode="HTML",
        )
    except Exception:
        pass


@bot.message_handler(commands=["broadcast"])
def broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        msg = bot.reply_to(message, "Usage: /broadcast text")
        auto_delete(msg.chat.id, msg.message_id)
        return
    text = args[1]
    success = 0
    for uid in list(users.keys()):
        try:
            bot.send_message(int(uid), f"📢 ANNOUNCEMENT\n\n{text}")
            success += 1
        except Exception:
            pass
    msg = bot.reply_to(message, f"✅ Sent to {success} users.")
    auto_delete(msg.chat.id, msg.message_id)


@bot.message_handler(commands=["stats"])
def stats(message):
    if message.from_user.id != ADMIN_ID:
        return
    msg = bot.reply_to(
        message,
        f"📊 STATS\nUsers: {len(users)}\nTotal Lookups: {total_lookups}",
    )
    auto_delete(msg.chat.id, msg.message_id)


# ================= 💬 ANONYMOUS 2-WAY CHAT SYSTEM =================


@bot.message_handler(
    func=lambda m: m.chat.type == "private", content_types=["text"]
)
def handle_all_messages(message):
    if message.from_user.id == ADMIN_ID:
        if message.text.startswith("/msg"):
            try:
                parts = message.text.split(maxsplit=2)
                if len(parts) < 3:
                    bot.reply_to(
                        message,
                        "❌ Format: <code>/msg user_id आपका मैसेज</code>",
                    )
                    return
                target_id = int(parts[1])
                reply_text = parts[2]
                bot.send_message(
                    target_id,
                    f"💬 <b>Message from Admin/Support:</b>\n\n{reply_text}",
                    parse_mode="HTML",
                )
                bot.reply_to(message, "✅ Message sent successfully!")
            except Exception as e:
                bot.reply_to(message, f"❌ Failed to send: {e}")
            return

        if message.reply_to_message:
            try:
                orig_text = (
                    message.reply_to_message.text
                    or message.reply_to_message.caption
                    or ""
                )
                match = re.search(r"User ID:\s*(\d+)", orig_text) or re.search(
                    r"ID:\s*(\d+)", orig_text
                )
                if match:
                    target_id = int(match.group(1))
                    bot.send_message(
                        target_id,
                        f"💬 <b>Message from Admin/Support:</b>\n\n{message.text}",
                        parse_mode="HTML",
                    )
                    bot.reply_to(message, "✅ Reply sent successfully!")
                else:
                    bot.reply_to(
                        message, "❌ Cannot find valid User ID in replied message."
                    )
            except Exception as e:
                bot.reply_to(message, f"❌ Failed to send reply: {e}")
            return

        return

    try:
        uname = (
            f"@{message.from_user.username}"
            if message.from_user.username
            else "No Username"
        )
        user_msg_log = (
            f"📩 <b>NEW USER MESSAGE</b>\n"
            f"👤 <b>From:</b> {message.from_user.first_name} ({uname})\n"
            f"🆔 <b>User ID:</b> <code>{message.from_user.id}</code>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📝 <b>Message:</b>\n{message.text}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💡 <i>(Swipe left to reply, OR use /msg {message.from_user.id} text)</i>"
        )
        bot.send_message(ADMIN_ID, user_msg_log, parse_mode="HTML")
        bot.reply_to(
            message,
            "✅ Your message has been sent to Admin. You will receive a reply here soon!",
        )
    except Exception as e:
        print(f"[!] User Message Forward Error: {e}")


# ================= RUN =================

if __name__ == "__main__":
    print("🚀 CROWN M4 BOT STARTED")
    bot.infinity_polling()
