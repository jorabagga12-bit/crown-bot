import datetime
import json
import os
import re
import threading
import time
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
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

# 🔥 यहाँ तेरी नई फोटो का नाम सेट कर दिया है!
START_PHOTO_PATH = "89187_2.jpg"  

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

# ================= PREMIUM INLINE MENU =================

def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    # बटन अब मैसेज के साथ ही चिपक कर आएंगे!
    markup.add(
        InlineKeyboardButton("📱 Num Lookup", callback_data="num"),
        InlineKeyboardButton("🪪 Aadhaar", callback_data="aadhar"),
        InlineKeyboardButton("🚗 Vehicle", callback_data="veh"),
        InlineKeyboardButton("📧 Email", callback_data="email"),
        InlineKeyboardButton("🎮 BGMI", callback_data="bgmi"),
        InlineKeyboardButton("🏢 GST Info", callback_data="gst"),
        InlineKeyboardButton("🏦 IFSC", callback_data="ifsc"),
        InlineKeyboardButton("📍 Pincode", callback_data="pin"),
        InlineKeyboardButton("🌐 IP Info", callback_data="ip"),
        InlineKeyboardButton("💎 My Profile", callback_data="profile")
    )
    return markup

# ================= START COMMAND =================

@bot.message_handler(commands=["start"])
def start(message):
    get_user(message.from_user.id)

    welcome_text = (
        f"✨ <b><i>WELCOME TO CROWN 👑 M4 PRO INTEL</i></b> ✨\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👋 <i>Greetings,</i> <b>{message.from_user.first_name}</b>!\n\n"
        f"🛡️ <b><u>ADVANCED OSINT SYSTEM</u></b> 🛡️\n"
        f"Our database is fully synced and ready.\n"
        f"🎁 <b>Starter Bonus:</b> <code>5 Free Credits</code>\n\n"
        f"⚡ <i>Click any button below to start your lookup:</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👨‍💻 <i>Owned & Managed by</i> <b>CROWN 👑 M4</b>"
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
                welcome_text + "\n\n<i>(⚠️ Error: Start Photo not found in server folder)</i>",
                reply_markup=main_menu(),
                parse_mode="HTML"
            )
        auto_delete(msg.chat.id, msg.message_id)
    except Exception as e:
        print(f"Photo sending error: {e}")

# ================= INLINE BUTTON HANDLERS =================

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    
    if call.data == "num":
        bot.send_message(chat_id, "📱 <b>TARGET SELECTION:</b>\n<i>Please send any 10‑digit Indian phone number.</i>", parse_mode="HTML")
    elif call.data == "aadhar":
        bot.send_message(chat_id, "🪪 <b>TARGET SELECTION:</b>\n<i>Please send the 12-digit Aadhaar Card number.</i>", parse_mode="HTML")
    elif call.data == "veh":
        bot.send_message(chat_id, "🚗 <b>TARGET SELECTION:</b>\n<i>Please send Vehicle RC number (e.g., <code>HP809021</code>).</i>", parse_mode="HTML")
    elif call.data == "email":
        bot.send_message(chat_id, "📧 <b>TARGET SELECTION:</b>\n<i>Please send the Target Email address (e.g., <code>test@gmail.com</code>).</i>", parse_mode="HTML")
    elif call.data == "bgmi":
        bot.send_message(chat_id, "🎮 <b>TARGET SELECTION:</b>\n<i>Please send BGMI Player User ID.</i>", parse_mode="HTML")
    elif call.data == "gst":
        bot.send_message(chat_id, "🏢 <b>TARGET SELECTION:</b>\n<i>Please send 15-character GSTIN Number.</i>", parse_mode="HTML")
    elif call.data == "ifsc":
        bot.send_message(chat_id, "🏦 <b>TARGET SELECTION:</b>\n<i>Please send IFSC code.</i>", parse_mode="HTML")
    elif call.data == "pin":
        bot.send_message(chat_id, "📍 <b>TARGET SELECTION:</b>\n<i>Please send 6-digit Pincode.</i>", parse_mode="HTML")
    elif call.data == "ip":
        bot.send_message(chat_id, "🌐 <b>TARGET SELECTION:</b>\n<i>Please send target IP address.</i>", parse_mode="HTML")
    elif call.data == "profile":
        user = get_user(call.from_user.id)
        credits_display = "♾️ <b>Unlimited (Owner)</b>" if call.from_user.id == ADMIN_ID else f"<b>{user['credits']}</b>"
        
        info_text = (
            f"👤 <b><u>USER VIP PROFILE</u></b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🆔 <b>User:</b> <i>{call.from_user.first_name}</i>\n"
            f"💎 <b>Credits:</b> {credits_display}\n"
            f"🔍 <b>Total Queries:</b> <b>{user['lookups']}</b>\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        bot.send_message(chat_id, info_text, parse_mode="HTML")

    bot.answer_callback_query(call.id) # Loading animation हटाने के लिए

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
            result_json = result_json[:3000] + "\n... [DATA TRUNCATED FOR DISPLAY]"

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

# ================= AUTO QUERY ROUTER =================
# अब यूजर को कमांड डालने की जरुरत नहीं, बस डेटा सेंड करो बोट खुद पहचान लेगा!

@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def handle_queries(message):
    txt = message.text.strip()
    clean_rc = re.sub(r'[^A-Z0-9]', '', txt.upper())

    # 1. Email Address Lookup
    if re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", txt):
        url = f"{BASE_URL_OSINT}/email-info?key={OSINT_KEY}&mail={txt}"
        execute_api_call(message, url, "EMAIL DATABASE", txt)
        return

    # 2. Phone Number (10 digits)
    if txt.isdigit() and len(txt) == 10:
        url = f"{BASE_URL_MAIN}/ph-tracker?token={TOKEN}&number={txt}"
        execute_api_call(message, url, "PHONE RECORD", txt)
        return

    # 3. Aadhaar Card Number (12 digits)
    if txt.isdigit() and len(txt) == 12:
        url = f"{BASE_URL_MAIN}/aadhar-info?token={TOKEN}&id={txt}"
        execute_api_call(message, url, "AADHAAR CARD RECORD", txt)
        return

    # 4. BGMI Player Info (8 to 13 digits ID)
    if txt.isdigit() and len(txt) in [8, 9, 10, 11, 12, 13]:
        url = f"{BASE_URL_OSINT}/bgmi-info?key={OSINT_KEY}&user={txt}"
        execute_api_call(message, url, "BGMI PLAYER INTEL", txt)
        return

    # 5. Pincode (6 digits)
    if txt.isdigit() and len(txt) == 6:
        url = f"{BASE_URL_MAIN}/pincode?token={TOKEN}&pincode={txt}"
        execute_api_call(message, url, "AREA PINCODE", txt)
        return

    # 6. GSTIN Lookup (15 Chars)
    if re.match(r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z0-9]{1}Z[A-Z0-9]{1}$", txt.upper()):
        url = f"{BASE_URL_OSINT}/gst-search?key={OSINT_KEY}&gstin={txt.upper()}"
        execute_api_call(message, url, "GST BUSINESS INTEL", txt.upper())
        return

    # 7. IP Address
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", txt):
        url = f"{BASE_URL_MAIN}/ip-master?token={TOKEN}&ip={txt}"
        execute_api_call(message, url, "NETWORK IP", txt)
        return

    # 8. IFSC Code
    if re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", txt.upper()):
        url = f"{BASE_URL_MAIN}/ifsc-master?token={TOKEN}&ifsc={txt.upper()}"
        execute_api_call(message, url, "BANK IFSC", txt.upper())
        return

    # 9. Vehicle Number (RC)
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
