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

# ================= FLASK SERVER (24/7 Uptime) =================

app = Flask('')

@app.route('/')
def home():
    return "👑 Crown M4 VIP OSINT System is Running 24/7!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

# ================= CONFIGURATION =================

BOT_TOKEN = "8887168683:AAFU5xQN389gI1WSOhEom41FY0I4-fRy3fs"
ADMIN_ID = 8407090614

# APIs Configuration
TOKEN = "xpol_Demo_combo_a811c2fb"
BASE_URL_MAIN = "https://xpolitesupgrade-api.darrify-api.workers.dev/api"
BASE_URL_OSINT = "https://osint-api-delta.vercel.app/api"
OSINT_KEY = "demo"

DATA_FILE = "users_data.json"
START_PHOTO_PATH = "89187_2.jpg"  # तेरी फोटो का नाम

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
total_lookups = 0

# ================= DATA PERSISTENCE =================

def load_data():
    global total_lookups
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                total_lookups = data.get("total_lookups", 0)
                return data.get("users", {})
        except Exception as e:
            print(f"[!] Data Load Error: {e}")
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
        print(f"[!] Data Save Error: {e}")

users = load_data()

def get_user(user_id):
    uid = str(user_id)
    if uid not in users:
        users[uid] = {"credits": 5, "lookups": 0}
        save_data()
    return users[uid]

def auto_delete(chat_id, message_id):
    def delete():
        time.sleep(3600)  # Auto delete after 1 hour
        try:
            bot.delete_message(chat_id, message_id)
        except Exception:
            pass
    threading.Thread(target=delete).start()

# ================= BOTTOM REPLY KEYBOARD (10 Buttons) =================

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = KeyboardButton("🇮🇳 Indian Number Lookup")
    btn2 = KeyboardButton("🪪 Aadhaar Card Lookup")
    btn3 = KeyboardButton("🚗 Vehicle Lookup")
    btn4 = KeyboardButton("📧 Email Info Lookup")
    btn5 = KeyboardButton("🎮 BGMI Player Info")
    btn6 = KeyboardButton("🏢 GST Search")
    btn7 = KeyboardButton("🏦 IFSC Lookup")
    btn8 = KeyboardButton("📍 Pincode Lookup")
    btn9 = KeyboardButton("🌐 IP Info")
    btn10 = KeyboardButton("💎 My Credits")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10)
    return markup

# ================= START COMMAND =================

@bot.message_handler(commands=["start"])
def start(message):
    get_user(message.from_user.id)

    welcome_text = (
        f"✨ <b><i>WELCOME TO CROWN 👑 M4 PRO INTEL SYSTEM</i></b> ✨\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👋 <i>Greetings,</i> <b>{message.from_user.first_name}</b>!\n\n"
        f"🎁 <b>Starter Bonus:</b> <code>5 Free Credits Available</code>\n\n"
        f"🔥 <b><u>AVAILABLE INTEL SERVICES</u></b> 🔥\n"
        f"📱 <i>Send 10-Digit Phone Number</i>\n"
        f"🪪 <i>Send 12-Digit Aadhaar Number</i>\n"
        f"🚗 <i>Send RC Number (e.g., HP809021)</i>\n"
        f"📧 <i>Send Email Address</i>\n"
        f"🎮 <i>Send BGMI Character ID</i>\n"
        f"🏢 <i>Send 15-Digit GSTIN Number</i>\n"
        f"🏦 <i>Send Bank IFSC Code</i>\n"
        f"📍 <i>Send 6-Digit Area Code</i>\n"
        f"🌐 <i>Send IP Address</i>\n\n"
        f"💎 <i>Cost per search:</i> <b>1 Credit</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ <i>Powered & Secured by</i> <b>CROWN 👑 M4</b>"
    )

    try:
        if os.path.exists(START_PHOTO_PATH):
            with open(START_PHOTO_PATH, "rb") as photo:
                msg = bot.send_photo(
                    message.chat.id,
                    photo,
                    caption=welcome_text,
                    reply_markup=main_menu(),
                    parse_mode="HTML"
                )
        else:
            msg = bot.send_message(
                message.chat.id,
                welcome_text + "\n\n<i>(⚠️ Photo not found in server folder)</i>",
                reply_markup=main_menu(),
                parse_mode="HTML"
            )
        auto_delete(msg.chat.id, msg.message_id)
    except Exception as e:
        print(f"Photo error: {e}")

# ================= EXECUTE API ENGINE =================

def execute_api_call(message, endpoint_url, query_label, search_val):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user_id != ADMIN_ID and user["credits"] < 1:
        msg = bot.reply_to(message, "❌ <i>Not enough credits available. Contact Admin to recharge!</i>", parse_mode="HTML")
        auto_delete(msg.chat.id, msg.message_id)
        return

    wait_msg = bot.reply_to(message, "📡 <b><i>Extracting Live Database Records...</i></b>", parse_mode="HTML")

    try:
        r = requests.get(endpoint_url, timeout=15)
        if r.status_code != 200:
            bot.edit_message_text(f"❌ <b>API Error Code:</b> <code>{r.status_code}</code>", message.chat.id, wait_msg.message_id, parse_mode="HTML")
            return

        api_response = r.json()
        if not api_response:
            bot.edit_message_text("❌ <b>No records found in database.</b>", message.chat.id, wait_msg.message_id, parse_mode="HTML")
            return

        if user_id != ADMIN_ID:
            user["credits"] -= 1

        user["lookups"] += 1
        global total_lookups
        total_lookups += 1
        save_data()

        result_json = json.dumps(api_response, indent=2, ensure_ascii=False)
        if len(result_json) > 3000:
            result_json = result_json[:3000] + "\n... [DATA TRUNCATED]"

        date = datetime.datetime.now().strftime("%d-%m-%Y %I:%M %p")
        rem_credits = "♾️ Unlimited" if user_id == ADMIN_ID else user["credits"]

        text = f"""
🏛️ <b><i>CROWN 👑 M4 INTEL SYSTEM</i></b> 🏛️
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 <b>SEARCH TYPE:</b> <i>{query_label}</i>
📌 <b>INPUT QUERY:</b> <code>{search_val}</code>
📅 <b>TIMESTAMP:</b> <code>{date}</code>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b><u>DATABASE RECORD OUTPUT:</u></b>
<pre>{result_json}</pre>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 <b>OFFICER/USER:</b> @{message.from_user.username or 'NoUsername'}
💎 <b>REMAINING CREDITS:</b> <code>{rem_credits}</code>
⚡ <b>POWERED BY:</b> <b>CROWN 👑 M4</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        bot.edit_message_text(text, message.chat.id, wait_msg.message_id, parse_mode="HTML")
        auto_delete(message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ <b>Execution Error:</b> <code>{e}</code>", message.chat.id, wait_msg.message_id, parse_mode="HTML")

# ================= QUERY ROUTER & BUTTON FIX =================

@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def handle_queries(message):
    txt = message.text.strip()
    clean_rc = re.sub(r'[^A-Z0-9]', '', txt.upper())

    # 1. Handle Menu Button Clicks (Fixes "Target Unidentified" error on button click)
    if txt == "🇮🇳 Indian Number Lookup":
        msg = bot.reply_to(message, "📱 <i>Please send any 10‑digit Indian phone number.</i>", parse_mode="HTML")
        auto_delete(msg.chat.id, msg.message_id)
        return
    elif txt == "🪪 Aadhaar Card Lookup":
        msg = bot.reply_to(message, "🪪 <i>Please send the 12-digit Aadhaar Card number.</i>", parse_mode="HTML")
        auto_delete(msg.chat.id, msg.message_id)
        return
    elif txt == "🚗 Vehicle Lookup":
        msg = bot.reply_to(message, "🚗 <i>Please send Vehicle RC number (e.g., HP809021).</i>", parse_mode="HTML")
        auto_delete(msg.chat.id, msg.message_id)
        return
    elif txt == "📧 Email Info Lookup":
        msg = bot.reply_to(message, "📧 <i>Please send Target Email address (e.g., test@gmail.com).</i>", parse_mode="HTML")
        auto_delete(msg.chat.id, msg.message_id)
        return
    elif txt == "🎮 BGMI Player Info":
        msg = bot.reply_to(message, "🎮 <i>Please send BGMI Player User ID.</i>", parse_mode="HTML")
        auto_delete(msg.chat.id, msg.message_id)
        return
    elif txt == "🏢 GST Search":
        msg = bot.reply_to(message, "🏢 <i>Please send 15-character GSTIN Number.</i>", parse_mode="HTML")
        auto_delete(msg.chat.id, msg.message_id)
        return
    elif txt == "🏦 IFSC Lookup":
        msg = bot.reply_to(message, "🏦 <i>Please send Bank IFSC code (e.g., SBIN0004843).</i>", parse_mode="HTML")
        auto_delete(msg.chat.id, msg.message_id)
        return
    elif txt == "📍 Pincode Lookup":
        msg = bot.reply_to(message, "📍 <i>Please send 6-digit Pincode.</i>", parse_mode="HTML")
        auto_delete(msg.chat.id, msg.message_id)
        return
    elif txt == "🌐 IP Info":
        msg = bot.reply_to(message, "🌐 <i>Please send target IP address (e.g., 8.8.8.8).</i>", parse_mode="HTML")
        auto_delete(msg.chat.id, msg.message_id)
        return
    elif txt == "💎 My Credits":
        user = get_user(message.from_user.id)
        credits_display = "♾️ <b>Unlimited (Owner)</b>" if message.from_user.id == ADMIN_ID else f"<b>{user['credits']}</b>"
        info_text = (
            f"👤 <b><u>USER VIP PROFILE</u></b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🆔 <b>User:</b> <i>{message.from_user.first_name}</i>\n"
            f"💎 <b>Credits:</b> {credits_display}\n"
            f"🔍 <b>Total Lookups:</b> <b>{user['lookups']}</b>\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        msg = bot.reply_to(message, info_text, parse_mode="HTML")
        auto_delete(msg.chat.id, msg.message_id)
        return

    # 2. Email Address Lookup
    if re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", txt):
        url = f"{BASE_URL_OSINT}/email-info?key={OSINT_KEY}&mail={txt}"
        execute_api_call(message, url, "EMAIL DATABASE", txt)
        return

    # 3. Phone Number (10 digits)
    if txt.isdigit() and len(txt) == 10:
        url = f"{BASE_URL_MAIN}/ph-tracker?token={TOKEN}&number={txt}"
        execute_api_call(message, url, "PHONE RECORD", txt)
        return

    # 4. Aadhaar Card Number (12 digits)
    if txt.isdigit() and len(txt) == 12:
        url = f"{BASE_URL_MAIN}/aadhar-info?token={TOKEN}&id={txt}"
        execute_api_call(message, url, "AADHAAR CARD RECORD", txt)
        return

    # 5. BGMI Player Info (8 to 13 digits ID)
    if txt.isdigit() and len(txt) in [8, 9, 10, 11, 12, 13]:
        url = f"{BASE_URL_OSINT}/bgmi-info?key={OSINT_KEY}&user={txt}"
        execute_api_call(message, url, "BGMI PLAYER INTEL", txt)
        return

    # 6. Pincode (6 digits)
    if txt.isdigit() and len(txt) == 6:
        url = f"{BASE_URL_MAIN}/pincode?token={TOKEN}&pincode={txt}"
        execute_api_call(message, url, "AREA PINCODE", txt)
        return

    # 7. GSTIN Lookup (15 Chars)
    if re.match(r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z0-9]{1}Z[A-Z0-9]{1}$", txt.upper()):
        url = f"{BASE_URL_OSINT}/gst-search?key={OSINT_KEY}&gstin={txt.upper()}"
        execute_api_call(message, url, "GST BUSINESS INTEL", txt.upper())
        return

    # 8. IP Address
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", txt):
        url = f"{BASE_URL_MAIN}/ip-master?token={TOKEN}&ip={txt}"
        execute_api_call(message, url, "NETWORK IP", txt)
        return

    # 9. IFSC Code
    if re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", txt.upper()):
        url = f"{BASE_URL_MAIN}/ifsc-master?token={TOKEN}&ifsc={txt.upper()}"
        execute_api_call(message, url, "BANK IFSC", txt.upper())
        return

    # 10. Vehicle Number (RC)
    if re.match(r"^[A-Z]{2}\d{1,2}[A-Z]{0,3}\d{1,4}$", clean_rc):
        url = f"{BASE_URL_MAIN}/vehicle-master?token={TOKEN}&rc={clean_rc}"
        execute_api_call(message, url, "RTO VEHICLE RECORD", clean_rc)
        return

    # Fallback
    msg = bot.reply_to(
        message, 
        "❌ <b>Target Unidentified!</b>\n<i>Please enter a valid Phone, Aadhaar, Email, BGMI ID, GSTIN, Vehicle RC, IFSC, Pincode, or IP.</i>", 
        parse_mode="HTML"
    )
    auto_delete(msg.chat.id, msg.message_id)

# ================= RUN SERVER =================

if __name__ == "__main__":
    print("👑 CROWN M4 VIP OSINT BOT IS ONLINE!")
    keep_alive()
    bot.infinity_polling()
 
