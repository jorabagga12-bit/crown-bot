import datetime
import json
import os
import re
import threading
import time
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from flask import Flask

# ================= FLASK SERVER WITH MODERN WEB GUI =================
app = Flask('')

@app.route('/')
def home():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>👑 CROWN VIP OSINT - Dashboard</title>
        <style>
            body { background-color: #0f172a; color: #f8fafc; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: rgba(30, 41, 59, 0.75); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.1); padding: 40px; border-radius: 18px; text-align: center; max-width: 480px; width: 90%; }
            h1 { color: #38bdf8; font-size: 22px; margin-bottom: 10px; }
            .status { background: rgba(34, 197, 94, 0.15); color: #4ade80; padding: 6px 16px; border-radius: 20px; font-size: 13px; font-weight: 600; display: inline-block; margin-bottom: 20px; }
            .footer { margin-top: 20px; font-size: 11px; color: #475569; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>👑 CROWN VIP OSINT</h1>
            <div class="status">🟢 System Online & Secure</div>
            <div class="footer">Powered by CROWN 👑</div>
        </div>
    </body>
    </html>
    """
    return html_content

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
OSINT_KEY = "demo"
BASE_URL_MAIN = "https://xpolitesupgrade-api.darrify-api.workers.dev/api"
BASE_URL_OSINT = "https://osint-api-delta.vercel.app/api"

DATA_FILE = "users_data.json"
START_PHOTO_PATH = "89372.jpg"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
total_lookups = 0
user_steps = {}

# ================= DATA PERSISTENCE =================
def load_data():
    global total_lookups
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                total_lookups = data.get("total_lookups", 0)
                return data.get("users", {})
        except Exception:
            return {}
    return {}

def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": users, "total_lookups": total_lookups}, f, indent=4, ensure_ascii=False)
    except Exception:
        pass

users = load_data()

def get_user(user_id):
    uid = str(user_id)
    if uid not in users:
        users[uid] = {"credits": 20, "lookups": 0}
        save_data()
    return users[uid]

def auto_delete(chat_id, message_id):
    def delete():
        time.sleep(3600)
        try:
            bot.delete_message(chat_id, message_id)
        except Exception:
            pass
    threading.Thread(target=delete).start()

# ================= REPLY KEYBOARD (BOTTOM BUTTONS) =================
def get_reply_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("🚗 Vehicle RC Lookup"),
        KeyboardButton("🇮🇳 Indian Number Lookup")
    )
    markup.add(
        KeyboardButton("📞 Truecaller Lookup"),
        KeyboardButton("🎵 Song Downloader")
    )
    markup.add(
        KeyboardButton("🏢 GST Search"),
        KeyboardButton("🏦 IFSC Lookup")
    )
    markup.add(
        KeyboardButton("💎 My Credits")
    )
    return markup

# ================= PREMIUM UI MENUS =================
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔍 Identity & Govt", callback_data="menu_identity"),
        InlineKeyboardButton("📱 Social & Media", callback_data="menu_social")
    )
    markup.add(
        InlineKeyboardButton("🌍 Network & Tools", callback_data="menu_geo"),
        InlineKeyboardButton("🤖 AI & Utilities", callback_data="menu_ai")
    )
    markup.add(InlineKeyboardButton("💎 My VIP Profile", callback_data="profile"))
    return markup

def identity_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📱 Phone Number", callback_data="ask_phone"),
        InlineKeyboardButton("🚗 Vehicle RC", callback_data="ask_vehicle")
    )
    markup.add(
        InlineKeyboardButton("📞 Truecaller", callback_data="ask_truecaller"),
        InlineKeyboardButton("🪪 Aadhaar Info", callback_data="ask_aadhar")
    )
    markup.add(
        InlineKeyboardButton("📇 PAN Card", callback_data="ask_pan"),
        InlineKeyboardButton("🏢 GST Search", callback_data="ask_gst")
    )
    markup.add(
        InlineKeyboardButton("🏦 IFSC Bank", callback_data="ask_ifsc"),
        InlineKeyboardButton("📱 IMEI Info", callback_data="ask_imei")
    )
    markup.add(InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main"))
    return markup

def social_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📸 Insta Profile", callback_data="ask_ig_prof"),
        InlineKeyboardButton("⬇️ Insta Download", callback_data="ask_ig_dl"),
        InlineKeyboardButton("🎵 Song Downloader", callback_data="ask_song")
    )
    markup.add(
        InlineKeyboardButton("👥 Telegram Info", callback_data="ask_tg"),
        InlineKeyboardButton("📺 YouTube Downloader", callback_data="ask_ytdl"),
        InlineKeyboardButton("🎮 BGMI Player", callback_data="ask_bgmi")
    )
    markup.add(InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main"))
    return markup

def geo_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🌐 IP Tracker (V2)", callback_data="ask_ip2"),
        InlineKeyboardButton("📍 Pincode Info", callback_data="ask_pin")
    )
    markup.add(
        InlineKeyboardButton("🌤️ Weather Info", callback_data="ask_weather"),
        InlineKeyboardButton("🌐 Website Scraper", callback_data="ask_web")
    )
    markup.add(InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main"))
    return markup

def ai_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💖 AI Girlfriend", callback_data="ask_aigf"),
        InlineKeyboardButton("🎨 AI Image Gen", callback_data="ask_aiimg")
    )
    markup.add(InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main"))
    return markup

# ================= START COMMAND =================
@bot.message_handler(commands=["start"])
def start(message):
    get_user(message.from_user.id)
    user_steps[message.from_user.id] = None 

    welcome_text = (
        f"<b>👑 CROWN VIP OSINT SYSTEM 👑</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👋 Welcome to the Database, <b>{message.from_user.first_name}</b>!\n\n"
        f"⚡ <i>Tap a category below or use the quick buttons:</i>\n"
    )

    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode="HTML")
    bot.send_message(message.chat.id, "👇 <b>Quick Access Keyboards:</b>", reply_markup=get_reply_keyboard(), parse_mode="HTML")

# ================= INLINE CALLBACK HANDLER =================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    
    if call.data == "menu_main":
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=main_menu())
    elif call.data == "menu_identity":
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=identity_menu())
    elif call.data == "menu_social":
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=social_menu())
    elif call.data == "menu_geo":
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=geo_menu())
    elif call.data == "menu_ai":
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=ai_menu())
        
    elif call.data == "profile":
        user = get_user(user_id)
        credits_display = "♾️ <b>Unlimited (VIP)</b>" if user_id == ADMIN_ID else f"<b>{user['credits']}</b>"
        info_text = (
            f"👑 <b><u>CROWN VIP PROFILE</u></b> 👑\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🆔 <b>Name:</b> <i>{call.from_user.first_name}</i>\n"
            f"💎 <b>Credits:</b> {credits_display}\n"
            f"🔍 <b>Total Lookups:</b> <b>{user['lookups']}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<i>Powered by CROWN 👑</i>"
        )
        bot.send_message(chat_id, info_text, parse_mode="HTML")

    else:
        prompts = {
            "ask_phone": "📱 <i>Send 10-digit Phone Number.</i>",
            "ask_vehicle": "🚗 <i>Send Vehicle Registration Number (e.g. MH12DE1433).</i>",
            "ask_truecaller": "📞 <i>Send Phone Number for Truecaller Lookup.</i>",
            "ask_aadhar": "🪪 <i>Send 12-digit Aadhaar Number.</i>",
            "ask_pan": "📇 <i>Send 10-character PAN Card Number.</i>",
            "ask_gst": "🏢 <i>Send 15-character GSTIN Number.</i>",
            "ask_ifsc": "🏦 <i>Send Bank IFSC Code.</i>",
            "ask_imei": "📱 <i>Send 15-digit IMEI Number.</i>",
            "ask_ig_prof": "📸 <i>Send Instagram Username.</i>",
            "ask_ig_dl": "⬇️ <i>Send Instagram Reel/Post URL.</i>",
            "ask_song": "🎵 <i>Send Song Name to Download.</i>",
            "ask_tg": "👥 <i>Send Telegram User ID.</i>",
            "ask_ytdl": "📺 <i>Send YouTube Video URL.</i>",
            "ask_bgmi": "🎮 <i>Send BGMI Player ID.</i>",
            "ask_ip2": "🌐 <i>Send Target IP Address.</i>",
            "ask_pin": "📍 <i>Send 6-digit Pincode.</i>",
            "ask_weather": "🌤️ <i>Send City Name for Weather Info.</i>",
            "ask_web": "🌐 <i>Send Website URL to Scrape.</i>",
            "ask_aigf": "💖 <i>Send a message to your AI GF!</i>",
            "ask_aiimg": "🎨 <i>Send prompt to generate Image.</i>"
        }
        
        if call.data in prompts:
            user_steps[user_id] = call.data
            bot.send_message(chat_id, f"👑 <b>CROWN TARGET LOCKED:</b>\n{prompts[call.data]}", parse_mode="HTML")

    bot.answer_callback_query(call.id)

# ================= EXECUTE API ENGINE WITH STRICT SCRUBBING =================
def execute_api_call(message, endpoint_url, query_label, search_val):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user_id != ADMIN_ID and user["credits"] < 1:
        bot.reply_to(message, "❌ <i>Not enough credits. Contact Admin!</i>", parse_mode="HTML")
        return

    wait_msg = bot.reply_to(message, "👑📡 <b><i>Extracting CROWN Live Database...</i></b>", parse_mode="HTML")

    try:
        r = requests.get(endpoint_url, timeout=25)
        
        if r.status_code == 404:
            bot.edit_message_text(f"⚠️ <b>API Error (404):</b> <i>Target data not found or Tool is currently offline.</i>", message.chat.id, wait_msg.message_id, parse_mode="HTML")
            return
            
        try:
            api_response = r.json()
        except:
            api_response = {"response": r.text}

        if user_id != ADMIN_ID:
            user["credits"] -= 1

        user["lookups"] += 1
        global total_lookups
        total_lookups += 1
        save_data()

        result_json = json.dumps(api_response, indent=2, ensure_ascii=False)
        
        # 🔴 EXTREME SCRUBBER: ONLYHACKERZON KO HATA KE CROWN LAGA RAHA HAI 🔴
        scrub_patterns = [
            r"(?i)onlyh4ckerzon",
            r"(?i)onlyhackerzon",
            r"(?i)rohit\s*padhwe",
            r"(?i)rohit",
            r"(?i)@froxtdevil",
            r"(?i)froxtdevil",
            r"(?i)https?://t\.me/\S+"
        ]
        
        for pattern in scrub_patterns:
            result_json = re.sub(pattern, "Crown 👑", result_json)

        if len(result_json) > 3500:
            result_json = result_json[:3500] + "\n... [DATA TRUNCATED]"

        text = f"""
👑 <b>CROWN INTEL SYSTEM</b> 👑
━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 <b>TARGET:</b> <i>{query_label}</i>
📌 <b>VALUE:</b> <code>{search_val}</code>
━━━━━━━━━━━━━━━━━━━━━━━━━━
<b><u>DATABASE OUTPUT:</u></b>
<pre>{result_json}</pre>
━━━━━━━━━━━━━━━━━━━━━━━━━━
👑⚡ <b>POWERED BY: CROWN 👑</b>
"""
        bot.edit_message_text(text, message.chat.id, wait_msg.message_id, parse_mode="HTML")
        auto_delete(message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ <b>Execution Error:</b> <code>System Timeout or API Down</code>", message.chat.id, wait_msg.message_id, parse_mode="HTML")

# ================= SMART QUERY ROUTER =================
@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def handle_queries(message):
    txt = message.text.strip()
    user_id = message.from_user.id

    # 0. Handle Reply Keyboard Button Clicks
    if txt == "🚗 Vehicle RC Lookup":
        user_steps[user_id] = "ask_vehicle"
        bot.reply_to(message, "👑 <b>CROWN TARGET LOCKED:</b>\n<i>Send Vehicle Registration Number.</i>", parse_mode="HTML")
        return
    elif txt == "🇮🇳 Indian Number Lookup":
        user_steps[user_id] = "ask_phone"
        bot.reply_to(message, "👑 <b>CROWN TARGET LOCKED:</b>\n<i>Send 10-digit Phone Number.</i>", parse_mode="HTML")
        return
    elif txt == "📞 Truecaller Lookup":
        user_steps[user_id] = "ask_truecaller"
        bot.reply_to(message, "👑 <i>Send Phone Number for Truecaller Lookup.</i>", parse_mode="HTML")
        return
    elif txt == "🎵 Song Downloader":
        user_steps[user_id] = "ask_song"
        bot.reply_to(message, "👑 <i>Send Song Name to Download.</i>", parse_mode="HTML")
        return
    elif txt == "🏢 GST Search":
        user_steps[user_id] = "ask_gst"
        bot.reply_to(message, "👑 <i>Send 15-character GSTIN Number.</i>", parse_mode="HTML")
        return
    elif txt == "🏦 IFSC Lookup":
        user_steps[user_id] = "ask_ifsc"
        bot.reply_to(message, "👑 <i>Send Bank IFSC Code.</i>", parse_mode="HTML")
        return
    elif txt == "💎 My Credits":
        user = get_user(user_id)
        bot.reply_to(message, f"👑 <b>Credits:</b> {user['credits']}", parse_mode="HTML")
        return

    current_step = user_steps.get(user_id)
    user_steps[user_id] = None 
    
    # 1. State-Based Routing (All New APIs Integrated)
    if current_step:
        if current_step == "ask_vehicle":
            url = f"{BASE_URL_OSINT}/vehicle-v1?key={OSINT_KEY}&type=v1&rc={txt.upper()}"
            execute_api_call(message, url, "VEHICLE RC V1", txt.upper())
            return
        elif current_step == "ask_phone":
            url = f"{BASE_URL_MAIN}/ph-tracker?token={TOKEN}&number={txt}"
            execute_api_call(message, url, "PHONE RECORD", txt)
            return
        elif current_step == "ask_truecaller":
            url = f"{BASE_URL_OSINT}/truecaller-info?key={OSINT_KEY}&number={txt}"
            execute_api_call(message, url, "TRUECALLER INFO", txt)
            return
        elif current_step == "ask_song":
            url = f"{BASE_URL_OSINT}/song-download?key={OSINT_KEY}&song={txt}"
            execute_api_call(message, url, "SONG DOWNLOADER", txt)
            return
        elif current_step == "ask_tg":
            url = f"{BASE_URL_OSINT}/telegram-info?key={OSINT_KEY}&tg={txt}"
            execute_api_call(message, url, "TELEGRAM USER INFO", txt)
            return
        elif current_step == "ask_ytdl":
            url = f"{BASE_URL_OSINT}/youtube-download?key={OSINT_KEY}&download=1&url={txt}"
            execute_api_call(message, url, "YOUTUBE DOWNLOADER", txt)
            return
        elif current_step == "ask_weather":
            url = f"{BASE_URL_OSINT}/weather-info?key={OSINT_KEY}&city={txt}"
            execute_api_call(message, url, "WEATHER INFO", txt)
            return
        elif current_step == "ask_web":
            url = f"{BASE_URL_OSINT}/website-source?key={OSINT_KEY}&url={txt}"
            execute_api_call(message, url, "WEBSITE SCRAPER", txt)
            return
        elif current_step == "ask_aadhar":
            url = f"{BASE_URL_MAIN}/aadhar-info?token={TOKEN}&id={txt}"
            execute_api_call(message, url, "AADHAAR NUMBER", txt)
            return
        elif current_step == "ask_pan":
            url = f"{BASE_URL_OSINT}/pan-info?key={OSINT_KEY}&pan={txt.upper()}"
            execute_api_call(message, url, "PAN CARD", txt.upper())
            return
        elif current_step == "ask_gst":
            url = f"{BASE_URL_OSINT}/gst-search?key={OSINT_KEY}&gstin={txt.upper()}"
            execute_api_call(message, url, "GST SEARCH", txt.upper())
            return
        elif current_step == "ask_ifsc":
            url = f"{BASE_URL_OSINT}/ifsc-info?key={OSINT_KEY}&ifsc={txt.upper()}"
            execute_api_call(message, url, "IFSC LOOKUP", txt.upper())
            return
        elif current_step == "ask_imei":
            url = f"{BASE_URL_OSINT}/imei-info?key={OSINT_KEY}&imei_number={txt}"
            execute_api_call(message, url, "IMEI INFO", txt)
            return
        elif current_step == "ask_bgmi":
            url = f"{BASE_URL_OSINT}/bgmi-info?key={OSINT_KEY}&user={txt}"
            execute_api_call(message, url, "BGMI PLAYER", txt)
            return
        elif current_step == "ask_pin":
            url = f"{BASE_URL_OSINT}/pincode-info?key={OSINT_KEY}&pincode={txt}"
            execute_api_call(message, url, "PINCODE INFO", txt)
            return

    # 2. Auto-Detect Smart Routing
    if txt.isdigit() and len(txt) == 10:
        url = f"{BASE_URL_MAIN}/ph-tracker?token={TOKEN}&number={txt}"
        execute_api_call(message, url, "PHONE RECORD", txt)
    elif txt.isdigit() and len(txt) == 12:
        url = f"{BASE_URL_MAIN}/aadhar-info?token={TOKEN}&id={txt}"
        execute_api_call(message, url, "AADHAAR NUMBER", txt)
    elif re.match(r"^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$", txt.upper()):
        url = f"{BASE_URL_OSINT}/vehicle-v1?key={OSINT_KEY}&type=v1&rc={txt.upper()}"
        execute_api_call(message, url, "VEHICLE RC V1", txt.upper())
    elif re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", txt.upper()):
        url = f"{BASE_URL_OSINT}/pan-info?key={OSINT_KEY}&pan={txt.upper()}"
        execute_api_call(message, url, "PAN CARD INFO", txt.upper())
    elif txt.isdigit() and len(txt) == 6:
        url = f"{BASE_URL_OSINT}/pincode-info?key={OSINT_KEY}&pincode={txt}"
        execute_api_call(message, url, "PINCODE INFO", txt)
    else:
        msg = bot.reply_to(message, "❌ <b>Format Unidentified!</b>\n<i>Please select a tool from the /start menu first.</i>", parse_mode="HTML")
        auto_delete(msg.chat.id, msg.message_id)

# ================= RUN SERVER =================
if __name__ == "__main__":
    print("👑 CROWN VIP BOT IS ONLINE WITH ALL APIS!")
    keep_alive()
    bot.infinity_polling()

