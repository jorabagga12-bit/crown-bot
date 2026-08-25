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
    return "👑 Crown M4 Pro-Lookup Bot is Alive & Running 24/7!"

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

# --- NEW: Aadhaar Extractor System ---
def extract_aadhar(data):
    """API रिस्पांस में से आधार नंबर ढूंढ कर निकालने वाला फंक्शन"""
    if isinstance(data, dict):
        for k, v in data.items():
            if k.lower() in ['aadhar', 'aadhaar', 'uid', 'aadhar_number']:
                return v
            elif isinstance(v, (dict, list)):
                res = extract_aadhar(v)
                if res: return res
    elif isinstance(data, list):
        for item in data:
            res = extract_aadhar(item)
            if res: return res
    return None

# ================= MENU KEYBOARD =================

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = KeyboardButton("🇮🇳 Indian Number Lookup")
    btn2 = KeyboardButton("🪪 Aadhaar Lookup")
    btn3 = KeyboardButton("🚗 Vehicle Lookup")
    btn4 = KeyboardButton("🏦 IFSC Lookup")
    btn5 = KeyboardButton("📍 Pincode Lookup")
    btn6 = KeyboardButton("🌐 IP Info")
    btn7 = KeyboardButton("💎 My Credits")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
    return markup

# ================= START =================

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    user, is_new = get_user(user_id)

    welcome = (
        f"👋 Hello <b>{message.from_user.first_name}</b>!\n"
        f"Welcome to <b>crown👑m4 Pro-Lookup System</b> 🏛️\n\n"
        "🎁 <b>5 Free Credits</b> to start with.\n"
        "Use the buttons below to perform secure lookups:\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📱 <b>Number Lookup:</b> Send 10-digit phone number\n"
        "🪪 <b>Aadhaar Lookup:</b> Send 12-digit Aadhaar number\n"
        "🚗 <b>Vehicle Lookup:</b> Send RC number (e.g., MH02DG4444)\n"
        "🏦 <b>IFSC Lookup:</b> Send IFSC code\n"
        "📍 <b>Pincode Scanner:</b> Send 6-digit Pincode\n"
        "🌐 <b>IP Info:</b> Send IP address\n\n"
        "💎 Each lookup costs <b>1 credit</b>.\n"
        "💬 <b>Support:</b> Send any message here to contact Admin.\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "⚡ <i>Official Database System Powered by <b>crown👑m4</b></i>"
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

@bot.message_handler(func=lambda m: m.text == "🪪 Aadhaar Lookup")
def lookup_aadhar_button(message):
    msg = bot.reply_to(message, "🪪 Send 12-digit Aadhaar number.")
    auto_delete(msg.chat.id, msg.message_id)

@bot.message_handler(func=lambda m: m.text in ["🚗 Vehicle Lookup", "🏦 IFSC Lookup", "📍 Pincode Lookup", "🌐 IP Info"])
def generic_buttons(message):
    msg = bot.reply_to(message, f"📌 Send the details for {message.text}.")
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
        f"🔍 Total Lookups: <b>{user['lookups']}</b>",
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

    wait_msg = bot.reply_to(message, "📡 Extracting Data from Servers...")

    try:
        r = requests.get(endpoint_url, timeout=15)

        if r.status_code != 200:
            bot.edit_message_text(f"❌ API Error: {r.status_code}", message.chat.id, wait_msg.message_id)
            return

        api_response = r.json()

        if not api_response:
            bot.edit_message_text("❌ No record found in the database.", message.chat.id, wait_msg.message_id)
            return

        if user_id != ADMIN_ID:
            user["credits"] -= 1

        user["lookups"] += 1
        global total_lookups
        total_lookups += 1
        save_data()

        # Branding Injection
        if isinstance(api_response, dict):
            api_response["authorized_by"] = "crown 👑 m4"
            api_response["telegram"] = "@LIFExPAI"
        
        # --- VIP AADHAAR HIGHLIGHT SYSTEM ---
        found_aadhar = extract_aadhar(api_response)
        aadhar_panel = f"\n🪪 <b>LINKED AADHAAR:</b> <code>{found_aadhar}</code>\n" if found_aadhar else ""

        # Formatting JSON block safely
        result_json = json.dumps(api_response, indent=2, ensure_ascii=False)
        if len(result_json) > 3000:
            result_json = result_json[:3000] + "\n... [DATA TRUNCATED FOR SECURITY]"

        date = datetime.datetime.now().strftime("%d-%m-%Y %I:%M %p")
        uname = message.from_user.username or "NoUsername"
        rem_credits = "♾️ Unlimited" if user_id == ADMIN_ID else user["credits"]

        text = f"""
🏛️ <b>CROWN 👑 M4 GOV-INTEL SYSTEM</b> 🏛️
━━━━━━━━━━━━━━━━━━━━━━━━
🔍 <b>SEARCH TARGET:</b> {query_label}
📌 <b>INPUT DATA:</b> <code>{search_val}</code>
📅 <b>TIMESTAMP:</b> <code>{date}</code>{aadhar_panel}
━━━━━━━━━━━━━━━━━━━━━━━━
<b>[ RAW DATABASE OUTPUT ]</b>
<pre>{result_json}</pre>
━━━━━━━━━━━━━━━━━━━━━━━━
👤 <b>OFFICER/USER:</b> @{uname}
💎 <b>REMAINING CREDITS:</b> <code>{rem_credits}</code>
⚡ <b>SECURELY EXTRACTED BY:</b> <b>CROWN 👑 M4</b>
━━━━━━━━━━━━━━━━━━━━━━━━
"""
        bot.edit_message_text(text, message.chat.id, wait_msg.message_id, parse_mode="HTML")
        auto_delete(message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Network/Script Error: {e}", message.chat.id, wait_msg.message_id)

# ================= QUERY ROUTER =================

@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def handle_queries(message):
    txt = message.text.strip()

    if txt.isdigit() and len(txt) == 10:
        url = f"{BASE_URL}/ph-tracker?token={TOKEN}&number={txt}"
        execute_api_call(message, url, "PHONE RECORD", txt)
        return

    if txt.isdigit() and len(txt) == 12:
        url = f"{BASE_URL}/aadhar-info?token={TOKEN}&id={txt}"
        execute_api_call(message, url, "AADHAAR DATABASE", txt)
        return

    if txt.isdigit() and len(txt) == 6:
        url = f"{BASE_URL}/pincode?token={TOKEN}&pincode={txt}"
        execute_api_call(message, url, "AREA PINCODE", txt)
        return

    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", txt):
        url = f"{BASE_URL}/ip-master?token={TOKEN}&ip={txt}"
        execute_api_call(message, url, "NETWORK IP", txt)
        return

    if re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", txt.upper()):
        url = f"{BASE_URL}/ifsc-master?token={TOKEN}&ifsc={txt.upper()}"
        execute_api_call(message, url, "BANK IFSC", txt.upper())
        return

    if re.match(r"^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$", txt.upper().replace(" ", "")):
        clean_rc = txt.upper().replace(" ", "")
        url = f"{BASE_URL}/vehicle-master?token={TOKEN}&rc={clean_rc}"
        execute_api_call(message, url, "RTO VEHICLE", clean_rc)
        return

# ================= RUN =================

if __name__ == "__main__":
    print("👑 CROWN M4 GOV-INTEL BOT STARTED!")
    keep_alive()
    bot.infinity_polling()


        
