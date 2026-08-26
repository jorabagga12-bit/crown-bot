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

# ================= FLASK SERVER FOR 24/7 UPTIME =================
app = Flask('')

@app.route('/')
def home():
    return "<h1>👑 CROWN M4 VIP OSINT - All 30+ APIs Active</h1>"

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
TOKEN = "xpol_Demo_combo_a811c2fb" # Old APIs
OSINT_KEY = "demo" # New 30 APIs

BASE_URL_MAIN = "https://xpolitesupgrade-api.darrify-api.workers.dev/api"
BASE_URL_OSINT = "https://osint-api-delta.vercel.app/api"

DATA_FILE = "users_data.json"
START_PHOTO_PATH = "89395.jpg" # Reference to your provided photo

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
        users[uid] = {"credits": 50, "lookups": 0}
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

# ================= REPLY KEYBOARD =================
def get_reply_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("🇮🇳 Indian Number Lookup"),
        KeyboardButton("🪪 Aadhaar Card Lookup")
    )
    markup.add(
        KeyboardButton("🚗 Vehicle RC Info"),
        KeyboardButton("📧 Email Info Lookup")
    )
    markup.add(
        KeyboardButton("🎮 BGMI Player Info"),
        KeyboardButton("💎 My Credits")
    )
    return markup

# ================= VIP NESTED MENUS =================
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔍 Identity & Govt", callback_data="menu_identity"),
        InlineKeyboardButton("🌍 IP & Network", callback_data="menu_ip")
    )
    markup.add(
        InlineKeyboardButton("📸 Instagram Tools", callback_data="menu_insta"),
        InlineKeyboardButton("👻 Snapchat Tools", callback_data="menu_snap")
    )
    markup.add(
        InlineKeyboardButton("🤖 AI & Utility", callback_data="menu_ai"),
        InlineKeyboardButton("💻 GitHub & Email", callback_data="menu_misc")
    )
    markup.add(InlineKeyboardButton("💎 My VIP Profile", callback_data="profile"))
    return markup

def identity_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📱 Phone Number", callback_data="ask_phone"),
        InlineKeyboardButton("🪪 Aadhaar Info", callback_data="ask_aadhar")
    )
    markup.add(
        InlineKeyboardButton("📇 PAN Card", callback_data="ask_pan"),
        InlineKeyboardButton("🚗 Vehicle RC", callback_data="ask_vehicle")
    )
    markup.add(
        InlineKeyboardButton("🏢 GST Direct", callback_data="ask_gst_dir"),
        InlineKeyboardButton("🏢 GST Search", callback_data="ask_gst_src")
    )
    markup.add(
        InlineKeyboardButton("🏦 IFSC Bank", callback_data="ask_ifsc"),
        InlineKeyboardButton("📱 IMEI Info", callback_data="ask_imei")
    )
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="menu_main"))
    return markup

def insta_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🌟 Best Profile V1", callback_data="ig_best"),
        InlineKeyboardButton("👤 Profile V1", callback_data="ig_p_v1")
    )
    markup.add(
        InlineKeyboardButton("👤 Profile V2", callback_data="ig_p_v2"),
        InlineKeyboardButton("👤 Profile V3", callback_data="ig_p_v3")
    )
    markup.add(
        InlineKeyboardButton("👤 Profile V3 V2", callback_data="ig_p_v32"),
        InlineKeyboardButton("⬇️ DL Reel/Video", callback_data="ig_dl")
    )
    markup.add(
        InlineKeyboardButton("⬇️ Downloads V1", callback_data="ig_dl_v1"),
        InlineKeyboardButton("📸 Media V1", callback_data="ig_media")
    )
    markup.add(
        InlineKeyboardButton("📝 Posts V2", callback_data="ig_post"),
        InlineKeyboardButton("📊 Stats V1", callback_data="ig_stat")
    )
    markup.add(
        InlineKeyboardButton("🧑 User V1", callback_data="ig_user"),
        InlineKeyboardButton("🔙 Back", callback_data="menu_main")
    )
    return markup

def snap_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("👻 All Data", callback_data="sn_all"),
        InlineKeyboardButton("🌟 Highlights", callback_data="sn_high")
    )
    markup.add(
        InlineKeyboardButton("📖 Story", callback_data="sn_story"),
        InlineKeyboardButton("🔙 Back", callback_data="menu_main")
    )
    return markup

def ip_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🌐 IP Info V1", callback_data="ip_v1"),
        InlineKeyboardButton("🌐 IP Info V2", callback_data="ip_v2")
    )
    markup.add(
        InlineKeyboardButton("🌐 IP Info V3", callback_data="ip_v3"),
        InlineKeyboardButton("📍 Pincode Info", callback_data="ask_pin")
    )
    markup.add(
        InlineKeyboardButton("🗺️ Country Info", callback_data="ask_country"),
        InlineKeyboardButton("🔙 Back", callback_data="menu_main")
    )
    return markup

def ai_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💖 AI Girlfriend", callback_data="ask_aigf"),
        InlineKeyboardButton("🎨 AI Image Gen", callback_data="ask_aiimg")
    )
    markup.add(
        InlineKeyboardButton("✨ Prompt Gen", callback_data="ask_prompt"),
        InlineKeyboardButton("🔙 Back", callback_data="menu_main")
    )
    return markup

def misc_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📧 Email Info", callback_data="ask_email"),
        InlineKeyboardButton("💻 Github Repos", callback_data="ask_git")
    )
    markup.add(
        InlineKeyboardButton("🎮 BGMI Player", callback_data="ask_bgmi"),
        InlineKeyboardButton("🔙 Back", callback_data="menu_main")
    )
    return markup

# ================= START COMMAND =================
@bot.message_handler(commands=["start"])
def start(message):
    get_user(message.from_user.id)
    user_steps[message.from_user.id] = None 

    welcome_text = (
        f"🌟 <b><u>𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗖𝗥𝗢𝗪𝗡 𝗠𝟰 𝗩𝗜𝗣</u></b> 🌟\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👋 Hello <b>{message.from_user.first_name}</b>,\n"
        f"<i>All 30+ OSINT & Utility APIs are Live!</i>\n\n"
        f"👑 <i>Select a category below to start processing.</i>\n"
    )

    try:
        if os.path.exists(START_PHOTO_PATH):
            with open(START_PHOTO_PATH, "rb") as photo:
                msg = bot.send_photo(message.chat.id, photo, caption=welcome_text, reply_markup=main_menu(), parse_mode="HTML")
        else:
            msg = bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode="HTML")
        
        bot.send_message(message.chat.id, "👇 <b>Quick Access Menu:</b>", reply_markup=get_reply_keyboard(), parse_mode="HTML")
        auto_delete(msg.chat.id, msg.message_id)
    except Exception as e:
        bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode="HTML")
        bot.send_message(message.chat.id, "👇 <b>Quick Access Menu:</b>", reply_markup=get_reply_keyboard(), parse_mode="HTML")

# ================= INLINE CALLBACK HANDLER =================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    
    menus = {
        "menu_main": main_menu,
        "menu_identity": identity_menu,
        "menu_insta": insta_menu,
        "menu_snap": snap_menu,
        "menu_ip": ip_menu,
        "menu_ai": ai_menu,
        "menu_misc": misc_menu
    }
    
    if call.data in menus:
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=menus[call.data]())
        bot.answer_callback_query(call.id)
        return

    if call.data == "profile":
        user = get_user(user_id)
        credits_display = "♾️ <b>Unlimited (VIP)</b>" if user_id == ADMIN_ID else f"<b>{user['credits']}</b>"
        info_text = (
            f"👑 <b><u>CROWN X MONEY VIP PROFILE</u></b> 👑\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🆔 <b>Name:</b> <i>{call.from_user.first_name}</i>\n"
            f"💎 <b>Credits:</b> {credits_display}\n"
            f"🔍 <b>Total Lookups:</b> <b>{user['lookups']}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<i>Powered by CROWN 👑 M4</i>"
        )
        bot.send_message(chat_id, info_text, parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return

    prompts = {
        "ask_phone": "📱 <i>Send 10-digit Phone Number.</i>",
        "ask_aadhar": "🪪 <i>Send 12-digit Aadhaar Number.</i>",
        "ask_pan": "📇 <i>Send 10-character PAN Card Number.</i>",
        "ask_vehicle": "🚗 <i>Send Vehicle Registration Number (e.g. MH01AB1234).</i>",
        "ask_gst_dir": "🏢 <i>Send GSTIN Number for Direct Check.</i>",
        "ask_gst_src": "🏢 <i>Send GSTIN Number for Full Search.</i>",
        "ask_ifsc": "🏦 <i>Send Bank IFSC Code.</i>",
        "ask_imei": "📱 <i>Send 15-digit IMEI Number.</i>",
        
        "ig_best": "🌟 <i>Send Insta Username (Best V1).</i>",
        "ig_p_v1": "👤 <i>Send Insta Username (Profile V1).</i>",
        "ig_p_v2": "👤 <i>Send Insta Username (Profile V2).</i>",
        "ig_p_v3": "👤 <i>Send Insta Username (Profile V3).</i>",
        "ig_p_v32": "👤 <i>Send Insta Username (Profile V3 V2).</i>",
        "ig_dl": "⬇️ <i>Send Insta Reel/Post URL for Download.</i>",
        "ig_dl_v1": "⬇️ <i>Send Insta Username (Downloads V1).</i>",
        "ig_media": "📸 <i>Send Insta Username (Media V1).</i>",
        "ig_post": "📝 <i>Send Insta Username (Posts V2).</i>",
        "ig_stat": "📊 <i>Send Insta Username (Stats V1).</i>",
        "ig_user": "🧑 <i>Send Insta Username (User V1).</i>",

        "sn_all": "👻 <i>Send Snapchat Username (All Data).</i>",
        "sn_high": "🌟 <i>Send Snapchat Username (Highlights).</i>",
        "sn_story": "📖 <i>Send Snapchat Username (Story).</i>",

        "ip_v1": "🌐 <i>Send IP Address (V1).</i>",
        "ip_v2": "🌐 <i>Send IP Address (V2).</i>",
        "ip_v3": "🌐 <i>Send IP Address (V3).</i>",
        "ask_pin": "📍 <i>Send 6-digit Pincode.</i>",
        "ask_country": "🗺️ <i>Send Country Name (e.g. india).</i>",

        "ask_aigf": "💖 <i>Send a message to your AI GF!</i>",
        "ask_aiimg": "🎨 <i>Send prompt to generate Image.</i>",
        "ask_prompt": "✨ <i>Send a topic or URL to generate prompt.</i>",
        "ask_email": "📧 <i>Send Target Email Address.</i>",
        "ask_git": "💻 <i>Send GitHub Username.</i>",
        "ask_bgmi": "🎮 <i>Send BGMI Player ID.</i>"
    }
    
    if call.data in prompts:
        user_steps[user_id] = call.data
        bot.send_message(chat_id, f"👑 <b>CROWN TARGET LOCKED:</b>\n{prompts[call.data]}", parse_mode="HTML")

    bot.answer_callback_query(call.id)

# ================= EXECUTE API ENGINE WITH EXACT SCREENSHOT FOOTER =================
def execute_api_call(message, endpoint_url):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user_id != ADMIN_ID and user["credits"] < 1:
        bot.reply_to(message, "❌ <i>Not enough credits. Contact Admin!</i>", parse_mode="HTML")
        return

    wait_msg = bot.reply_to(message, "👑📡 <b><i>Extracting Live Database...</i></b>", parse_mode="HTML")

    try:
        r = requests.get(endpoint_url, timeout=30)
        
        # Vehicle fix & general error handle
        try:
            api_response = r.json()
        except Exception:
            if r.status_code == 200:
                api_response = {"response": r.text}
            else:
                api_response = {"error": f"API returned status {r.status_code}", "details": "Server might be down or data not found."}

        if user_id != ADMIN_ID:
            user["credits"] -= 1

        user["lookups"] += 1
        global total_lookups
        total_lookups += 1
        save_data()

        result_json = json.dumps(api_response, indent=2, ensure_ascii=False)
        
        # Scrubbing unwanted names
        scrub_patterns = [r"(?i)rohit\s*padhwe", r"(?i)rohit", r"(?i)@froxtdevil", r"(?i)froxtdevil", r"(?i)onlyhackerzon"]
        for pattern in scrub_patterns:
            result_json = re.sub(pattern, "CROWN M4", result_json)

        if len(result_json) > 3000:
            result_json = result_json[:3000] + "\n... [DATA TRUNCATED FOR DISPLAY]"

        username = message.from_user.username or message.from_user.first_name
        
        # 🔥 THE EXACT FOOTER FROM YOUR SCREENSHOT (LINK PREVIEW ENABLED) 🔥
        text = f"""<pre>{result_json}</pre>
━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 <b>USER:</b> @{username}
💎 <b>REMAINING CREDITS:</b> {user['credits']}

🚀 <b>OFFICIAL TELEGRAM:</b> @LIFExPAI
📢 <b>JOIN CHANNEL:</b> https://t.me/LIFExPAI
⚡ <b>POWERED & CREATED BY: CROWN 👑 M4</b>
"""     
        # disable_web_page_preview=False => "pyara sa photo niche" aayega
        bot.edit_message_text(text, message.chat.id, wait_msg.message_id, parse_mode="HTML", disable_web_page_preview=False)
        auto_delete(message.chat.id, wait_msg.message_id)

    except requests.exceptions.RequestException as e:
        bot.edit_message_text(f"❌ <b>API Timeout/Error!</b>\n<i>The server is currently unreachable.</i>", message.chat.id, wait_msg.message_id, parse_mode="HTML")
    except Exception as e:
        bot.edit_message_text(f"❌ <b>Execution Error!</b>\n<i>Invalid Response.</i>", message.chat.id, wait_msg.message_id, parse_mode="HTML")

# ================= SMART QUERY ROUTER (ALL 30 APIs CONNECTED) =================
@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def handle_queries(message):
    txt = message.text.strip()
    user_id = message.from_user.id
    
    # Bottom Keyboard Catchers
    if txt == "🇮🇳 Indian Number Lookup":
        user_steps[user_id] = "ask_phone"
        bot.reply_to(message, "👑 <b>CROWN TARGET LOCKED:</b>\n<i>Send 10-digit Phone Number.</i>", parse_mode="HTML")
        return
    elif txt == "🪪 Aadhaar Card Lookup":
        user_steps[user_id] = "ask_aadhar"
        bot.reply_to(message, "👑 <b>CROWN TARGET LOCKED:</b>\n<i>Send 12-digit Aadhaar Number.</i>", parse_mode="HTML")
        return
    elif txt == "🚗 Vehicle RC Info": 
        user_steps[user_id] = "ask_vehicle"
        bot.reply_to(message, "👑 <b>CROWN TARGET LOCKED:</b>\n<i>Send Vehicle Registration Number (e.g. MH01AB1234).</i>", parse_mode="HTML")
        return
    elif txt == "📧 Email Info Lookup":
        user_steps[user_id] = "ask_email"
        bot.reply_to(message, "👑 <i>Send Target Email Address.</i>", parse_mode="HTML")
        return
    elif txt == "🎮 BGMI Player Info":
        user_steps[user_id] = "ask_bgmi"
        bot.reply_to(message, "👑 <i>Send BGMI Player ID.</i>", parse_mode="HTML")
        return
    elif txt == "💎 My Credits":
        user = get_user(user_id)
        bot.reply_to(message, f"💎 <b>Your Credits:</b> {user['credits']}\n👑 <b>Powered by CROWN M4</b>", parse_mode="HTML")
        return

    current_step = user_steps.get(user_id)
    user_steps[user_id] = None 
    
    if current_step:
        # IDENTITY
        if current_step == "ask_phone":
            url = f"{BASE_URL_MAIN}/ph-tracker?token={TOKEN}&number={txt}"
        elif current_step == "ask_aadhar":
            url = f"{BASE_URL_MAIN}/aadhar-info?token={TOKEN}&id={txt}"
        elif current_step == "ask_vehicle":
            clean_rc = txt.replace(" ", "").upper()
            url = f"{BASE_URL_OSINT}/vehicle-info?key={OSINT_KEY}&vehicle={clean_rc}"
        elif current_step == "ask_pan":
            url = f"{BASE_URL_OSINT}/pan-info?key={OSINT_KEY}&pan={txt.upper()}"
        elif current_step == "ask_gst_dir":
            url = f"{BASE_URL_OSINT}/gst-direct?key={OSINT_KEY}&gstin={txt.upper()}"
        elif current_step == "ask_gst_src":
            url = f"{BASE_URL_OSINT}/gst-search?key={OSINT_KEY}&gstin={txt.upper()}"
        elif current_step == "ask_ifsc":
            url = f"{BASE_URL_OSINT}/ifsc-info?key={OSINT_KEY}&ifsc={txt.upper()}"
        elif current_step == "ask_imei":
            url = f"{BASE_URL_OSINT}/imei-info?key={OSINT_KEY}&imei_number={txt}"
            
        # INSTAGRAM
        elif current_step == "ig_best":
            url = f"{BASE_URL_OSINT}/instagram-best-v1?key={OSINT_KEY}&type=best&username={txt}"
        elif current_step == "ig_p_v1":
            url = f"{BASE_URL_OSINT}/instagram-profile-v1?key={OSINT_KEY}&type=profile&username={txt}"
        elif current_step == "ig_p_v2":
            url = f"{BASE_URL_OSINT}/instagram-profile-v2?key={OSINT_KEY}&type=profile&username={txt}"
        elif current_step == "ig_p_v3":
            url = f"{BASE_URL_OSINT}/instagram-profile-v3?key={OSINT_KEY}&type=profile&username={txt}"
        elif current_step == "ig_p_v32":
            url = f"{BASE_URL_OSINT}/instagram-profile-v3-v2?key={OSINT_KEY}&type=profile_v2&username={txt}"
        elif current_step == "ig_dl":
            url = f"{BASE_URL_OSINT}/instagram-download?key={OSINT_KEY}&type=download&url={txt}"
        elif current_step == "ig_dl_v1":
            url = f"{BASE_URL_OSINT}/instagram-downloads-v1?key={OSINT_KEY}&type=downloads&username={txt}"
        elif current_step == "ig_media":
            url = f"{BASE_URL_OSINT}/instagram-media-v1?key={OSINT_KEY}&type=media&username={txt}"
        elif current_step == "ig_post":
            url = f"{BASE_URL_OSINT}/instagram-posts-v2?key={OSINT_KEY}&type=posts&username={txt}"
        elif current_step == "ig_stat":
            url = f"{BASE_URL_OSINT}/instagram-stats-v1?key={OSINT_KEY}&type=stats&username={txt}"
        elif current_step == "ig_user":
            url = f"{BASE_URL_OSINT}/instagram-user-v1?key={OSINT_KEY}&type=user&username={txt}"

        # SNAPCHAT
        elif current_step == "sn_all":
            url = f"{BASE_URL_OSINT}/snapchat-all?key={OSINT_KEY}&action=all&username={txt}"
        elif current_step == "sn_high":
            url = f"{BASE_URL_OSINT}/snapchat-highlight?key={OSINT_KEY}&action=highlights&username={txt}"
        elif current_step == "sn_story":
            url = f"{BASE_URL_OSINT}/snapchat-story?key={OSINT_KEY}&action=stories&username={txt}"

        # NETWORK / IP
        elif current_step == "ip_v1":
            url = f"{BASE_URL_OSINT}/ip-v1?key={OSINT_KEY}&query={txt}"
        elif current_step == "ip_v2":
            url = f"{BASE_URL_OSINT}/ip-v2?key={OSINT_KEY}&ip={txt}"
        elif current_step == "ip_v3":
            url = f"{BASE_URL_OSINT}/ip-v3?key={OSINT_KEY}&ip={txt}"
        elif current_step == "ask_pin":
            url = f"{BASE_URL_OSINT}/pincode-info?key={OSINT_KEY}&pincode={txt}"
        elif current_step == "ask_country":
            url = f"{BASE_URL_OSINT}/country-info?key={OSINT_KEY}&name={txt}"

        # AI & MISC
        elif current_step == "ask_aigf":
            url = f"{BASE_URL_OSINT}/ai-gf?key={OSINT_KEY}&prompt={txt}"
        elif current_step == "ask_aiimg":
            url = f"{BASE_URL_OSINT}/image-generator?key={OSINT_KEY}&prompt={txt}"
        elif current_step == "ask_prompt":
            url = f"{BASE_URL_OSINT}/prompt-generator?key={OSINT_KEY}&url={txt}"
        elif current_step == "ask_email":
            url = f"{BASE_URL_OSINT}/email-info?key={OSINT_KEY}&mail={txt}"
        elif current_step == "ask_git":
            url = f"{BASE_URL_OSINT}/github-repos?key={OSINT_KEY}&q={txt}"
        elif current_step == "ask_bgmi":
            url = f"{BASE_URL_OSINT}/bgmi-info?key={OSINT_KEY}&user={txt}"

        execute_api_call(message, url)
        return

    # Auto-Detect Fallback
    bot.reply_to(message, "❌ <b>Select a specific tool from the menu first!</b>\n<i>Type /start to open the Menu.</i>", parse_mode="HTML")

# ================= RUN SERVER =================
if __name__ == "__main__":
    print("👑 CROWN M4 VIP OSINT BOT (ALL 30 APIs) IS ONLINE!")
    keep_alive()
    bot.infinity_polling()

