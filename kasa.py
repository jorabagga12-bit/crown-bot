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
            <div class="status">🟢 Ultra 30+ APIs Engine Online</div>
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
        KeyboardButton("📸 Instagram Hub")
    )
    markup.add(
        KeyboardButton("👻 Snapchat Tools"),
        KeyboardButton("📧 Email Info Lookup")
    )
    markup.add(
        KeyboardButton("🚗 Vehicle RC Lookup"),
        KeyboardButton("🌐 Website Scraper")
    )
    markup.add(
        KeyboardButton("💎 My Credits"),
        KeyboardButton("🔙 Main Menu")
    )
    return markup

# ================= INLINE MENUS (GRID BOXES) =================
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔍 Identity & Govt", callback_data="menu_identity"),
        InlineKeyboardButton("📸 Instagram Hub", callback_data="menu_instagram")
    )
    markup.add(
        InlineKeyboardButton("👻 Snapchat Tools", callback_data="menu_snapchat"),
        InlineKeyboardButton("📦 Terabox Tools 🎬", callback_data="menu_terabox")
    )
    markup.add(
        InlineKeyboardButton("🌍 Network & Web", callback_data="menu_geo"),
        InlineKeyboardButton("🤖 AI & Utilities", callback_data="menu_ai")
    )
    markup.add(InlineKeyboardButton("💎 VIP Profile", callback_data="profile"))
    return markup

def identity_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📧 Email Info", callback_data="ask_email_info"),
        InlineKeyboardButton("📱 Phone Number", callback_data="ask_phone")
    )
    markup.add(
        InlineKeyboardButton("🚗 Vehicle RC", callback_data="ask_vehicle"),
        InlineKeyboardButton("📞 Truecaller", callback_data="ask_truecaller")
    )
    markup.add(
        InlineKeyboardButton("🪪 Aadhaar Info", callback_data="ask_aadhar"),
        InlineKeyboardButton("📇 PAN Card", callback_data="ask_pan")
    )
    markup.add(
        InlineKeyboardButton("🏢 GST Search", callback_data="ask_gst"),
        InlineKeyboardButton("🏦 IFSC Bank", callback_data="ask_ifsc")
    )
    markup.add(
        InlineKeyboardButton("📱 IMEI Info", callback_data="ask_imei"),
        InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main")
    )
    return markup

def instagram_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🏆 Best Profile V1", callback_data="ask_ig_best"),
        InlineKeyboardButton("⬇️ Reel/Post Download", callback_data="ask_ig_dl")
    )
    markup.add(
        InlineKeyboardButton("📂 Downloads V1", callback_data="ask_ig_downloads"),
        InlineKeyboardButton("🎬 Media V1", callback_data="ask_ig_media")
    )
    markup.add(
        InlineKeyboardButton("📝 Posts V2", callback_data="ask_ig_posts"),
        InlineKeyboardButton("👤 Profile V1", callback_data="ask_ig_p1")
    )
    markup.add(
        InlineKeyboardButton("👤 Profile V2", callback_data="ask_ig_p2"),
        InlineKeyboardButton("👤 Profile V3", callback_data="ask_ig_p3")
    )
    markup.add(
        InlineKeyboardButton("👤 Profile V3 V2", callback_data="ask_ig_p3v2"),
        InlineKeyboardButton("📊 Stats V1", callback_data="ask_ig_stats")
    )
    markup.add(
        InlineKeyboardButton("👤 User V1", callback_data="ask_ig_user"),
        InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main")
    )
    return markup

def snapchat_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("👻 Snapchat All Data", callback_data="ask_snap_all"),
        InlineKeyboardButton("🌟 Snapchat Highlight", callback_data="ask_snap_high")
    )
    markup.add(
        InlineKeyboardButton("🎞️ Snapchat Story", callback_data="ask_snap_story"),
        InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main")
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

def geo_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🌐 Website Scraper", callback_data="ask_web"),
        InlineKeyboardButton("🌐 IP Info V1", callback_data="ask_ip1")
    )
    markup.add(
        InlineKeyboardButton("🌐 IP Info V2", callback_data="ask_ip2"),
        InlineKeyboardButton("🌐 IP Info V3", callback_data="ask_ip3")
    )
    markup.add(
        InlineKeyboardButton("📍 Pincode Info", callback_data="ask_pin"),
        InlineKeyboardButton("🇮🇳 Country Info", callback_data="ask_country")
    )
    markup.add(
        InlineKeyboardButton("🌤️ Weather Info", callback_data="ask_weather"),
        InlineKeyboardButton("💻 GitHub Repos", callback_data="ask_github")
    )
    markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main"))
    return markup

def ai_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💖 AI Girlfriend", callback_data="ask_aigf"),
        InlineKeyboardButton("🎨 AI Image Gen", callback_data="ask_aiimg")
    )
    markup.add(
        InlineKeyboardButton("✨ Prompt Generator", callback_data="ask_promptgen"),
        InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main")
    )
    return markup

# ================= START COMMAND =================
@bot.message_handler(commands=["start"])
def start(message):
    get_user(message.from_user.id)
    user_steps[message.from_user.id] = None 

    welcome_text = (
        f"<b>👑 CROWN VIP OSINT & 30+ APIS HUB 👑</b>\n"
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
            "ask_email_info": "📧 <i>Send Email Address for Lookup (e.g. test@gmail.com).</i>",
            "ask_phone": "📱 <i>Send 10-digit Phone Number.</i>",
            "ask_vehicle": "🚗 <i>Send Vehicle Number (e.g. MH12DE1433).</i>",
            "ask_truecaller": "📞 <i>Send Phone Number for Truecaller.</i>",
            "ask_aadhar": "🪪 <i>Send 12-digit Aadhaar Number.</i>",
            "ask_pan": "📇 <i>Send 10-character PAN Card.</i>",
            "ask_gst": "🏢 <i>Send 15-character GSTIN Number.</i>",
            "ask_ifsc": "🏦 <i>Send Bank IFSC Code.</i>",
            "ask_imei": "📱 <i>Send 15-digit IMEI Number.</i>",
            
            # Instagram Hub
            "ask_ig_best": "🏆 <i>Send Instagram Username for Best Profile V1.</i>",
            "ask_ig_dl": "⬇️ <i>Send Instagram Reel/Post URL for Download.</i>",
            "ask_ig_downloads": "📂 <i>Send Instagram Username for Downloads V1.</i>",
            "ask_ig_media": "🎬 <i>Send Instagram Username for Media V1.</i>",
            "ask_ig_posts": "📝 <i>Send Instagram Username for Posts V2.</i>",
            "ask_ig_p1": "👤 <i>Send Instagram Username for Profile V1.</i>",
            "ask_ig_p2": "👤 <i>Send Instagram Username for Profile V2.</i>",
            "ask_ig_p3": "👤 <i>Send Instagram Username for Profile V3.</i>",
            "ask_ig_p3v2": "👤 <i>Send Instagram Username for Profile V3 V2.</i>",
            "ask_ig_stats": "📊 <i>Send Instagram Username for Stats V1.</i>",
            "ask_ig_user": "👤 <i>Send Instagram Username for User V1.</i>",
            
            # Snapchat Hub
            "ask_snap_all": "👻 <i>Send Snapchat Username for All Data.</i>",
            "ask_snap_high": "🌟 <i>Send Snapchat Username for Highlights.</i>",
            "ask_snap_story": "🎞️ <i>Send Snapchat Username for Stories & Media.</i>",
            
            # Terabox Hub
            "ask_tb_s1": "🎬 <i>Send Terabox Link for Video Stream V1.</i>",
            "ask_tb_s2": "🎬 <i>Send Terabox Link for Video Stream V2.</i>",
            "ask_tb_s3": "🎬 <i>Send Terabox Link for Video Stream V3.</i>",
            "ask_tb_f2": "📥 <i>Send Terabox Link for File Download V2.</i>",
            "ask_tb_v2": "📥 <i>Send Terabox Link for Video Download V2.</i>",
            
            # Geo & Web Hub
            "ask_web": "🌐 <i>Send Full Website URL to Scrape.</i>",
            "ask_ip1": "🌐 <i>Send IP Address for IP Info V1.</i>",
            "ask_ip2": "🌐 <i>Send IP Address for IP Info V2.</i>",
            "ask_ip3": "🌐 <i>Send IP Address for IP Info V3.</i>",
            "ask_pin": "📍 <i>Send 6-digit Pincode.</i>",
            "ask_country": "🇮🇳 <i>Send Country Name (e.g. india).</i>",
            "ask_weather": "🌤️ <i>Send City Name for Weather.</i>",
            "ask_github": "💻 <i>Send GitHub Query / Username (e.g. @abhigyan).</i>",
            
            # AI Hub
            "ask_aigf": "💖 <i>Send a prompt for AI Girlfriend chat.</i>",
            "ask_aiimg": "🎨 <i>Send a prompt to generate AI Image.</i>",
            "ask_promptgen": "✨ <i>Send Image URL to generate Prompt.</i>"
        }
        
        if call.data in prompts:
            user_steps[user_id] = call.data
            bot.send_message(chat_id, f"👑 <b>CROWN TARGET LOCKED:</b>\n{prompts[call.data]}", parse_mode="HTML")

    bot.answer_callback_query(call.id)

# ================= TERABOX ADVANCED ENGINE WITH MULTI-FALLBACK =================
def execute_terabox_call(message, preferred_endpoint, query_label, search_val):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user_id != ADMIN_ID and user["credits"] < 1:
        bot.reply_to(message, "❌ <i>Not enough credits. Contact Admin!</i>", parse_mode="HTML")
        return

    wait_msg = bot.reply_to(message, "🎬🍿 <b><i>CROWN Terabox Video Stream Extract Ho Raha Hai...</i></b>", parse_mode="HTML")
    normalized_url = clean_terabox_url(search_val)
    
    endpoints_to_try = [
        (f"{BASE_URL_OSINT}/terabox-stream-v2", "video_streamv2"),
        (f"{BASE_URL_OSINT}/terabox-stream-v3", "video_streamv3"),
        (f"{BASE_URL_OSINT}/terabox-stream", "video_stream"),
        (f"{BASE_URL_OSINT}/terabox-video-v2", "video_downloadv2")
    ]
    
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
            f"👇 <b>Niche button par click karke direct video dekho:</b>"
        )
        bot.edit_message_text(caption_text, message.chat.id, wait_msg.message_id, reply_markup=markup, parse_mode="HTML")
        auto_delete(message.chat.id, wait_msg.message_id)
    else:
        bot.edit_message_text("❌ <b>Video Extract Error:</b> Terabox API video load nahi kar pa rahi hai.", message.chat.id, wait_msg.message_id, parse_mode="HTML")

# ================= STANDARD API ENGINE WITH MEDIA BUTTON DETECTOR =================
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

        # Check if response has direct media/video URLs (like Snapchat stories, reels, downloads)
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
<b><u>DATABASE / MEDIA OUTPUT:</u></b>
<pre>{result_json}</pre>
━━━━━━━━━━━━━━━━━━━━━━━━━━
👑⚡ <b>POWERED BY: CROWN 👑</b>
"""
        markup = None
        if media_link:
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("▶️ WATCH / VIEW MEDIA NOW", url=media_link),
                InlineKeyboardButton("📥 DOWNLOAD MEDIA FILE", url=media_link)
            )

        bot.edit_message_text(text, message.chat.id, wait_msg.message_id, reply_markup=markup, parse_mode="HTML")
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
    elif txt == "📸 Instagram Hub":
        bot.reply_to(message, "👑 <b>Choose Instagram Option Below:</b>", reply_markup=instagram_menu(), parse_mode="HTML")
        return
    elif txt == "👻 Snapchat Tools":
        bot.reply_to(message, "👑 <b>Choose Snapchat Option Below:</b>", reply_markup=snapchat_menu(), parse_mode="HTML")
        return
    elif txt == "📧 Email Info Lookup":
        user_steps[user_id] = "ask_email_info"
        bot.reply_to(message, "👑 <b>CROWN TARGET LOCKED:</b>\n<i>Send Email Address for Lookup.</i>", parse_mode="HTML")
        return
    elif txt == "🚗 Vehicle RC Lookup":
        user_steps[user_id] = "ask_vehicle"
        bot.reply_to(message, "👑 <b>CROWN TARGET LOCKED:</b>\n<i>Send Vehicle Registration Number.</i>", parse_mode="HTML")
        return
    elif txt == "🌐 Website Scraper":
        user_steps[user_id] = "ask_web"
        bot.reply_to(message, "👑 <i>Send Full Website URL to Scrape.</i>", parse_mode="HTML")
        return
    elif txt == "💎 My Credits":
        user = get_user(user_id)
        bot.reply_to(message, f"👑 <b>Credits:</b> {user['credits']}", parse_mode="HTML")
        return
    elif txt == "🔙 Main Menu":
        bot.reply_to(message, "👑 <b>Main Menu:</b>", reply_markup=main_menu(), parse_mode="HTML")
        return

    current_step = user_steps.get(user_id)
    user_steps[user_id] = None 

    tb_domains = ["terabox", "1024terabox", "teraboxapp", "freeterabox", "mirrobox", "neptunebox", "4funbox", "momolee"]
    is_terabox_link = any(domain in txt.lower() for domain in tb_domains)

    # 1. State-Based Routing (All 30+ APIs)
    if current_step:
        # AI & Utilities
        if current_step == "ask_aigf":
            url = f"{BASE_URL_OSINT}/ai-gf"
            params = {"key": OSINT_KEY, "prompt": txt}
            execute_api_call(message, url, "AI GIRLFRIEND CHAT", txt, params=params)
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

        # Email & Identity
        elif current_step == "ask_email_info":
            url = f"{BASE_URL_OSINT}/email-info"
            params = {"key": OSINT_KEY, "mail": txt}
            execute_api_call(message, url, "EMAIL INFO LOOKUP", txt, params=params)
            return
        elif current_step == "ask_phone":
            url = f"{BASE_URL_MAIN}/ph-tracker"
            params = {"token": TOKEN, "number": txt}
            execute_api_call(message, url, "PHONE RECORD", txt, params=params)
            return
        elif current_step == "ask_vehicle":
            url = f"{BASE_URL_OSINT}/vehicle-v1"
            params = {"key": OSINT_KEY, "type": "v1", "rc": txt.upper()}
            execute_api_call(message, url, "VEHICLE RC V1", txt.upper(), params=params)
            return
        elif current_step == "ask_truecaller":
            url = f"{BASE_URL_OSINT}/truecaller-info"
            params = {"key": OSINT_KEY, "number": txt}
            execute_api_call(message, url, "TRUECALLER INFO", txt, params=params)
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

        # Instagram Hub
        elif current_step == "ask_ig_best":
            url = f"{BASE_URL_OSINT}/instagram-best-v1"
            params = {"key": OSINT_KEY, "type": "best", "username": txt}
            execute_api_call(message, url, "INSTAGRAM BEST PROFILE V1", txt, params=params)
            return
        elif current_step == "ask_ig_dl":
            url = f"{BASE_URL_OSINT}/instagram-download"
            params = {"key": OSINT_KEY, "type": "download", "url": txt}
            execute_api_call(message, url, "INSTAGRAM DOWNLOAD", txt, params=params)
            return
        elif current_step == "ask_ig_downloads":
            url = f"{BASE_URL_OSINT}/instagram-downloads-v1"
            params = {"key": OSINT_KEY, "type": "downloads", "username": txt}
            execute_api_call(message, url, "INSTAGRAM DOWNLOADS V1", txt, params=params)
            return
        elif current_step == "ask_ig_media":
            url = f"{BASE_URL_OSINT}/instagram-media-v1"
            params = {"key": OSINT_KEY, "type": "media", "username": txt}
            execute_api_call(message, url, "INSTAGRAM MEDIA V1", txt, params=params)
            return
        elif current_step == "ask_ig_posts":
            url = f"{BASE_URL_OSINT}/instagram-posts-v2"
            params = {"key": OSINT_KEY, "type": "posts", "username": txt}
            execute_api_call(message, url, "INSTAGRAM POSTS V2", txt, params=params)
            return
        elif current_step == "ask_ig_p1":
            url = f"{BASE_URL_OSINT}/instagram-profile-v1"
            params = {"key": OSINT_KEY, "type": "profile", "username": txt}
            execute_api_call(message, url, "INSTAGRAM PROFILE V1", txt, params=params)
            return
        elif current_step == "ask_ig_p2":
            url = f"{BASE_URL_OSINT}/instagram-profile-v2"
            params = {"key": OSINT_KEY, "type": "profile", "username": txt}
            execute_api_call(message, url, "INSTAGRAM PROFILE V2", txt, params=params)
            return
        elif current_step == "ask_ig_p3":
            url = f"{BASE_URL_OSINT}/instagram-profile-v3"
            params = {"key": OSINT_KEY, "type": "profile", "username": txt}
            execute_api_call(message, url, "INSTAGRAM PROFILE V3", txt, params=params)
            return
        elif current_step == "ask_ig_p3v2":
            url = f"{BASE_URL_OSINT}/instagram-profile-v3-v2"
            params = {"key": OSINT_KEY, "type": "profile_v2", "username": txt}
            execute_api_call(message, url, "INSTAGRAM PROFILE V3 V2", txt, params=params)
            return
        elif current_step == "ask_ig_stats":
            url = f"{BASE_URL_OSINT}/instagram-stats-v1"
            params = {"key": OSINT_KEY, "type": "stats", "username": txt}
            execute_api_call(message, url, "INSTAGRAM STATS V1", txt, params=params)
            return
        elif current_step == "ask_ig_user":
            url = f"{BASE_URL_OSINT}/instagram-user-v1"
            params = {"key": OSINT_KEY, "type": "user", "username": txt}
            execute_api_call(message, url, "INSTAGRAM USER V1", txt, params=params)
            return

        # Snapchat Hub
        elif current_step == "ask_snap_all":
            url = f"{BASE_URL_OSINT}/snapchat-all"
            params = {"key": OSINT_KEY, "action": "all", "username": txt}
            execute_api_call(message, url, "SNAPCHAT ALL DATA", txt, params=params)
            return
        elif current_step == "ask_snap_high":
            url = f"{BASE_URL_OSINT}/snapchat-highlight"
            params = {"key": OSINT_KEY, "action": "highlights", "username": txt}
            execute_api_call(message, url, "SNAPCHAT HIGHLIGHT", txt, params=params)
            return
        elif current_step == "ask_snap_story":
            url = f"{BASE_URL_OSINT}/snapchat-story"
            params = {"key": OSINT_KEY, "action": "stories", "username": txt}
            execute_api_call(message, url, "SNAPCHAT STORY & MEDIA", txt, params=params)
            return

        # Terabox Hub
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

        # Geo & Network Hub
        elif current_step == "ask_web":
            url = f"{BASE_URL_OSINT}/website-source"
            params = {"key": OSINT_KEY, "url": txt}
            execute_api_call(message, url, "WEBSITE SCRAPER", txt, params=params)
            return
        elif current_step == "ask_ip1":
            url = f"{BASE_URL_OSINT}/ip-v1"
            params = {"key": OSINT_KEY, "query": txt}
            execute_api_call(message, url, "IP INFO V1", txt, params=params)
            return
        elif current_step == "ask_ip2":
            url = f"{BASE_URL_OSINT}/ip-v2"
            params = {"key": OSINT_KEY, "ip": txt}
            execute_api_call(message, url, "IP INFO V2", txt, params=params)
            return
        elif current_step == "ask_ip3":
            url = f"{BASE_URL_OSINT}/ip-v3"
            params = {"key": OSINT_KEY, "ip": txt}
            execute_api_call(message, url, "IP INFO V3", txt, params=params)
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

    # 2. Direct Auto-Routing for Links and Formats
    if is_terabox_link:
        execute_terabox_call(message, None, "TERABOX AUTO-STREAM", txt)
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
    print("👑 CROWN VIP OSINT & 30+ APIS BOT IS ONLINE!")
    keep_alive()
    bot.infinity_polling()
