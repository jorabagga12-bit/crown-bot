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
        <title>👑 CROWN VIP OSINT & STREAM - Dashboard</title>
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
            <h1>👑 CROWN VIP OSINT & MEDIA</h1>
            <div class="status">🟢 Ultra Engine Online</div>
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

# ================= HELPER: TERABOX URL NORMALIZER =================
def clean_terabox_url(raw_url):
    """सारे टेराबॉक्स लिंक्स (surl, filelist, etc.) को Clean Standard URL में बदलता है"""
    raw_url = raw_url.strip()
    if "surl=" in raw_url:
        surl = raw_url.split("surl=")[-1].split("&")[0]
        if not surl.startswith("1"):
            surl = "1" + surl
        return f"https://terabox.com/s/{surl}"
    return raw_url

# ================= REPLY KEYBOARD (FULL GRID BOXES) =================
def get_reply_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📦 Terabox Player"),
        KeyboardButton("🚗 Vehicle RC Lookup")
    )
    markup.add(
        KeyboardButton("🇮🇳 Indian Number"),
        KeyboardButton("📞 Truecaller Search")
    )
    markup.add(
        KeyboardButton("🌐 Website Scraper"),
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

# ================= INLINE MENUS (GRID BOXES) =================
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔍 Identity & Govt", callback_data="menu_identity"),
        InlineKeyboardButton("📱 Social & Media", callback_data="menu_social")
    )
    markup.add(
        InlineKeyboardButton("📦 Terabox Tools 🎬", callback_data="menu_terabox"),
        InlineKeyboardButton("🌍 Network & Web", callback_data="menu_geo")
    )
    markup.add(
        InlineKeyboardButton("🤖 AI & Utilities", callback_data="menu_ai"),
        InlineKeyboardButton("💎 VIP Profile", callback_data="profile")
    )
    return markup

def terabox_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🎬 Stream Video V1", callback_data="ask_tb_s1"),
        InlineKeyboardButton("🎬 Stream Video V2", callback_data="ask_tb_s2")
    )
    markup.add(
        InlineKeyboardButton("🎬 Stream Video V3", callback_data="ask_tb_s3"),
        InlineKeyboardButton("📥 Download File V2", callback_data="ask_tb_f2")
    )
    markup.add(
        InlineKeyboardButton("📥 Download Video V2", callback_data="ask_tb_v2")
    )
    markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main"))
    return markup

def identity_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📱 Phone Number", callback_data="ask_phone"),
        InlineKeyboardButton("🚗 Vehicle RC V1", callback_data="ask_vehicle")
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
    markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main"))
    return markup

def social_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📸 Insta Profile", callback_data="ask_ig_prof"),
        InlineKeyboardButton("⬇️ Insta Downloader", callback_data="ask_ig_dl")
    )
    markup.add(
        InlineKeyboardButton("🎵 Song Downloader", callback_data="ask_song"),
        InlineKeyboardButton("👥 Telegram Info", callback_data="ask_tg")
    )
    markup.add(
        InlineKeyboardButton("📺 YouTube Downloader", callback_data="ask_ytdl"),
        InlineKeyboardButton("🎮 BGMI Player", callback_data="ask_bgmi")
    )
    markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main"))
    return markup

def geo_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🌐 Website Scraper", callback_data="ask_web"),
        InlineKeyboardButton("🌐 IP Tracker V2", callback_data="ask_ip2")
    )
    markup.add(
        InlineKeyboardButton("📍 Pincode Info", callback_data="ask_pin"),
        InlineKeyboardButton("🌤️ Weather Info", callback_data="ask_weather")
    )
    markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main"))
    return markup

def ai_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💖 AI Girlfriend", callback_data="ask_aigf"),
        InlineKeyboardButton("🎨 AI Image Gen", callback_data="ask_aiimg")
    )
    markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main"))
    return markup

# ================= START COMMAND =================
@bot.message_handler(commands=["start"])
def start(message):
    get_user(message.from_user.id)
    user_steps[message.from_user.id] = None 

    welcome_text = (
        f"<b>👑 CROWN VIP OSINT & STREAM HUB 👑</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👋 Swagat Hai, <b>{message.from_user.first_name}</b>!\n\n"
        f"⚡ <i>Niche diye gaye kisi bhi Dabbe (Button) par tap karein:</i>\n"
    )

    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode="HTML")
    bot.send_message(message.chat.id, "👇 <b>Quick Grid Keyboard:</b>", reply_markup=get_reply_keyboard(), parse_mode="HTML")

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
            f"👑 <b><u>CROWN VIP PROFILE</u></b> 👑\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🆔 <b>User:</b> <i>{call.from_user.first_name}</i>\n"
            f"💎 <b>Credits:</b> {credits_display}\n"
            f"🔍 <b>Total Lookups:</b> <b>{user['lookups']}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<i>Powered by CROWN 👑</i>"
        )
        bot.send_message(chat_id, info_text, parse_mode="HTML")

    else:
        prompts = {
            "ask_phone": "📱 <i>Send 10-digit Phone Number.</i>",
            "ask_vehicle": "🚗 <i>Send Vehicle Number (e.g. MH12DE1433).</i>",
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
            "ask_ytdl": "📺 <i>Send YouTube Video Link.</i>",
            "ask_bgmi": "🎮 <i>Send BGMI Player ID.</i>",
            "ask_web": "🌐 <i>Send Full Website URL (e.g., https://example.com).</i>",
            "ask_ip2": "🌐 <i>Send Target IP Address.</i>",
            "ask_pin": "📍 <i>Send 6-digit Pincode.</i>",
            "ask_weather": "🌤️ <i>Send City Name for Weather Info.</i>",
            "ask_tb_s1": "🎬 <i>Send Terabox Link for Video Stream V1.</i>",
            "ask_tb_s2": "🎬 <i>Send Terabox Link for Video Stream V2.</i>",
            "ask_tb_s3": "🎬 <i>Send Terabox Link for Video Stream V3.</i>",
            "ask_tb_f2": "📥 <i>Send Terabox Link for File Download V2.</i>",
            "ask_tb_v2": "📥 <i>Send Terabox Link for Video Download V2.</i>",
            "ask_aigf": "💖 <i>Send a message to your AI GF!</i>",
            "ask_aiimg": "🎨 <i>Send prompt to generate Image.</i>"
        }
        
        if call.data in prompts:
            user_steps[user_id] = call.data
            bot.send_message(chat_id, f"👑 <b>CROWN TARGET LOCKED:</b>\n{prompts[call.data]}", parse_mode="HTML")

    bot.answer_callback_query(call.id)

# ================= TERABOX ADVANCED ENGINE WITH MULTI-FALLBACK =================
def execute_terabox_call(message, preferred_endpoint, query_label, search_val, params=None):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user_id != ADMIN_ID and user["credits"] < 1:
        bot.reply_to(message, "❌ <i>Not enough credits. Contact Admin!</i>", parse_mode="HTML")
        return

    wait_msg = bot.reply_to(message, "🎬🍿 <b><i>CROWN Terabox Video Stream Extract Ho Raha Hai...</i></b>", parse_mode="HTML")

    normalized_url = clean_terabox_url(search_val)
    
    # ऑटो-फॉलबैक लिस्ट (एक सर्वर फेल होने पर अगला अपने आप चलेगा)
    endpoints_to_try = [
        (f"{BASE_URL_OSINT}/terabox-stream-v2", "video_streamv2"),
        (f"{BASE_URL_OSINT}/terabox-stream-v3", "video_streamv3"),
        (f"{BASE_URL_OSINT}/terabox-stream", "video_stream"),
        (f"{BASE_URL_OSINT}/terabox-video-v2", "video_downloadv2")
    ]
    
    # अगर यूजर ने खास ऑप्शन सिलेक्ट किया है, तो उसे सबसे पहले रखें
    if preferred_endpoint:
        for i, ep_info in enumerate(endpoints_to_try):
            if ep_info[0] == preferred_endpoint:
                endpoints_to_try.insert(0, endpoints_to_try.pop(i))
                break

    stream_link = None

    for ep, type_param in endpoints_to_try:
        try:
            req_params = {"key": OSINT_KEY, "type": type_param, "url": normalized_url}
            r = requests.get(ep, params=req_params, timeout=12)
            
            if r.status_code != 200:
                continue
                
            api_response = r.json()
            
            if isinstance(api_response, dict):
                stream_link = (
                    api_response.get("stream_url") or 
                    api_response.get("download_url") or 
                    api_response.get("url") or 
                    api_response.get("link") or 
                    api_response.get("fast_url")
                )
                if not stream_link and isinstance(api_response.get("data"), dict):
                    stream_link = (
                        api_response["data"].get("download_url") or 
                        api_response["data"].get("url") or 
                        api_response["data"].get("stream_url")
                    )
                elif not stream_link and isinstance(api_response.get("data"), list) and len(api_response["data"]) > 0:
                    item = api_response["data"][0]
                    if isinstance(item, dict):
                        stream_link = item.get("download_url") or item.get("url") or item.get("stream_url")

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
            InlineKeyboardButton("▶️ WATCH / STREAM VIDEO NOW", url=stream_link),
            InlineKeyboardButton("📥 FAST DOWNLOAD VIDEO", url=stream_link)
        )
        
        caption_text = (
            f"👑 <b>CROWN TERABOX VIDEO PLAYER</b> 👑\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎬 <b>Status:</b> <i>Video Stream Ready!</i>\n"
            f"🔗 <b>Target:</b> <code>{normalized_url[:40]}...</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👇 <b>Niche 'WATCH / STREAM' button par click karke direct video dekho:</b>"
        )
        bot.edit_message_text(caption_text, message.chat.id, wait_msg.message_id, reply_markup=markup, parse_mode="HTML")
        auto_delete(message.chat.id, wait_msg.message_id)
    else:
        bot.edit_message_text("❌ <b>Video Extract Error:</b> Terabox API load nahi kar pa rahi hai. Kripya naya link bhej kar check karein.", message.chat.id, wait_msg.message_id, parse_mode="HTML")

# ================= STANDARD API ENGINE =================
def execute_api_call(message, endpoint_url, query_label, search_val, params=None):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user_id != ADMIN_ID and user["credits"] < 1:
        bot.reply_to(message, "❌ <i>Not enough credits. Contact Admin!</i>", parse_mode="HTML")
        return

    wait_msg = bot.reply_to(message, "👑📡 <b><i>Extracting CROWN Live Database...</i></b>", parse_mode="HTML")

    try:
        r = requests.get(endpoint_url, params=params, timeout=30)
        
        if r.status_code == 404:
            bot.edit_message_text(f"⚠️ <b>API Error (404):</b> <i>Target data not found or service offline.</i>", message.chat.id, wait_msg.message_id, parse_mode="HTML")
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

        result_json = json.dumps(api_response, indent=2, ensure_ascii=False)
        
        scrub_patterns = [
            r"(?i)onlyh4ckerzon",
            r"(?i)onlyhackerzon",
            r"(?i)rohit\s*padhwe",
            r"(?i)rohit",
            r"(?i)@froxtdevil",
            r"(?i)froxtdevil",
            r"(?i)@optimusprime50",
            r"(?i)DRACO"
        ]
        
        for pattern in scrub_patterns:
            result_json = re.sub(pattern, "Crown 👑", result_json)

        if len(result_json) > 3500:
            result_json = result_json[:3500] + "\n... [DATA TRUNCATED]"

        text = f"""
👑 <b>CROWN INTEL & MEDIA SYSTEM</b> 👑
━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 <b>TARGET:</b> <i>{query_label}</i>
📌 <b>INPUT:</b> <code>{search_val}</code>
━━━━━━━━━━━━━━━━━━━━━━━━━━
<b><u>DATABASE / STREAM OUTPUT:</u></b>
<pre>{result_json}</pre>
━━━━━━━━━━━━━━━━━━━━━━━━━━
👑⚡ <b>POWERED BY: CROWN 👑</b>
"""
        bot.edit_message_text(text, message.chat.id, wait_msg.message_id, parse_mode="HTML")
        auto_delete(message.chat.id, wait_msg.message_id)

    except Exception:
        bot.edit_message_text(f"❌ <b>Execution Error:</b> <code>System Timeout or API Connection Issue</code>", message.chat.id, wait_msg.message_id, parse_mode="HTML")

# ================= SMART QUERY ROUTER =================
@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def handle_queries(message):
    txt = message.text.strip()
    user_id = message.from_user.id

    # 0. Reply Keyboard Handlers
    if txt == "📦 Terabox Player":
        bot.reply_to(message, "👑 <b>Choose Terabox Option Below:</b>", reply_markup=terabox_menu(), parse_mode="HTML")
        return
    elif txt == "🚗 Vehicle RC Lookup":
        user_steps[user_id] = "ask_vehicle"
        bot.reply_to(message, "👑 <b>CROWN TARGET LOCKED:</b>\n<i>Send Vehicle Registration Number.</i>", parse_mode="HTML")
        return
    elif txt == "🇮🇳 Indian Number":
        user_steps[user_id] = "ask_phone"
        bot.reply_to(message, "👑 <b>CROWN TARGET LOCKED:</b>\n<i>Send 10-digit Phone Number.</i>", parse_mode="HTML")
        return
    elif txt == "📞 Truecaller Search":
        user_steps[user_id] = "ask_truecaller"
        bot.reply_to(message, "👑 <i>Send Phone Number for Truecaller Lookup.</i>", parse_mode="HTML")
        return
    elif txt == "🌐 Website Scraper":
        user_steps[user_id] = "ask_web"
        bot.reply_to(message, "👑 <i>Send Full Website URL to Scrape.</i>", parse_mode="HTML")
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

    # Terabox Keywords Checking Array
    tb_domains = ["terabox", "1024terabox", "teraboxapp", "freeterabox", "mirrobox", "neptunebox", "4funbox", "momolee"]
    is_terabox_link = any(domain in txt.lower() for domain in tb_domains)

    # 1. State-Based Routing
    if current_step:
        if current_step == "ask_web":
            url = f"{BASE_URL_OSINT}/website-source"
            params = {"key": OSINT_KEY, "url": txt}
            execute_api_call(message, url, "WEBSITE SCRAPER", txt, params=params)
            return
        elif current_step == "ask_tb_s1":
            execute_terabox_call(message, f"{BASE_URL_OSINT}/terabox-stream", "TERABOX STREAM V1", txt)
            return
        elif current_step == "ask_tb_s2":
            execute_terabox_call(message, f"{BASE_URL_OSINT}/terabox-stream-v2", "TERABOX STREAM V2", txt)
            return
        elif current_step == "ask_tb_s3":
            execute_terabox_call(message, f"{BASE_URL_OSINT}/terabox-stream-v3", "TERABOX STREAM V3", txt)
            return
        elif current_step == "ask_tb_f2":
            execute_terabox_call(message, f"{BASE_URL_OSINT}/terabox-file-v2", "TERABOX FILE DL V2", txt)
            return
        elif current_step == "ask_tb_v2":
            execute_terabox_call(message, f"{BASE_URL_OSINT}/terabox-video-v2", "TERABOX VIDEO DL V2", txt)
            return

        # Standard Tools
        elif current_step == "ask_vehicle":
            url = f"{BASE_URL_OSINT}/vehicle-v1"
            params = {"key": OSINT_KEY, "type": "v1", "rc": txt.upper()}
            execute_api_call(message, url, "VEHICLE RC V1", txt.upper(), params=params)
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
        elif current_step == "ask_song":
            url = f"{BASE_URL_OSINT}/song-download"
            params = {"key": OSINT_KEY, "song": txt}
            execute_api_call(message, url, "SONG DOWNLOADER", txt, params=params)
            return
        elif current_step == "ask_tg":
            url = f"{BASE_URL_OSINT}/telegram-info"
            params = {"key": OSINT_KEY, "tg": txt}
            execute_api_call(message, url, "TELEGRAM USER INFO", txt, params=params)
            return
        elif current_step == "ask_ytdl":
            url = f"{BASE_URL_OSINT}/youtube-download"
            params = {"key": OSINT_KEY, "download": "1", "url": txt}
            execute_api_call(message, url, "YOUTUBE DOWNLOADER", txt, params=params)
            return
        elif current_step == "ask_weather":
            url = f"{BASE_URL_OSINT}/weather-info"
            params = {"key": OSINT_KEY, "city": txt}
            execute_api_call(message, url, "WEATHER INFO", txt, params=params)
            return
        elif current_step == "ask_aadhar":
            url = f"{BASE_URL_MAIN}/aadhar-info"
            params = {"token": TOKEN, "id": txt}
            execute_api_call(message, url, "AADHAAR NUMBER", txt, params=params)
            return
        elif current_step == "ask_pan":
            url = f"{BASE_URL_OSINT}/pan-info"
            params = {"key": OSINT_KEY, "pan": txt.upper()}
            execute_api_call(message, url, "PAN CARD", txt.upper(), params=params)
            return
        elif current_step == "ask_gst":
            url = f"{BASE_URL_OSINT}/gst-search"
            params = {"key": OSINT_KEY, "gstin": txt.upper()}
            execute_api_call(message, url, "GST SEARCH", txt.upper(), params=params)
            return
        elif current_step == "ask_ifsc":
            url = f"{BASE_URL_OSINT}/ifsc-info"
            params = {"key": OSINT_KEY, "ifsc": txt.upper()}
            execute_api_call(message, url, "IFSC LOOKUP", txt.upper(), params=params)
            return
        elif current_step == "ask_imei":
            url = f"{BASE_URL_OSINT}/imei-info"
            params = {"key": OSINT_KEY, "imei_number": txt}
            execute_api_call(message, url, "IMEI INFO", txt, params=params)
            return
        elif current_step == "ask_bgmi":
            url = f"{BASE_URL_OSINT}/bgmi-info"
            params = {"key": OSINT_KEY, "user": txt}
            execute_api_call(message, url, "BGMI PLAYER", txt, params=params)
            return

    # 2. Direct Query Auto-Routing
    if is_terabox_link:
        execute_terabox_call(message, None, "TERABOX AUTO-STREAM", txt)
    elif txt.startswith("http://") or txt.startswith("https://"):
        url = f"{BASE_URL_OSINT}/website-source"
        params = {"key": OSINT_KEY, "url": txt}
        execute_api_call(message, url, "WEBSITE SCRAPER", txt, params=params)
    elif txt.isdigit() and len(txt) == 10:
        url = f"{BASE_URL_MAIN}/ph-tracker"
        params = {"token": TOKEN, "number": txt}
        execute_api_call(message, url, "PHONE RECORD", txt, params=params)
    elif txt.isdigit() and len(txt) == 12:
        url = f"{BASE_URL_MAIN}/aadhar-info"
        params = {"token": TOKEN, "id": txt}
        execute_api_call(message, url, "AADHAAR NUMBER", txt, params=params)
    elif re.match(r"^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$", txt.upper()):
        url = f"{BASE_URL_OSINT}/vehicle-v1"
        params = {"key": OSINT_KEY, "type": "v1", "rc": txt.upper()}
        execute_api_call(message, url, "VEHICLE RC V1", txt.upper(), params=params)
    else:
        msg = bot.reply_to(message, "❌ <b>Format Unidentified!</b>\n<i>Kripya /start dabayein aur menu se dabba select karein.</i>", parse_mode="HTML")
        auto_delete(msg.chat.id, msg.message_id)

# ================= RUN SERVER =================
if __name__ == "__main__":
    print("👑 CROWN VIP OSINT & TERABOX STREAM BOT IS ONLINE!")
    keep_alive()
    bot.infinity_polling()
