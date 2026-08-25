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
    return "👑 MONEY DEVELOPER VIP OSINT System is Running 24/7!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

# ================= CONFIGURATION =================
BOT_TOKEN = "8887168683:AAFU5xQN389gI1WSOhEom41FY0I4-fRy3fs"
ADMIN_ID = 8407090614

# APIs Configuration (यहाँ 'demo' की जगह अपनी असली की डाल सकता है अगर बदलनी हो)
OSINT_KEY = "demo" 
BASE_URL_OSINT = "https://osint-api-delta.vercel.app/api"

DATA_FILE = "users_data.json"
START_PHOTO_PATH = "89372.jpg"  # 🔴 EXACT FILE NAME 

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
        time.sleep(3600)  # Auto delete after 1 hour
        try:
            bot.delete_message(chat_id, message_id)
        except Exception:
            pass
    threading.Thread(target=delete).start()

# ================= PREMIUM UI MENUS =================
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔍 Identity & Govt", callback_data="menu_identity"),
        InlineKeyboardButton("📱 Social & Gaming", callback_data="menu_social")
    )
    markup.add(
        InlineKeyboardButton("🌍 Network & Geo", callback_data="menu_geo"),
        InlineKeyboardButton("🤖 AI & Utilities", callback_data="menu_ai")
    )
    markup.add(InlineKeyboardButton("💎 My VIP Profile", callback_data="profile"))
    return markup

def identity_menu():
    markup = InlineKeyboardMarkup(row_width=2)
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
        InlineKeyboardButton("👻 Snapchat Info", callback_data="ask_snap")
    )
    markup.add(
        InlineKeyboardButton("💻 Github Repos", callback_data="ask_git"),
        InlineKeyboardButton("📧 Email Info", callback_data="ask_email"),
        InlineKeyboardButton("🎮 BGMI Player", callback_data="ask_bgmi")
    )
    markup.add(InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main"))
    return markup

def geo_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🌐 IP Tracker (V1)", callback_data="ask_ip1"),
        InlineKeyboardButton("🌐 IP Tracker (V2)", callback_data="ask_ip2")
    )
    markup.add(
        InlineKeyboardButton("📍 Pincode Info", callback_data="ask_pin"),
        InlineKeyboardButton("🗺️ Country Info", callback_data="ask_country")
    )
    markup.add(InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main"))
    return markup

def ai_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💖 AI Girlfriend", callback_data="ask_aigf"),
        InlineKeyboardButton("🎨 AI Image Gen", callback_data="ask_aiimg")
    )
    markup.add(InlineKeyboardButton("✨ Prompt Gen", callback_data="ask_prompt"))
    markup.add(InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main"))
    return markup

# ================= START COMMAND =================
@bot.message_handler(commands=["start"])
def start(message):
    get_user(message.from_user.id)
    user_steps[message.from_user.id] = None 

    welcome_text = (
        f"<b>👑 MONEY DEVELOPER VIP OSINT 👑</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👋 Welcome to the Database, <b>{message.from_user.first_name}</b>!\n\n"
        f"👤 <b>USER DASHBOARD</b>\n"
        f" ├ <b>Status:</b> 🟢 <i>Secured & Active</i>\n"
        f" ├ <b>Access:</b> VIP Node Terminal\n"
        f" └ <b>System:</b> 30+ Live Trackers\n\n"
        f"⚡ <i>Tap a category below to deploy tools:</i>\n"
    )

    try:
        if os.path.exists(START_PHOTO_PATH):
            with open(START_PHOTO_PATH, "rb") as photo:
                msg = bot.send_photo(message.chat.id, photo, caption=welcome_text, reply_markup=main_menu(), parse_mode="HTML")
        else:
            msg = bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode="HTML")
        
        auto_delete(msg.chat.id, msg.message_id)
    except Exception as e:
        bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode="HTML")

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
            f"👤 <b><u>YOUR VIP PROFILE</u></b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🆔 <b>Name:</b> <i>{call.from_user.first_name}</i>\n"
            f"💎 <b>Credits:</b> {credits_display}\n"
            f"🔍 <b>Total Lookups:</b> <b>{user['lookups']}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<i>Powered by MONEY DEVELOPER</i>"
        )
        bot.send_message(chat_id, info_text, parse_mode="HTML")

    else:
        prompts = {
            "ask_pan": "📇 <i>Send 10-character PAN Card Number.</i>",
            "ask_gst": "🏢 <i>Send 15-character GSTIN Number.</i>",
            "ask_ifsc": "🏦 <i>Send Bank IFSC Code.</i>",
            "ask_imei": "📱 <i>Send 15-digit IMEI Number.</i>",
            "ask_ig_prof": "📸 <i>Send Instagram Username.</i>",
            "ask_ig_dl": "⬇️ <i>Send Instagram Reel/Post URL.</i>",
            "ask_snap": "👻 <i>Send Snapchat Username.</i>",
            "ask_git": "💻 <i>Send GitHub Username.</i>",
            "ask_email": "📧 <i>Send Target Email Address.</i>",
            "ask_bgmi": "🎮 <i>Send BGMI Player ID.</i>",
            "ask_ip1": "🌐 <i>Send Target IP Address (for IP V1).</i>",
            "ask_ip2": "🌐 <i>Send Target IP Address (for IP V2/V3).</i>",
            "ask_pin": "📍 <i>Send 6-digit Pincode.</i>",
            "ask_country": "🗺️ <i>Send Country Name (e.g., india).</i>",
            "ask_aigf": "💖 <i>Send a message to your AI GF!</i>",
            "ask_aiimg": "🎨 <i>Send prompt to generate Image.</i>",
            "ask_prompt": "✨ <i>Send a topic or image URL to generate prompt.</i>"
        }
        
        if call.data in prompts:
            user_steps[user_id] = call.data
            bot.send_message(chat_id, f"🎯 <b>TARGET LOCKED:</b>\n{prompts[call.data]}", parse_mode="HTML")

    bot.answer_callback_query(call.id)

# ================= EXECUTE API ENGINE =================
def execute_api_call(message, endpoint_url, query_label, search_val):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user_id != ADMIN_ID and user["credits"] < 1:
        bot.reply_to(message, "❌ <i>Not enough credits. Contact Admin!</i>", parse_mode="HTML")
        return

    wait_msg = bot.reply_to(message, "📡 <b><i>Extracting MONEY DEVELOPER Live Database...</i></b>", parse_mode="HTML")

    try:
        r = requests.get(endpoint_url, timeout=25)
        
        if r.status_code == 404:
            bot.edit_message_text(f"⚠️ <b>API Error (404):</b> <i>Target data not found or Tool is currently offline.</i>", message.chat.id, wait_msg.message_id, parse_mode="HTML")
            return
        elif r.status_code != 200:
            bot.edit_message_text(f"❌ <b>API Error:</b> <code>{r.status_code}</code>\n<i>Server might be busy.</i>", message.chat.id, wait_msg.message_id, parse_mode="HTML")
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
        
        # 🔴 EXTREME DEVELOPER NAME SCRUBBER (REPLACES ROHIT/FROXTDEVIL) 🔴
        scrub_patterns = [
            r"(?i)rohit\s*padhwe",
            r"(?i)rohit",
            r"(?i)@froxtdevil",
            r"(?i)froxtdevil"
        ]
        
        for pattern in scrub_patterns:
            result_json = re.sub(pattern, "MONEY DEVELOPER", result_json)

        if len(result_json) > 3500:
            result_json = result_json[:3500] + "\n... [DATA TRUNCATED FOR DISPLAY]"

        date = datetime.datetime.now().strftime("%d-%m-%Y %I:%M %p")
        rem_credits = "♾️ Unlimited" if user_id == ADMIN_ID else user["credits"]

        text = f"""
🏛️ <b>MONEY DEVELOPER INTEL SYSTEM</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 <b>TARGET:</b> <i>{query_label}</i>
📌 <b>QUERY:</b> <code>{search_val}</code>
━━━━━━━━━━━━━━━━━━━━━━━━━━
<b><u>DATABASE OUTPUT:</u></b>
<pre>{result_json}</pre>
━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 <b>USER:</b> @{message.from_user.username or 'NoUsername'}
⚡ <b>POWERED BY: MONEY DEVELOPER 👑</b>
"""
        bot.edit_message_text(text, message.chat.id, wait_msg.message_id, parse_mode="HTML")
        auto_delete(message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ <b>Execution Error:</b> <code>System Timeout or Error</code>", message.chat.id, wait_msg.message_id, parse_mode="HTML")

# ================= SMART QUERY ROUTER (ALL ENDPOINTS INTEGRATED) =================
@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def handle_queries(message):
    txt = message.text.strip()
    user_id = message.from_user.id
    current_step = user_steps.get(user_id)
    
    # Reset step
    user_steps[user_id] = None 
    
    # 1. State-Based Routing (Using all user endpoints cleanly)
    if current_step:
        if current_step == "ask_ig_prof":
            url = f"{BASE_URL_OSINT}/instagram-profile-v1?key={OSINT_KEY}&type=profile&username={txt}"
            execute_api_call(message, url, "INSTAGRAM PROFILE V1", txt)
            return
        elif current_step == "ask_ig_dl":
            url = f"{BASE_URL_OSINT}/instagram-download?key={OSINT_KEY}&type=download&url={txt}"
            execute_api_call(message, url, "INSTAGRAM DOWNLOAD", txt)
            return
        elif current_step == "ask_snap":
            url = f"{BASE_URL_OSINT}/snapchat-all?key={OSINT_KEY}&action=all&username={txt}"
            execute_api_call(message, url, "SNAPCHAT OSINT", txt)
            return
        elif current_step == "ask_git":
            url = f"{BASE_URL_OSINT}/github-repos?key={OSINT_KEY}&q={txt}"
            execute_api_call(message, url, "GITHUB REPOS SEARCH", txt)
            return
        elif current_step == "ask_country":
            url = f"{BASE_URL_OSINT}/country-info?key={OSINT_KEY}&name={txt}"
            execute_api_call(message, url, "COUNTRY INTEL", txt)
            return
        elif current_step == "ask_aigf":
            url = f"{BASE_URL_OSINT}/ai-gf?key={OSINT_KEY}&prompt={txt}"
            execute_api_call(message, url, "AI GIRLFRIEND", txt)
            return
        elif current_step == "ask_aiimg":
            url = f"{BASE_URL_OSINT}/image-generator?key={OSINT_KEY}&prompt={txt}"
            execute_api_call(message, url, "AI IMAGE GENERATOR", txt)
            return
        elif current_step == "ask_prompt":
            url = f"{BASE_URL_OSINT}/prompt-generator?key={OSINT_KEY}&url={txt}"
            execute_api_call(message, url, "PROMPT GENERATOR", txt)
            return
        elif current_step == "ask_pan":
            url = f"{BASE_URL_OSINT}/pan-info?key={OSINT_KEY}&pan={txt.upper()}"
            execute_api_call(message, url, "PAN CARD INFO", txt.upper())
            return
        elif current_step == "ask_gst":
            url = f"{BASE_URL_OSINT}/gst-search?key={OSINT_KEY}&gstin={txt.upper()}"
            execute_api_call(message, url, "GST SEARCH", txt.upper())
            return
        elif current_step == "ask_ifsc":
            url = f"{BASE_URL_OSINT}/ifsc-info?key={OSINT_KEY}&ifsc={txt.upper()}"
            execute_api_call(message, url, "BANK IFSC INFO", txt.upper())
            return
        elif current_step == "ask_imei":
            url = f"{BASE_URL_OSINT}/imei-info?key={OSINT_KEY}&imei_number={txt}"
            execute_api_call(message, url, "IMEI INFO CHECK", txt)
            return
        elif current_step == "ask_email":
            url = f"{BASE_URL_OSINT}/email-info?key={OSINT_KEY}&mail={txt}"
            execute_api_call(message, url, "EMAIL INFO LOOKUP", txt)
            return
        elif current_step == "ask_bgmi":
            url = f"{BASE_URL_OSINT}/bgmi-info?key={OSINT_KEY}&user={txt}"
            execute_api_call(message, url, "BGMI PLAYER INFO", txt)
            return
        elif current_step == "ask_ip1":
            url = f"{BASE_URL_OSINT}/ip-v1?key={OSINT_KEY}&query={txt}"
            execute_api_call(message, url, "IP INFO V1", txt)
            return
        elif current_step == "ask_ip2":
            url = f"{BASE_URL_OSINT}/ip-v2?key={OSINT_KEY}&ip={txt}"
            execute_api_call(message, url, "IP INFO V2", txt)
            return
        elif current_step == "ask_pin":
            url = f"{BASE_URL_OSINT}/pincode-info?key={OSINT_KEY}&pincode={txt}"
            execute_api_call(message, url, "PINCODE INFO", txt)
            return

    # 2. Auto-Detect Smart Routing
    if re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", txt):
        url = f"{BASE_URL_OSINT}/email-info?key={OSINT_KEY}&mail={txt}"
        execute_api_call(message, url, "EMAIL INFO LOOKUP", txt)
    elif re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", txt.upper()):
        url = f"{BASE_URL_OSINT}/pan-info?key={OSINT_KEY}&pan={txt.upper()}"
        execute_api_call(message, url, "PAN CARD INFO", txt.upper())
    elif txt.isdigit() and len(txt) == 15:
        url = f"{BASE_URL_OSINT}/imei-info?key={OSINT_KEY}&imei_number={txt}"
        execute_api_call(message, url, "IMEI INFO CHECK", txt)
    elif txt.isdigit() and len(txt) in [8, 9, 11, 13]:
        url = f"{BASE_URL_OSINT}/bgmi-info?key={OSINT_KEY}&user={txt}"
        execute_api_call(message, url, "BGMI PLAYER INFO", txt)
    elif txt.isdigit() and len(txt) == 6:
        url = f"{BASE_URL_OSINT}/pincode-info?key={OSINT_KEY}&pincode={txt}"
        execute_api_call(message, url, "PINCODE INFO", txt)
    elif re.match(r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z0-9]{1}Z[A-Z0-9]{1}$", txt.upper()):
        url = f"{BASE_URL_OSINT}/gst-search?key={OSINT_KEY}&gstin={txt.upper()}"
        execute_api_call(message, url, "GST SEARCH", txt.upper())
    elif re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", txt):
        url = f"{BASE_URL_OSINT}/ip-v2?key={OSINT_KEY}&ip={txt}"
        execute_api_call(message, url, "IP INFO V2", txt)
    elif re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", txt.upper()):
        url = f"{BASE_URL_OSINT}/ifsc-info?key={OSINT_KEY}&ifsc={txt.upper()}"
        execute_api_call(message, url, "BANK IFSC INFO", txt.upper())
    else:
        msg = bot.reply_to(message, "❌ <b>Format Unidentified!</b>\n<i>Please select a tool from the /start menu first.</i>", parse_mode="HTML")
        auto_delete(msg.chat.id, msg.message_id)

# ================= RUN SERVER =================
if __name__ == "__main__":
    print("👑 MONEY DEVELOPER VIP OSINT BOT IS ONLINE!")
    keep_alive()
    bot.infinity_polling()
