import datetime
import json
import os
import re
import threading
import time
import requests
import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup
from flask import Flask

# ================= FLASK SERVER (For 24/7 Uptime) =================

app = Flask('')

@app.route('/')
def home():
    return "👑 Crown M4 Multi-Lookup Bot is Alive & Running 24/7!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

# ================= CONFIG =================

BOT_TOKEN = "8887168683:AAFU5xQN389gI1WSOhEom41FY0I4-fRy3fs"
ADMIN_ID = 8407090614  # आपकी Telegram ID

TOKEN = "xpol_Demo_combo_a811c2fb"
BASE_URL = "https://xpolitesupgrade-api.darrify-api.workers.dev/api"

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

def redact_sensitive(data):
    if isinstance(data, dict):
        new_dict = {}
        for k, v in data.items():
            if k.lower() in ["aadhar", "aadhaar", "uid"]:
                new_dict[k] = "[Redacted]"
            else:
                new_dict[k] = redact_sensitive(v)
        return new_dict
    elif isinstance(data, list):
        return [redact_sensitive(item) for item in data]
    return data

# ================= MENU KEYBOARD =================

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = KeyboardButton("🇮🇳 Indian Number Lookup")
    btn2 = KeyboardButton("🚗 Vehicle Lookup")
    btn3 = KeyboardButton("🏦 IFSC Lookup")
    btn4 = KeyboardButton("📍 Pincode Lookup")
    btn5 = KeyboardButton("🌐 IP Info")
    btn6 = KeyboardButton("💎 My Credits")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
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
        f"Welcome to <b>crown👑m4 Multi-Lookup System</b> 🔥\n\n"
        "🎁 <b>5 Free Credits</b> to start with.\n"
        "Use the buttons below to perform lookups:\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📱 <b>Number Lookup:</b> Send 10-digit phone number\n"
        "🚗 <b>Vehicle Lookup:</b> Send RC number (e.g., MH02DG4444)\n"
        "🏦 <b>IFSC Lookup:</b> Send IFSC code (e.g., SBIN0004843)\n"
        "📍 <b>Pincode Scanner:</b> Send 6-digit Pincode (e.g., 110001)\n"
        "🌐 <b>IP Info:</b> Send IP address (e.g., 8.8.8.8)\n\n"
        "💎 Each lookup costs <b>1 credit</b>.\n"
        "💬 <b>Support:</b> Send any message here to talk with Admin.\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "⚡ Powered by <b>crown👑m4</b>"
    )

    msg = bot.send_message(
        message.chat.id, welcome, reply_markup=main_menu(), parse_mode="HTML"
    )
    auto_delete(msg.chat.id, msg.message_id)

# ================= BUTTON HANDLERS =================

@bot.message_handler(func=lambda m: m.text == "🇮🇳 Indian Number Lookup")
def lookup_num_button(message):
    msg = bot.reply_to(message, "📱 Send any 10‑digit Indian phone number.")
    auto_delete(msg.chat.id, msg.message_id)

@bot.message_handler(func=lambda m: m.text == "🚗 Vehicle Lookup")
def lookup_veh_button(message):
    msg = bot.reply_to(message, "🚗 Send Vehicle RC number (e.g., <code>MH02DG4444</code>).")
    auto_delete(msg.chat.id, msg.message_id)

@bot.message_handler(func=lambda m: m.text == "🏦 IFSC Lookup")
def lookup_ifsc_button(message):
    msg = bot.reply_to(message, "🏦 Send IFSC code (e.g., <code>SBIN0004843</code>).")
    auto_delete(msg.chat.id, msg.message_id)

@bot.message_handler(func=lambda m: m.text == "📍 Pincode Lookup")
def lookup_pin_button(message):
    msg = bot.reply_to(message, "📍 Send 6-digit Pincode (e.g., <code>110001</code>).")
    auto_delete(msg.chat.id, msg.message_id)

@bot.message_handler(func=lambda m: m.text == "🌐 IP Info")
def lookup_ip_button(message):
    msg = bot.reply_to(message, "🌐 Send IP address (e.g., <code>8.8.8.8</code>).")
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

# ================= LOOKUP CORE ENGINE =================

def execute_api_call(message, endpoint_url, query_label, search_val):
    user_id = message.from_user.id
    user, _ = get_user(user_id)

    if user_id != ADMIN_ID and user["credits"] < 1:
        msg = bot.reply_to(message, "❌ Not enough credits. Contact admin for more.")
        auto_delete(msg.chat.id, msg.message_id)
        return

    wait_msg = bot.reply_to(message, "📡 Searching...")

    if user_id != ADMIN_ID:
        try:
            username = f"@{message.from_user.username}" if message.from_user.username else "No Username"
            admin_log = f"🔍 <b>SEARCH NOTIFICATION</b>\n👤 <b>User:</b> {message.from_user.first_name} ({username})\n🆔 <b>User ID:</b> <code>{user_id}</code>\n<b>Type:</b> {query_label}\n<b>Value:</b> <code>{search_val}</code>"
            bot.send_message(ADMIN_ID, admin_log, parse_mode="HTML")
        except Exception as e:
            print(f"[!] Admin Alert Error: {e}")

    try:
        r = requests.get(endpoint_url, timeout=15)

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

        api_response = redact_sensitive(api_response)

        if isinstance(api_response, dict):
            api_response["owner"] = "crown 👑 m4"
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
🔍 <b>SEARCH TYPE:</b> {query_label}
📌 <b>QUERY:</b> <code>{search_val}</code>
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

# ================= QUERY ROUTER =================

@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def handle_queries(message):
    txt = message.text.strip()

    # Phone Number (10 digits)
    if txt.isdigit() and len(txt) == 10:
        url = f"{BASE_URL}/ph-tracker?token={TOKEN}&number={txt}"
        execute_api_call(message, url, "PHONE LOOKUP", txt)
        return

    # Pincode (6 digits)
    if txt.isdigit() and len(txt) == 6:
        url = f"{BASE_URL}/pincode?token={TOKEN}&pincode={txt}"
        execute_api_call(message, url, "PINCODE SCANNER", txt)
        return

    # IP Address
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", txt):
        url = f"{BASE_URL}/ip-master?token={TOKEN}&ip={txt}"
        execute_api_call(message, url, "IP INFO", txt)
        return

    # IFSC Code (e.g., SBIN0004843)
    if re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", txt.upper()):
        url = f"{BASE_URL}/ifsc-master?token={TOKEN}&ifsc={txt.upper()}"
        execute_api_call(message, url, "IFSC MASTER", txt.upper())
        return

    # Vehicle Number (e.g., MH02DG4444)
    if re.match(r"^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$", txt.upper().replace(" ", "")):
        clean_rc = txt.upper().replace(" ", "")
        url = f"{BASE_URL}/vehicle-master?token={TOKEN}&rc={clean_rc}"
        execute_api_call(message, url, "VEHICLE MASTER", clean_rc)
        return

    # Fallback to Admin 2-Way Chat if unformatted text
    handle_all_messages(message)

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
    print("👑 CROWN M4 MULTI-LOOKUP BOT STARTED WITH KEEP-ALIVE SERVER")
    keep_alive()
    bot.infinity_polling()

        
