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

# ================= FLASK SERVER FOR 24/7 HOSTING =================
app = Flask('')

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>👑 CROWN BOT M4</title>
        <style>
            body { background: #0b0f19; color: #38bdf8; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: #1e293b; padding: 40px; border-radius: 16px; text-align: center; border: 1px solid #334155; }
            h1 { font-size: 26px; margin-bottom: 8px; }
            p { color: #94a3b8; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>👑 CROWN BOT M4 ULTRA</h1>
            <p>🟢 System Status: Fully Operational</p>
        </div>
    </body>
    </html>
    """

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

# ================= CONFIGURATION & CONSTANTS =================
BOT_TOKEN = "8887168683:AAFU5xQN389gI1WSOhEom41FY0I4-fRy3fs"
ADMIN_ID = 8407090614

TOKEN = "xpol_Demo_combo_a811c2fb"
OSINT_KEY = "demo"
BASE_URL_MAIN = "https://xpolitesupgrade-api.darrify-api.workers.dev/api"
BASE_URL_OSINT = "https://osint-api-delta.vercel.app/api"

DATA_FILE = "users_data.json"
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
total_lookups = 0
user_steps = {}

# ================= DATA ENGINE =================
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

# Extract direct media URLs recursively from deep JSON responses
def extract_media_url(data):
    if isinstance(data, str):
        if data.startswith("http") and any(ext in data.lower() for ext in [".mp4", ".mov", "m3u8", ".jpg", ".jpeg", ".png", "video", "stream", "download", "terabox"]):
            return data
        return None

    if isinstance(data, dict):
        priority_keys = ["video_url", "stream_url", "download_url", "play_url", "media_url", "display_url", "image_url", "direct_link", "url", "link"]
        for key in priority_keys:
            val = data.get(key)
            if isinstance(val, str) and val.startswith("http"):
                return val
        for key, val in data.items():
            res = extract_media_url(val)
            if res:
                return res

    if isinstance(data, list):
        for item in data:
            res = extract_media_url(item)
            if res:
                return res
    return None

def clean_terabox_url(raw_url):
    raw_url = raw_url.strip()
    if "surl=" in raw_url:
        surl = raw_url.split("surl=")[-1].split("&")[0]
        if not surl.startswith("1"):
            surl = "1" + surl
        return f"https://terabox.com/s/{surl}"
    return raw_url

# ================= NAVIGATION KEYBOARDS =================
def get_reply_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("👻 Snapchat Video Hub"),
        KeyboardButton("📦 Terabox Direct Downloader")
    )
    markup.add(
        KeyboardButton("📸 Instagram Hub"),
        KeyboardButton("🚗 Vehicle RC & Info")
    )
    markup.add(
        KeyboardButton("📧 Email Intelligence"),
        KeyboardButton("🌐 IP & Network Tools")
    )
    markup.add(
        KeyboardButton("💎 My VIP Account"),
        KeyboardButton("🔙 Main Menu")
    )
    return markup

def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("👻 Snapchat Video Hub", callback_data="menu_snapchat"),
        InlineKeyboardButton("📦 Terabox Video Streamer", callback_data="menu_terabox")
    )
    markup.add(
        InlineKeyboardButton("📸 Instagram Downloader", callback_data="menu_instagram"),
        InlineKeyboardButton("🪪 Identity & Vehicle Info", callback_data="menu_identity")
    )
    markup.add(
        InlineKeyboardButton("🌐 Network & Web Tools", callback_data="menu_geo"),
        InlineKeyboardButton("🤖 AI Tools & Utilities", callback_data="menu_ai")
    )
    markup.add(InlineKeyboardButton("👑 VIP User Profile", callback_data="profile"))
    return markup

def snapchat_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📥 Snapchat Video & Media Downloader", callback_data="ask_snap_dl"),
        InlineKeyboardButton("🎞️ Snapchat Stories & Videos", callback_data="ask_snap_story"),
        InlineKeyboardButton("🌟 Snapchat Highlights", callback_data="ask_snap_high"),
        InlineKeyboardButton("👻 Full Snapchat Profile Info", callback_data="ask_snap_all"),
        InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main")
    )
    return markup

def terabox_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🎬 Direct Chrome Video Stream", callback_data="ask_tb_s1"),
        InlineKeyboardButton("📥 High-Speed Video Download Link", callback_data="ask_tb_v2"),
        InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main")
    )
    return markup

def instagram_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("⬇️ Reel / Post Video Download", callback_data="ask_ig_dl"),
        InlineKeyboardButton("👤 Profile Search", callback_data="ask_ig_best")
    )
    markup.add(
        InlineKeyboardButton("📸 Media Files", callback_data="ask_ig_media"),
        InlineKeyboardButton("📝 Recent Posts", callback_data="ask_ig_posts")
    )
    markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main"))
    return markup

def identity_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🚗 Vehicle RC & Details", callback_data="ask_vehicle"),
        InlineKeyboardButton("📧 Email Intelligence", callback_data="ask_email_info")
    )
    markup.add(
        InlineKeyboardButton("📱 Phone Lookup", callback_data="ask_phone"),
        InlineKeyboardButton("📞 Truecaller Search", callback_data="ask_truecaller")
    )
    markup.add(
        InlineKeyboardButton("📇 PAN Card Details", callback_data="ask_pan"),
        InlineKeyboardButton("🏢 GST Details", callback_data="ask_gst")
    )
    markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main"))
    return markup

def geo_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🌐 Website Scraper", callback_data="ask_web"),
        InlineKeyboardButton("📍 IP Info Lookup", callback_data="ask_ip1")
    )
    markup.add(
        InlineKeyboardButton("🌤️ Weather Search", callback_data="ask_weather"),
        InlineKeyboardButton("💻 GitHub Search", callback_data="ask_github")
    )
    markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main"))
    return markup

def ai_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💖 AI Chatbot", callback_data="ask_aigf"),
        InlineKeyboardButton("🎨 AI Image Generator", callback_data="ask_aiimg")
    )
    markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main"))
    return markup

# ================= START COMMAND =================
@bot.message_handler(commands=["start"])
def start(message):
    get_user(message.from_user.id)
    user_steps[message.from_user.id] = None 

    welcome_text = (
        f"👑 <b>Welcome to Crown Bot M4 Ultra!</b> 👑\n\n"
        f"<i>Your ultimate high-performance downloader & OSINT utility suite.</i>\n"
        f"──────────────────────────────\n"
        f"⚡ <b>Official Developer:</b> @team_lifexy\n"
        f"✨ <i>Select an option below to start downloading videos or querying data.</i>"
    )

    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode="HTML")
    bot.send_message(message.chat.id, "👇 <b>Quick Control Panel:</b>", reply_markup=get_reply_keyboard(), parse_mode="HTML")

# ================= CALLBACK ROUTER =================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    
    if call.data == "menu_main":
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=main_menu())
    elif call.data == "menu_snapchat":
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=snapchat_menu())
    elif call.data == "menu_terabox":
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=terabox_menu())
    elif call.data == "menu_instagram":
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=instagram_menu())
    elif call.data == "menu_identity":
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=identity_menu())
    elif call.data == "menu_geo":
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=geo_menu())
    elif call.data == "menu_ai":
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=ai_menu())
        
    elif call.data == "profile":
        user = get_user(user_id)
        credits_disp = "♾️ <b>Unlimited (VIP)</b>" if user_id == ADMIN_ID else f"<b>{user['credits']}</b>"
        info_text = (
            f"👑 <b><u>Crown User Profile M4</u></b> 👑\n"
            f"──────────────────────────────\n"
            f"👤 <b>Account Name:</b> <i>{call.from_user.first_name}</i>\n"
            f"💎 <b>Available Credits:</b> {credits_disp}\n"
            f"🔍 <b>Total Queries Fulfillments:</b> <b>{user['lookups']}</b>\n"
            f"──────────────────────────────\n"
            f"⚡ <b>Developer:</b> @team_lifexy"
        )
        bot.send_message(chat_id, info_text, parse_mode="HTML")

    else:
        prompts = {
            "ask_snap_dl": "👻 <b>Send Snapchat Video Link or Username for Media Extraction:</b>",
            "ask_snap_story": "🎞️ <b>Enter Snapchat Username for Stories:</b>",
            "ask_snap_high": "🌟 <b>Enter Snapchat Username for Highlights:</b>",
            "ask_snap_all": "👻 <b>Enter Snapchat Username:</b>",
            
            "ask_tb_s1": "🎬 <b>Send Terabox Video Link for Stream:</b>",
            "ask_tb_v2": "📥 <b>Send Terabox Link for High-Speed Download:</b>",
            
            "ask_ig_dl": "⬇️ <b>Send Instagram Reel or Video Link:</b>\n<i>(e.g., https://www.instagram.com/reel/...)</i>",
            "ask_ig_best": "👤 <b>Enter Instagram Username:</b>",
            "ask_ig_media": "📸 <b>Enter Instagram Username for Media:</b>",
            "ask_ig_posts": "📝 <b>Enter Instagram Username for Posts:</b>",
            
            "ask_vehicle": "🚗 <b>Enter Vehicle Number (e.g., MH12DE1433):</b>",
            "ask_email_info": "📧 <b>Enter Target Email Address:</b>",
            "ask_phone": "📱 <b>Enter 10-Digit Mobile Number:</b>",
            "ask_truecaller": "📞 <b>Enter Mobile Number for Truecaller:</b>",
            "ask_pan": "📇 <b>Enter 10-Character PAN Number:</b>",
            "ask_gst": "🏢 <b>Enter GSTIN:</b>",
            
            "ask_web": "🌐 <b>Enter Full Website URL:</b>",
            "ask_ip1": "📍 <b>Enter IP Address:</b>",
            "ask_weather": "🌤️ <b>Enter City Name:</b>",
            "ask_github": "💻 <b>Enter GitHub Username / Term:</b>",
            
            "ask_aigf": "💖 <b>Enter prompt for AI Chatbot:</b>",
            "ask_aiimg": "🎨 <b>Enter image prompt:</b>"
        }
        
        if call.data in prompts:
            user_steps[user_id] = call.data
            bot.send_message(chat_id, f"👑 <b>Input Required:</b>\n{prompts[call.data]}", parse_mode="HTML")

    bot.answer_callback_query(call.id)

# ================= ENHANCED TERABOX HANDLER =================
def execute_terabox_call(message, search_val):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user_id != ADMIN_ID and user["credits"] < 1:
        bot.reply_to(message, "❌ <i>Insufficient credits! Contact @team_lifexy</i>", parse_mode="HTML")
        return

    wait_msg = bot.reply_to(message, "🎬🍿 <b><i>Processing Terabox video stream link...</i></b>", parse_mode="HTML")
    clean_url = clean_terabox_url(search_val)
    
    endpoints = [
        (f"{BASE_URL_OSINT}/terabox-stream-v2", "video_streamv2"),
        (f"{BASE_URL_OSINT}/terabox-stream-v3", "video_streamv3"),
        (f"{BASE_URL_OSINT}/terabox-stream", "video_stream")
    ]

    direct_video_url = None
    for ep, type_param in endpoints:
        try:
            r = requests.get(ep, params={"key": OSINT_KEY, "type": type_param, "url": clean_url}, timeout=12)
            if r.status_code == 200:
                resp_json = r.json()
                direct_video_url = extract_media_url(resp_json)
                if direct_video_url:
                    break
        except Exception:
            continue

    if direct_video_url:
        if user_id != ADMIN_ID:
            user["credits"] -= 1
        user["lookups"] += 1
        global total_lookups
        total_lookups += 1
        save_data()

        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("▶️ Open & Stream Video in Chrome", url=direct_video_url),
            InlineKeyboardButton("📥 Direct Download Video File", url=direct_video_url)
        )
        
        caption = (
            f"👑 <b>Crown Terabox Media Player M4</b> 👑\n"
            f"──────────────────────────────\n"
            f"🟢 <b>Video Found & Decoded Successfully!</b>\n"
            f"──────────────────────────────\n"
            f"<i>Tap below to stream or download direct from your browser:</i>"
        )
        bot.edit_message_text(caption, message.chat.id, wait_msg.message_id, reply_markup=markup, parse_mode="HTML")
        auto_delete(message.chat.id, wait_msg.message_id)
    else:
        bot.edit_message_text("❌ <b>Could not extract stream.</b> Please verify your Terabox URL and try again.", message.chat.id, wait_msg.message_id, parse_mode="HTML")

# ================= FIXED & DEDICATED INSTAGRAM HANDLER =================
def execute_instagram_call(message, action_type, search_val):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user_id != ADMIN_ID and user["credits"] < 1:
        bot.reply_to(message, "❌ <i>Credits exhausted. Contact @team_lifexy</i>", parse_mode="HTML")
        return

    wait_msg = bot.reply_to(message, "📸⚡ <b><i>Fetching Instagram media...</i></b>", parse_mode="HTML")

    txt_clean = search_val.strip()
    is_url = "instagram.com" in txt_clean.lower() or "instagr.am" in txt_clean.lower()
    clean_username = txt_clean.replace("@", "").split("/")[-1].split("?")[0] if not is_url else ""

    endpoints_to_try = []

    if is_url:
        # If user passed an Instagram Post/Reel URL
        endpoints_to_try.append((f"{BASE_URL_OSINT}/instagram-download", {"key": OSINT_KEY, "type": "download", "url": txt_clean}))
        endpoints_to_try.append((f"{BASE_URL_OSINT}/instagram-posts-v2", {"key": OSINT_KEY, "type": "posts", "url": txt_clean}))
    else:
        # If user passed Username instead of URL
        if action_type == "download":
            action_type = "profile"
        
        if action_type in ["profile", "best"]:
            endpoints_to_try.append((f"{BASE_URL_OSINT}/instagram-best-v1", {"key": OSINT_KEY, "type": "best", "username": clean_username}))
            endpoints_to_try.append((f"{BASE_URL_OSINT}/instagram-media-v1", {"key": OSINT_KEY, "type": "media", "username": clean_username}))
        elif action_type == "posts":
            endpoints_to_try.append((f"{BASE_URL_OSINT}/instagram-posts-v2", {"key": OSINT_KEY, "type": "posts", "username": clean_username}))
        else:
            endpoints_to_try.append((f"{BASE_URL_OSINT}/instagram-media-v1", {"key": OSINT_KEY, "type": "media", "username": clean_username}))
            endpoints_to_try.append((f"{BASE_URL_OSINT}/instagram-best-v1", {"key": OSINT_KEY, "type": "best", "username": clean_username}))

    extracted_media = None
    final_response = None
    has_blocked_error = False

    for ep, params in endpoints_to_try:
        try:
            r = requests.get(ep, params=params, timeout=20)
            if r.status_code == 200:
                res = r.json()
                
                # Check for server block inside response payload
                res_str = json.dumps(res).lower()
                if "blocked" in res_str or "http 401" in res_str or "\"ok\":false" in res_str:
                    has_blocked_error = True
                    continue

                extracted_media = extract_media_url(res)
                final_response = res
                if extracted_media:
                    break
        except Exception:
            continue

    if user_id != ADMIN_ID:
        user["credits"] -= 1

    user["lookups"] += 1
    global total_lookups
    total_lookups += 1
    save_data()

    # If valid Video/Photo URL extracted, send direct Telegram file!
    if extracted_media:
        bot.delete_message(message.chat.id, wait_msg.message_id)
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("▶️ Open Media in Browser", url=extracted_media),
            InlineKeyboardButton("📥 Direct Download File", url=extracted_media)
        )

        is_video = any(ext in extracted_media.lower() for ext in [".mp4", ".mov", "m3u8", "video"])
        sent_successfully = False
        try:
            if is_video:
                bot.send_video(message.chat.id, extracted_media, caption="📸 <b>Instagram Video Downloaded Successfully!</b>\n⚡ <i>Powered by @team_lifexy</i>", reply_markup=markup, parse_mode="HTML")
            else:
                bot.send_photo(message.chat.id, extracted_media, caption="📸 <b>Instagram Media Downloaded Successfully!</b>\n⚡ <i>Powered by @team_lifexy</i>", reply_markup=markup, parse_mode="HTML")
            sent_successfully = True
        except Exception:
            pass

        if not sent_successfully:
            bot.send_message(
                message.chat.id,
                f"📸 <b>Instagram Media Ready!</b>\n\nClick below to stream or download:",
                reply_markup=markup,
                parse_mode="HTML"
            )
        return

    # If profile data or raw response fetched
    if final_response:
        result_str = json.dumps(final_response, indent=2, ensure_ascii=False)
        scrub_targets = [r"(?i)onlyh4ckerzon", r"(?i)onlyhackerzon", r"(?i)rohit", r"(?i)@froxtdevil", r"(?i)optimusprime"]
        for target in scrub_targets:
            result_str = re.sub(target, "Crown 👑", result_str)

        if len(result_str) > 3000:
            result_str = result_str[:3000] + "\n... [Output Truncated]"

        out_msg = (
            f"📸 <b>Crown Instagram Intelligence (M4)</b> 📸\n"
            f"──────────────────────────────\n"
            f"🔍 <b>Input:</b> <code>{search_val}</code>\n"
            f"──────────────────────────────\n"
            f"<b>Output Data:</b>\n"
            f"<pre>{result_str}</pre>\n"
            f"──────────────────────────────\n"
            f"⚡ <b>Powered By: @team_lifexy</b>"
        )
        bot.edit_message_text(out_msg, message.chat.id, wait_msg.message_id, parse_mode="HTML")
        auto_delete(message.chat.id, wait_msg.message_id)
    else:
        msg_text = (
            f"❌ <b>Instagram Request Failed!</b>\n\n"
            f"• <b>Reason:</b> Instagram server restriction or invalid URL.\n"
            f"• <b>Note:</b> Make sure to paste a valid Instagram Reel/Post link (e.g. <code>https://www.instagram.com/reel/...</code>) for downloading media."
        )
        bot.edit_message_text(msg_text, message.chat.id, wait_msg.message_id, parse_mode="HTML")

# ================= GENERAL API ENGINE =================
def execute_api_call(message, endpoint_url, query_label, search_val, params=None):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user_id != ADMIN_ID and user["credits"] < 1:
        bot.reply_to(message, "❌ <i>Credits exhausted. Contact @team_lifexy</i>", parse_mode="HTML")
        return

    wait_msg = bot.reply_to(message, "👑📡 <b><i>Fetching requested data & video links...</i></b>", parse_mode="HTML")

    try:
        r = requests.get(endpoint_url, params=params, timeout=25)
        
        if r.status_code == 404:
            bot.edit_message_text("⚠️ <b>Error 404:</b> Resource not found.", message.chat.id, wait_msg.message_id, parse_mode="HTML")
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

        extracted_media = extract_media_url(api_response)

        result_str = json.dumps(api_response, indent=2, ensure_ascii=False)
        
        scrub_targets = [r"(?i)onlyh4ckerzon", r"(?i)onlyhackerzon", r"(?i)rohit", r"(?i)@froxtdevil", r"(?i)optimusprime"]
        for target in scrub_targets:
            result_str = re.sub(target, "Crown 👑", result_str)

        if len(result_str) > 3000:
            result_str = result_str[:3000] + "\n... [Output Truncated]"

        out_msg = (
            f"👑 <b>Crown Intelligence Result (M4)</b> 👑\n"
            f"──────────────────────────────\n"
            f"🔍 <b>Feature:</b> <i>{query_label}</i>\n"
            f"📌 <b>Query Input:</b> <code>{search_val}</code>\n"
            f"──────────────────────────────\n"
            f"<b>Output Data:</b>\n"
            f"<pre>{result_str}</pre>\n"
            f"──────────────────────────────\n"
            f"⚡ <b>Powered By: @team_lifexy</b>"
        )
        
        markup = None
        if extracted_media:
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("▶️ Open Video in Chrome / Browser", url=extracted_media),
                InlineKeyboardButton("📥 Direct Download File", url=extracted_media)
            )

        bot.edit_message_text(out_msg, message.chat.id, wait_msg.message_id, reply_markup=markup, parse_mode="HTML")
        auto_delete(message.chat.id, wait_msg.message_id)

    except Exception:
        bot.edit_message_text("❌ <b>Request Error:</b> API service timed out or server unreachable.", message.chat.id, wait_msg.message_id, parse_mode="HTML")

# ================= INPUT ROUTER & AUTO DETECTOR =================
@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def handle_queries(message):
    txt = message.text.strip()
    user_id = message.from_user.id

    # 1. Quick Keyboard Buttons
    if txt == "👻 Snapchat Video Hub":
        bot.reply_to(message, "👑 <b>Snapchat Toolkit:</b>", reply_markup=snapchat_menu(), parse_mode="HTML")
        return
    elif txt == "📦 Terabox Direct Downloader":
        bot.reply_to(message, "👑 <b>Terabox Toolkit:</b>", reply_markup=terabox_menu(), parse_mode="HTML")
        return
    elif txt == "📸 Instagram Hub":
        bot.reply_to(message, "👑 <b>Instagram Toolkit:</b>", reply_markup=instagram_menu(), parse_mode="HTML")
        return
    elif txt == "🚗 Vehicle RC & Info":
        user_steps[user_id] = "ask_vehicle"
        bot.reply_to(message, "👑 <b>Enter Vehicle Registration Number:</b>\n<i>(e.g., MH12DE1433)</i>", parse_mode="HTML")
        return
    elif txt == "📧 Email Intelligence":
        user_steps[user_id] = "ask_email_info"
        bot.reply_to(message, "👑 <b>Enter Target Email:</b>", parse_mode="HTML")
        return
    elif txt == "🌐 IP & Network Tools":
        bot.reply_to(message, "👑 <b>Network Utilities:</b>", reply_markup=geo_menu(), parse_mode="HTML")
        return
    elif txt == "💎 My VIP Account":
        user = get_user(user_id)
        bot.reply_to(message, f"👑 <b>Credits Available:</b> {user['credits']}\n<b>Developer:</b> @team_lifexy", parse_mode="HTML")
        return
    elif txt == "🔙 Main Menu":
        bot.reply_to(message, "👑 <b>Main Control Menu:</b>", reply_markup=main_menu(), parse_mode="HTML")
        return

    current_step = user_steps.get(user_id)
    user_steps[user_id] = None

    tb_domains = ["terabox", "1024terabox", "teraboxapp", "freeterabox", "mirrobox", "neptunebox", "4funbox"]
    is_terabox = any(d in txt.lower() for d in tb_domains)

    # 2. Direct Menu Step Handlers
    if current_step:
        # Snapchat Handlers
        if current_step == "ask_snap_dl":
            url = f"{BASE_URL_OSINT}/snapchat-download"
            params = {"key": OSINT_KEY, "action": "download", "query": txt}
            execute_api_call(message, url, "SNAPCHAT VIDEO ENCODING & MEDIA", txt, params=params)
            return
        elif current_step == "ask_snap_story":
            url = f"{BASE_URL_OSINT}/snapchat-story"
            params = {"key": OSINT_KEY, "action": "stories", "username": txt}
            execute_api_call(message, url, "SNAPCHAT STORIES & VIDEOS", txt, params=params)
            return
        elif current_step == "ask_snap_high":
            url = f"{BASE_URL_OSINT}/snapchat-highlight"
            params = {"key": OSINT_KEY, "action": "highlights", "username": txt}
            execute_api_call(message, url, "SNAPCHAT HIGHLIGHTS", txt, params=params)
            return
        elif current_step == "ask_snap_all":
            url = f"{BASE_URL_OSINT}/snapchat-all"
            params = {"key": OSINT_KEY, "action": "all", "username": txt}
            execute_api_call(message, url, "SNAPCHAT ALL DATA", txt, params=params)
            return

        # Terabox Handlers
        elif current_step in ["ask_tb_s1", "ask_tb_v2"]:
            execute_terabox_call(message, txt)
            return

        # Instagram Handlers (UPDATED & ROUTED SAFELY)
        elif current_step == "ask_ig_dl":
            execute_instagram_call(message, "download", txt)
            return
        elif current_step == "ask_ig_best":
            execute_instagram_call(message, "profile", txt)
            return
        elif current_step == "ask_ig_media":
            execute_instagram_call(message, "media", txt)
            return
        elif current_step == "ask_ig_posts":
            execute_instagram_call(message, "posts", txt)
            return

        # Identity Handlers
        elif current_step == "ask_vehicle":
            url = f"{BASE_URL_OSINT}/vehicle-v1"
            params = {"key": OSINT_KEY, "type": "v1", "rc": txt.upper()}
            execute_api_call(message, url, "VEHICLE RC LOOKUP", txt.upper(), params=params)
            return
        elif current_step == "ask_email_info":
            url = f"{BASE_URL_OSINT}/email-info"
            params = {"key": OSINT_KEY, "mail": txt}
            execute_api_call(message, url, "EMAIL INTEL LOOKUP", txt, params=params)
            return
        elif current_step == "ask_phone":
            url = f"{BASE_URL_MAIN}/ph-tracker"
            params = {"token": TOKEN, "number": txt}
            execute_api_call(message, url, "PHONE TRACKER", txt, params=params)
            return
        elif current_step == "ask_truecaller":
            url = f"{BASE_URL_OSINT}/truecaller-info"
            params = {"key": OSINT_KEY, "number": txt}
            execute_api_call(message, url, "TRUECALLER SEARCH", txt, params=params)
            return
        elif current_step == "ask_pan":
            url = f"{BASE_URL_OSINT}/pan-info"
            params = {"key": OSINT_KEY, "pan": txt.upper()}
            execute_api_call(message, url, "PAN DETAILS", txt.upper(), params=params)
            return
        elif current_step == "ask_gst":
            url = f"{BASE_URL_OSINT}/gst-search"
            params = {"key": OSINT_KEY, "gstin": txt.upper()}
            execute_api_call(message, url, "GST SEARCH", txt.upper(), params=params)
            return

        # Utilities & AI Handlers
        elif current_step == "ask_web":
            url = f"{BASE_URL_OSINT}/website-source"
            params = {"key": OSINT_KEY, "url": txt}
            execute_api_call(message, url, "WEBSITE SCRAPER", txt, params=params)
            return
        elif current_step == "ask_ip1":
            url = f"{BASE_URL_OSINT}/ip-v1"
            params = {"key": OSINT_KEY, "query": txt}
            execute_api_call(message, url, "IP LOOKUP", txt, params=params)
            return
        elif current_step == "ask_weather":
            url = f"{BASE_URL_OSINT}/weather-info"
            params = {"key": OSINT_KEY, "city": txt}
            execute_api_call(message, url, "WEATHER SEARCH", txt, params=params)
            return
        elif current_step == "ask_github":
            url = f"{BASE_URL_OSINT}/github-repos"
            params = {"key": OSINT_KEY, "q": txt}
            execute_api_call(message, url, "GITHUB SEARCH", txt, params=params)
            return
        elif current_step == "ask_aigf":
            url = f"{BASE_URL_OSINT}/ai-gf"
            params = {"key": OSINT_KEY, "prompt": txt}
            execute_api_call(message, url, "AI CHATBOT", txt, params=params)
            return
        elif current_step == "ask_aiimg":
            url = f"{BASE_URL_OSINT}/image-generator"
            params = {"key": OSINT_KEY, "prompt": txt}
            execute_api_call(message, url, "AI IMAGE GENERATOR", txt, params=params)
            return

    # 3. Automatic Format Detector
    if is_terabox:
        execute_terabox_call(message, txt)
    elif "snapchat.com" in txt.lower():
        url = f"{BASE_URL_OSINT}/snapchat-download"
        params = {"key": OSINT_KEY, "action": "download", "query": txt}
        execute_api_call(message, url, "SNAPCHAT VIDEO DOWNLOAD", txt, params=params)
    elif "instagram.com" in txt.lower() or "instagr.am" in txt.lower():
        execute_instagram_call(message, "download", txt)
    elif "@" in txt and "." in txt and not txt.startswith("http"):
        url = f"{BASE_URL_OSINT}/email-info"
        params = {"key": OSINT_KEY, "mail": txt}
        execute_api_call(message, url, "EMAIL INTEL", txt, params=params)
    elif txt.isdigit() and len(txt) == 10:
        url = f"{BASE_URL_MAIN}/ph-tracker"
        params = {"token": TOKEN, "number": txt}
        execute_api_call(message, url, "PHONE RECORD", txt, params=params)
    elif re.match(r"^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$", txt.upper()):
        url = f"{BASE_URL_OSINT}/vehicle-v1"
        params = {"key": OSINT_KEY, "type": "v1", "rc": txt.upper()}
        execute_api_call(message, url, "VEHICLE RC LOOKUP", txt.upper(), params=params)
    else:
        err = bot.reply_to(message, "⚠️ <b>Unrecognized Input!</b>\n<i>Please press /start to open the interactive main menu.</i>", parse_mode="HTML")
        auto_delete(err.chat.id, err.message_id)

# ================= LAUNCH BOT =================
if __name__ == "__main__":
    print("👑 CROWN BOT M4 ULTRA IS READY AND RUNNING!")
    keep_alive()
    bot.infinity_polling()

