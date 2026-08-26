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
        <title>👑 CROWN BOT M4 Dashboard</title>
        <style>
            body { background-color: #0f172a; color: #f8fafc; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: rgba(30, 41, 59, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.1); padding: 40px; border-radius: 18px; text-align: center; max-width: 480px; width: 90%; }
            h1 { color: #38bdf8; font-size: 24px; margin-bottom: 10px; }
            .status { background: rgba(34, 197, 94, 0.15); color: #4ade80; padding: 8px 18px; border-radius: 20px; font-size: 14px; font-weight: 600; display: inline-block; margin-bottom: 20px; }
            .footer { margin-top: 20px; font-size: 12px; color: #94a3b8; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>👑 CROWN BOT M4</h1>
            <div class="status">🟢 Ultra System Online</div>
            <div class="footer">Powered by @team_lifexy ⚡</div>
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

def clean_terabox_url(raw_url):
    raw_url = raw_url.strip()
    if "surl=" in raw_url:
        surl = raw_url.split("surl=")[-1].split("&")[0]
        if not surl.startswith("1"):
            surl = "1" + surl
        return f"https://terabox.com/s/{surl}"
    return raw_url

# ================= REPLY KEYBOARD (GRID BOXES) =================
def get_reply_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📧 Email Info Lookup"),
        KeyboardButton("🚗 Vehicle Info & RC")
    )
    markup.add(
        KeyboardButton("📸 Instagram Hub"),
        KeyboardButton("👻 Snapchat Tools")
    )
    markup.add(
        KeyboardButton("📦 Terabox Player"),
        KeyboardButton("🌐 Network & IP Tools")
    )
    markup.add(
        KeyboardButton("💎 My Credits"),
        KeyboardButton("🔙 Main Menu")
    )
    return markup

# ================= INLINE MENUS =================
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🪪 Identity & Gov Services", callback_data="menu_identity"),
        InlineKeyboardButton("📸 Instagram Toolkit", callback_data="menu_instagram")
    )
    markup.add(
        InlineKeyboardButton("👻 Snapchat Toolkit", callback_data="menu_snapchat"),
        InlineKeyboardButton("📦 Terabox Player 🎬", callback_data="menu_terabox")
    )
    markup.add(
        InlineKeyboardButton("🌐 Web & IP Network", callback_data="menu_geo"),
        InlineKeyboardButton("🤖 AI & Utilities", callback_data="menu_ai")
    )
    markup.add(InlineKeyboardButton("💎 My Profile (VIP)", callback_data="profile"))
    return markup

def identity_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📧 Email Info Lookup", callback_data="ask_email_info"),
        InlineKeyboardButton("🚗 Vehicle Full Info & RC", callback_data="ask_vehicle")
    )
    markup.add(
        InlineKeyboardButton("📱 Phone Number Info", callback_data="ask_phone"),
        InlineKeyboardButton("📞 Truecaller Search", callback_data="ask_truecaller")
    )
    markup.add(
        InlineKeyboardButton("🪪 Aadhaar Info", callback_data="ask_aadhar"),
        InlineKeyboardButton("📇 PAN Card Details", callback_data="ask_pan")
    )
    markup.add(
        InlineKeyboardButton("🏢 GST Search", callback_data="ask_gst"),
        InlineKeyboardButton("🏦 Bank IFSC Code", callback_data="ask_ifsc")
    )
    markup.add(
        InlineKeyboardButton("📱 IMEI Number Check", callback_data="ask_imei"),
        InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main")
    )
    return markup

def instagram_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("👤 Profile Search (Best)", callback_data="ask_ig_best"),
        InlineKeyboardButton("⬇️ Reel / Post Downloader", callback_data="ask_ig_dl")
    )
    markup.add(
        InlineKeyboardButton("📸 Media & Photos", callback_data="ask_ig_media"),
        InlineKeyboardButton("📝 Recent Posts", callback_data="ask_ig_posts")
    )
    markup.add(
        InlineKeyboardButton("📂 Full Data Download", callback_data="ask_ig_downloads"),
        InlineKeyboardButton("📊 Account Stats", callback_data="ask_ig_stats")
    )
    markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main"))
    return markup

def snapchat_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("👻 Snapchat Profile & All Data", callback_data="ask_snap_all"),
        InlineKeyboardButton("🌟 Snapchat Highlights", callback_data="ask_snap_high")
    )
    markup.add(
        InlineKeyboardButton("🎞️ Snapchat Stories & Videos", callback_data="ask_snap_story"),
        InlineKeyboardButton("📥 Snapchat Video Encoding Hub", callback_data="ask_snap_dl")
    )
    markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main"))
    return markup

def terabox_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🎬 Direct Video Stream", callback_data="ask_tb_s1"),
        InlineKeyboardButton("📥 Fast Video Download", callback_data="ask_tb_v2")
    )
    markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main"))
    return markup

def geo_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🌐 Website Scraper", callback_data="ask_web"),
        InlineKeyboardButton("📍 IP Address Info", callback_data="ask_ip1")
    )
    markup.add(
        InlineKeyboardButton("📮 Pincode Info", callback_data="ask_pin"),
        InlineKeyboardButton("🇮🇳 Country Info", callback_data="ask_country")
    )
    markup.add(
        InlineKeyboardButton("🌤️ Weather Information", callback_data="ask_weather"),
        InlineKeyboardButton("💻 GitHub Search", callback_data="ask_github")
    )
    markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main"))
    return markup

def ai_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💖 AI Chat Assistant", callback_data="ask_aigf"),
        InlineKeyboardButton("🎨 AI Image Generator", callback_data="ask_aiimg")
    )
    markup.add(
        InlineKeyboardButton("✨ Prompt Generator", callback_data="ask_promptgen"),
        InlineKeyboardButton("🎮 BGMI Player Info", callback_data="ask_bgmi")
    )
    markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main"))
    return markup

# ================= START COMMAND =================
@bot.message_handler(commands=["start"])
def start(message):
    get_user(message.from_user.id)
    user_steps[message.from_user.id] = None 

    welcome_text = (
        f"<b>Welcome to Crown Bot M4!</b>\n\n"
        f"<i>Select any option below or use the buttons to proceed:</i>\n"
        f"──────────────────────\n"
        f"⚡ <b>Research & Support:</b> @team_lifexy"
    )

    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode="HTML")
    bot.send_message(message.chat.id, "👇 <b>Quick Control Panel:</b>", reply_markup=get_reply_keyboard(), parse_mode="HTML")

# ================= CALLBACK HANDLER =================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    
    if call.data == "menu_main":
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=main_menu())
    elif call.data == "menu_identity":
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=identity_menu())
    elif call.data == "menu_instagram":
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=instagram_menu())
    elif call.data == "menu_snapchat":
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=snapchat_menu())
    elif call.data == "menu_terabox":
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=terabox_menu())
    elif call.data == "menu_geo":
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=geo_menu())
    elif call.data == "menu_ai":
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=ai_menu())
        
    elif call.data == "profile":
        user = get_user(user_id)
        credits_display = "♾️ <b>Unlimited (VIP)</b>" if user_id == ADMIN_ID else f"<b>{user['credits']}</b>"
        info_text = (
            f"👑 <b><u>Crown Profile M4</u></b> 👑\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>User:</b> <i>{call.from_user.first_name}</i>\n"
            f"💎 <b>Credits:</b> {credits_display}\n"
            f"🔍 <b>Total Lookups:</b> <b>{user['lookups']}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⚡ <b>Developer:</b> @team_lifexy"
        )
        bot.send_message(chat_id, info_text, parse_mode="HTML")

    else:
        prompts = {
            "ask_email_info": "📧 <b>Enter Email Address:</b> (e.g., test@gmail.com)",
            "ask_vehicle": "🚗 <b>Enter Vehicle Number:</b> (e.g., MH12DE1433)",
            "ask_phone": "📱 <b>Enter 10-digit Phone Number:</b>",
            "ask_truecaller": "📞 <b>Enter Phone Number for Truecaller:</b>",
            "ask_aadhar": "🪪 <b>Enter 12-digit Aadhaar Number:</b>",
            "ask_pan": "📇 <b>Enter 10-character PAN Card Number:</b>",
            "ask_gst": "🏢 <b>Enter 15-character GSTIN:</b>",
            "ask_ifsc": "🏦 <b>Enter Bank IFSC Code:</b>",
            "ask_imei": "📱 <b>Enter 15-digit IMEI Number:</b>",
            
            # Instagram
            "ask_ig_best": "🏆 <b>Enter Instagram Username:</b>",
            "ask_ig_dl": "⬇️ <b>Send Instagram Reel or Post Link:</b>",
            "ask_ig_media": "🎬 <b>Enter Instagram Username (Media Check):</b>",
            "ask_ig_posts": "📝 <b>Enter Instagram Username for Posts:</b>",
            "ask_ig_downloads": "📂 <b>Enter Instagram Username for Downloads:</b>",
            "ask_ig_stats": "📊 <b>Enter Instagram Username for Stats:</b>",
            
            # Snapchat
            "ask_snap_all": "👻 <b>Enter Snapchat Username:</b>",
            "ask_snap_high": "🌟 <b>Enter Snapchat Username for Highlights:</b>",
            "ask_snap_story": "🎞️ <b>Enter Snapchat Username for Stories/Videos:</b>",
            "ask_snap_dl": "📥 <b>Enter Snapchat Video URL or Username for Media Encoding:</b>",
            
            # Terabox
            "ask_tb_s1": "🎬 <b>Send Terabox Video Link:</b>",
            "ask_tb_v2": "📥 <b>Send Terabox Link for Download:</b>",
            
            # Geo & Utilities
            "ask_web": "🌐 <b>Enter Full Website URL:</b>",
            "ask_ip1": "🌐 <b>Enter IP Address:</b>",
            "ask_pin": "📍 <b>Enter 6-digit Pincode:</b>",
            "ask_country": "🇮🇳 <b>Enter Country Name (e.g., india):</b>",
            "ask_weather": "🌤️ <b>Enter City Name:</b>",
            "ask_github": "💻 <b>Enter GitHub Username or Query:</b>",
            
            # AI & Games
            "ask_aigf": "💖 <b>Type your query for AI Chat:</b>",
            "ask_aiimg": "🎨 <b>Enter prompt to generate image:</b>",
            "ask_promptgen": "✨ <b>Send Image URL for Prompt Generation:</b>",
            "ask_bgmi": "🎮 <b>Enter BGMI Character ID:</b>"
        }
        
        if call.data in prompts:
            user_steps[user_id] = call.data
            bot.send_message(chat_id, f"👑 <b>Input Required:</b>\n{prompts[call.data]}", parse_mode="HTML")

    bot.answer_callback_query(call.id)

# ================= TERABOX ENGINE =================
def execute_terabox_call(message, search_val):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user_id != ADMIN_ID and user["credits"] < 1:
        bot.reply_to(message, "❌ <i>Insufficient credits!</i>", parse_mode="HTML")
        return

    wait_msg = bot.reply_to(message, "🎬🍿 <b><i>Loading video stream, please wait...</i></b>", parse_mode="HTML")
    normalized_url = clean_terabox_url(search_val)
    
    endpoints = [
        (f"{BASE_URL_OSINT}/terabox-stream-v2", "video_streamv2"),
        (f"{BASE_URL_OSINT}/terabox-stream-v3", "video_streamv3"),
        (f"{BASE_URL_OSINT}/terabox-stream", "video_stream")
    ]

    stream_link = None
    for ep, type_param in endpoints:
        try:
            r = requests.get(ep, params={"key": OSINT_KEY, "type": type_param, "url": normalized_url}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, dict):
                    stream_link = data.get("stream_url") or data.get("download_url") or data.get("url") or data.get("link")
                if stream_link:
                    break
        except Exception:
            continue

    if stream_link:
        if user_id != ADMIN_ID:
            user["credits"] -= 1
        user["lookups"] += 1
        global total_lookups
        total_lookups += 1
        save_data()

        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("▶️ Watch Video Now", url=stream_link),
            InlineKeyboardButton("📥 Download File Direct", url=stream_link)
        )
        
        caption = (
            f"👑 <b>Crown Terabox Player M4</b> 👑\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎬 <b>Status:</b> <i>Video stream is ready!</i>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👇 <b>Click the buttons below to play/download:</b>"
        )
        bot.edit_message_text(caption, message.chat.id, wait_msg.message_id, reply_markup=markup, parse_mode="HTML")
        auto_delete(message.chat.id, wait_msg.message_id)
    else:
        bot.edit_message_text("❌ <b>Unable to load video stream.</b> Please try another link.", message.chat.id, wait_msg.message_id, parse_mode="HTML")

# ================= STANDARD API ENGINE WITH MEDIA BUTTON DETECTOR =================
def execute_api_call(message, endpoint_url, query_label, search_val, params=None):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user_id != ADMIN_ID and user["credits"] < 1:
        bot.reply_to(message, "❌ <i>Credits exhausted. Contact @team_lifexy</i>", parse_mode="HTML")
        return

    wait_msg = bot.reply_to(message, "👑📡 <b><i>Fetching data from server...</i></b>", parse_mode="HTML")

    try:
        r = requests.get(endpoint_url, params=params, timeout=25)
        
        if r.status_code == 404:
            bot.edit_message_text("⚠️ <b>Error (404):</b> Data not found.", message.chat.id, wait_msg.message_id, parse_mode="HTML")
            return
            
        try:
            api_response = r.json()
        except Exception:
            api_response = {"response": r.text}

        if user_id != ADMIN_ID:
            user["credits"] -= 1

        user["lookups"] += 1
        global total_lookups
        total_lookups += 1
        save_data()

        # Direct Video / Media Detector for Snapchat & Instagram
        media_link = None
        if isinstance(api_response, dict):
            media_link = (
                api_response.get("url") or 
                api_response.get("download_url") or 
                api_response.get("video_url") or 
                api_response.get("media_url") or 
                api_response.get("stream_url")
            )
            if not media_link and isinstance(api_response.get("data"), dict):
                media_link = (
                    api_response["data"].get("url") or 
                    api_response["data"].get("download_url") or 
                    api_response["data"].get("video_url") or
                    api_response["data"].get("media_url")
                )
            elif not media_link and isinstance(api_response.get("data"), list) and len(api_response["data"]) > 0:
                item = api_response["data"][0]
                if isinstance(item, dict):
                    media_link = item.get("url") or item.get("download_url") or item.get("video_url") or item.get("media_url")

        result_json = json.dumps(api_response, indent=2, ensure_ascii=False)
        
        # Scrub unauthorized names
        scrub_patterns = [r"(?i)onlyh4ckerzon", r"(?i)onlyhackerzon", r"(?i)rohit", r"(?i)@froxtdevil", r"(?i)optimusprime"]
        for pattern in scrub_patterns:
            result_json = re.sub(pattern, "Crown 👑", result_json)

        if len(result_json) > 3500:
            result_json = result_json[:3500] + "\n... [TRUNCATED]"

        text = f"""
👑 <b>Crown Intel Result (CROWN M4)</b> 👑
━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 <b>Service:</b> <i>{query_label}</i>
📌 <b>Input:</b> <code>{search_val}</code>
━━━━━━━━━━━━━━━━━━━━━━━━━━
<b><u>Data Output:</u></b>
<pre>{result_json}</pre>
━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ <b>Power: @team_lifexy</b>
"""
        markup = None
        if media_link:
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("▶️ View Video / Media", url=media_link),
                InlineKeyboardButton("📥 Download File", url=media_link)
            )

        bot.edit_message_text(text, message.chat.id, wait_msg.message_id, reply_markup=markup, parse_mode="HTML")
        auto_delete(message.chat.id, wait_msg.message_id)

    except Exception:
        bot.edit_message_text("❌ <b>System Error:</b> Request timeout or API unreachable.", message.chat.id, wait_msg.message_id, parse_mode="HTML")

# ================= SMART QUERY ROUTER =================
@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def handle_queries(message):
    txt = message.text.strip()
    user_id = message.from_user.id

    # 0. Quick Buttons Handlers
    if txt == "📧 Email Info Lookup":
        user_steps[user_id] = "ask_email_info"
        bot.reply_to(message, "👑 <b>Enter Email Address:</b>\n<i>(e.g., test@gmail.com)</i>", parse_mode="HTML")
        return
    elif txt == "🚗 Vehicle Info & RC":
        user_steps[user_id] = "ask_vehicle"
        bot.reply_to(message, "👑 <b>Enter Vehicle Number:</b>\n<i>(e.g., MH12DE1433)</i>", parse_mode="HTML")
        return
    elif txt == "📦 Terabox Player":
        bot.reply_to(message, "👑 <b>Terabox Menu:</b>", reply_markup=terabox_menu(), parse_mode="HTML")
        return
    elif txt == "📸 Instagram Hub":
        bot.reply_to(message, "👑 <b>Instagram Menu:</b>", reply_markup=instagram_menu(), parse_mode="HTML")
        return
    elif txt == "👻 Snapchat Tools":
        bot.reply_to(message, "👑 <b>Snapchat Menu:</b>", reply_markup=snapchat_menu(), parse_mode="HTML")
        return
    elif txt == "🌐 Network & IP Tools":
        bot.reply_to(message, "👑 <b>Network Menu:</b>", reply_markup=geo_menu(), parse_mode="HTML")
        return
    elif txt == "💎 My Credits":
        user = get_user(user_id)
        bot.reply_to(message, f"👑 <b>Your Credits:</b> {user['credits']}\n<b>Support:</b> @team_lifexy", parse_mode="HTML")
        return
    elif txt == "🔙 Main Menu":
        bot.reply_to(message, "👑 <b>Main Menu:</b>", reply_markup=main_menu(), parse_mode="HTML")
        return

    current_step = user_steps.get(user_id)
    user_steps[user_id] = None 

    tb_domains = ["terabox", "1024terabox", "teraboxapp", "freeterabox", "mirrobox", "neptunebox", "4funbox"]
    is_terabox_link = any(domain in txt.lower() for domain in tb_domains)

    # 1. Step Routing
    if current_step:
        # Identity & Vehicle
        if current_step == "ask_email_info":
            url = f"{BASE_URL_OSINT}/email-info"
            params = {"key": OSINT_KEY, "mail": txt}
            execute_api_call(message, url, "EMAIL INFO LOOKUP", txt, params=params)
            return
        elif current_step == "ask_vehicle":
            url = f"{BASE_URL_OSINT}/vehicle-v1"
            params = {"key": OSINT_KEY, "type": "v1", "rc": txt.upper()}
            execute_api_call(message, url, "VEHICLE FULL INFO & RC", txt.upper(), params=params)
            return
        elif current_step == "ask_phone":
            url = f"{BASE_URL_MAIN}/ph-tracker"
            params = {"token": TOKEN, "number": txt}
            execute_api_call(message, url, "PHONE RECORD", txt, params=params)
            return
        elif current_step == "ask_truecaller":
            url = f"{BASE_URL_OSINT}/truecaller-info"
            params = {"key": OSINT_KEY, "number": txt}
            execute_api_call(message, url, "TRUECALLER INFO", txt, params=params)
            return
        elif current_step == "ask_aadhar":
            url = f"{BASE_URL_MAIN}/aadhar-info"
            params = {"token": TOKEN, "id": txt}
            execute_api_call(message, url, "AADHAAR INFO", txt, params=params)
            return
        elif current_step == "ask_pan":
            url = f"{BASE_URL_OSINT}/pan-info"
            params = {"key": OSINT_KEY, "pan": txt.upper()}
            execute_api_call(message, url, "PAN CARD INFO", txt.upper(), params=params)
            return
        elif current_step == "ask_gst":
            url = f"{BASE_URL_OSINT}/gst-search"
            params = {"key": OSINT_KEY, "gstin": txt.upper()}
            execute_api_call(message, url, "GST SEARCH", txt.upper(), params=params)
            return
        elif current_step == "ask_ifsc":
            url = f"{BASE_URL_OSINT}/ifsc-info"
            params = {"key": OSINT_KEY, "ifsc": txt.upper()}
            execute_api_call(message, url, "BANK IFSC SEARCH", txt.upper(), params=params)
            return
        elif current_step == "ask_imei":
            url = f"{BASE_URL_OSINT}/imei-info"
            params = {"key": OSINT_KEY, "imei_number": txt}
            execute_api_call(message, url, "IMEI DETAILS", txt, params=params)
            return

        # Instagram
        elif current_step == "ask_ig_best":
            url = f"{BASE_URL_OSINT}/instagram-best-v1"
            params = {"key": OSINT_KEY, "type": "best", "username": txt}
            execute_api_call(message, url, "INSTAGRAM PROFILE SEARCH", txt, params=params)
            return
        elif current_step == "ask_ig_dl":
            url = f"{BASE_URL_OSINT}/instagram-download"
            params = {"key": OSINT_KEY, "type": "download", "url": txt}
            execute_api_call(message, url, "INSTAGRAM REEL/POST DOWNLOAD", txt, params=params)
            return
        elif current_step == "ask_ig_media":
            url = f"{BASE_URL_OSINT}/instagram-media-v1"
            params = {"key": OSINT_KEY, "type": "media", "username": txt}
            execute_api_call(message, url, "INSTAGRAM MEDIA LOOKUP", txt, params=params)
            return
        elif current_step == "ask_ig_posts":
            url = f"{BASE_URL_OSINT}/instagram-posts-v2"
            params = {"key": OSINT_KEY, "type": "posts", "username": txt}
            execute_api_call(message, url, "INSTAGRAM POSTS LOOKUP", txt, params=params)
            return
        elif current_step == "ask_ig_downloads":
            url = f"{BASE_URL_OSINT}/instagram-downloads-v1"
            params = {"key": OSINT_KEY, "type": "downloads", "username": txt}
            execute_api_call(message, url, "INSTAGRAM FULL DOWNLOADS", txt, params=params)
            return
        elif current_step == "ask_ig_stats":
            url = f"{BASE_URL_OSINT}/instagram-stats-v1"
            params = {"key": OSINT_KEY, "type": "stats", "username": txt}
            execute_api_call(message, url, "INSTAGRAM ACCOUNT STATS", txt, params=params)
            return

        # Snapchat
        elif current_step == "ask_snap_all":
            url = f"{BASE_URL_OSINT}/snapchat-all"
            params = {"key": OSINT_KEY, "action": "all", "username": txt}
            execute_api_call(message, url, "SNAPCHAT FULL DATA", txt, params=params)
            return
        elif current_step == "ask_snap_high":
            url = f"{BASE_URL_OSINT}/snapchat-highlight"
            params = {"key": OSINT_KEY, "action": "highlights", "username": txt}
            execute_api_call(message, url, "SNAPCHAT HIGHLIGHTS", txt, params=params)
            return
        elif current_step == "ask_snap_story":
            url = f"{BASE_URL_OSINT}/snapchat-story"
            params = {"key": OSINT_KEY, "action": "stories", "username": txt}
            execute_api_call(message, url, "SNAPCHAT STORY & VIDEO", txt, params=params)
            return
        elif current_step == "ask_snap_dl":
            url = f"{BASE_URL_OSINT}/snapchat-download"
            params = {"key": OSINT_KEY, "action": "download", "query": txt}
            execute_api_call(message, url, "SNAPCHAT VIDEO ENCODING & MEDIA", txt, params=params)
            return

        # Terabox & Network
        elif current_step in ["ask_tb_s1", "ask_tb_v2"]:
            execute_terabox_call(message, txt)
            return
        elif current_step == "ask_web":
            url = f"{BASE_URL_OSINT}/website-source"
            params = {"key": OSINT_KEY, "url": txt}
            execute_api_call(message, url, "WEBSITE SCRAPER", txt, params=params)
            return
        elif current_step == "ask_ip1":
            url = f"{BASE_URL_OSINT}/ip-v1"
            params = {"key": OSINT_KEY, "query": txt}
            execute_api_call(message, url, "IP INFO LOOKUP", txt, params=params)
            return
        elif current_step == "ask_pin":
            url = f"{BASE_URL_OSINT}/pincode-info"
            params = {"key": OSINT_KEY, "pincode": txt}
            execute_api_call(message, url, "PINCODE INFO", txt, params=params)
            return
        elif current_step == "ask_country":
            url = f"{BASE_URL_OSINT}/country-info"
            params = {"key": OSINT_KEY, "name": txt}
            execute_api_call(message, url, "COUNTRY INFO", txt, params=params)
            return
        elif current_step == "ask_weather":
            url = f"{BASE_URL_OSINT}/weather-info"
            params = {"key": OSINT_KEY, "city": txt}
            execute_api_call(message, url, "WEATHER INFO", txt, params=params)
            return
        elif current_step == "ask_github":
            url = f"{BASE_URL_OSINT}/github-repos"
            params = {"key": OSINT_KEY, "q": txt}
            execute_api_call(message, url, "GITHUB REPOS SEARCH", txt, params=params)
            return

        # AI & BGMI
        elif current_step == "ask_aigf":
            url = f"{BASE_URL_OSINT}/ai-gf"
            params = {"key": OSINT_KEY, "prompt": txt}
            execute_api_call(message, url, "AI CHAT ASSISTANT", txt, params=params)
            return
        elif current_step == "ask_aiimg":
            url = f"{BASE_URL_OSINT}/image-generator"
            params = {"key": OSINT_KEY, "prompt": txt}
            execute_api_call(message, url, "AI IMAGE GENERATOR", txt, params=params)
            return
        elif current_step == "ask_promptgen":
            url = f"{BASE_URL_OSINT}/prompt-generator"
            params = {"key": OSINT_KEY, "url": txt}
            execute_api_call(message, url, "PROMPT GENERATOR", txt, params=params)
            return
        elif current_step == "ask_bgmi":
            url = f"{BASE_URL_OSINT}/bgmi-info"
            params = {"key": OSINT_KEY, "user": txt}
            execute_api_call(message, url, "BGMI PLAYER INFO", txt, params=params)
            return

    # 2. Smart Auto-Detect
    if is_terabox_link:
        execute_terabox_call(message, txt)
    elif "@" in txt and "." in txt and not txt.startswith("http"):
        url = f"{BASE_URL_OSINT}/email-info"
        params = {"key": OSINT_KEY, "mail": txt}
        execute_api_call(message, url, "EMAIL INFO LOOKUP", txt, params=params)
    elif txt.startswith("http://") or txt.startswith("https://"):
        if "instagram.com" in txt.lower():
            url = f"{BASE_URL_OSINT}/instagram-download"
            params = {"key": OSINT_KEY, "type": "download", "url": txt}
            execute_api_call(message, url, "INSTAGRAM DOWNLOAD", txt, params=params)
        else:
            url = f"{BASE_URL_OSINT}/website-source"
            params = {"key": OSINT_KEY, "url": txt}
            execute_api_call(message, url, "WEBSITE SCRAPER", txt, params=params)
    elif txt.isdigit() and len(txt) == 10:
        url = f"{BASE_URL_MAIN}/ph-tracker"
        params = {"token": TOKEN, "number": txt}
        execute_api_call(message, url, "PHONE RECORD", txt, params=params)
    elif re.match(r"^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$", txt.upper()):
        url = f"{BASE_URL_OSINT}/vehicle-v1"
        params = {"key": OSINT_KEY, "type": "v1", "rc": txt.upper()}
        execute_api_call(message, url, "VEHICLE FULL INFO & RC", txt.upper(), params=params)
    else:
        msg = bot.reply_to(message, "❌ <b>Invalid Input!</b>\n<i>Please press /start to open the menu and select an option.</i>", parse_mode="HTML")
        auto_delete(msg.chat.id, msg.message_id)

# ================= RUN SERVER =================
if __name__ == "__main__":
    print("👑 CROWN BOT M4 IS ONLINE!")
    keep_alive()
    bot.infinity_polling()
