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
    <html lang="hi">
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
            <h1>👑 क्राउन बोट M4</h1>
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

# ================= CLEAN & POWERFUL REPLIES (GRID BOXES) =================
def get_reply_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📧 ईमेल इंफो (Email Info)"),
        KeyboardButton("🚗 व्हीकल इंफो & RC")
    )
    markup.add(
        KeyboardButton("📸 इंस्टाग्राम हब"),
        KeyboardButton("👻 स्नैपचैट टूल्स")
    )
    markup.add(
        KeyboardButton("📦 टेराबॉक्स प्लेयर"),
        KeyboardButton("🌐 नेटवर्क व IP खोज")
    )
    markup.add(
        KeyboardButton("💎 मेरे क्रेडिट्स"),
        KeyboardButton("🔙 मुख्य मेनू")
    )
    return markup

# ================= CLEAN INLINE MENUS (WITHOUT REPETITIVE VERSION NAMES) =================
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🪪 पहचान व सरकारी सेवाएं", callback_data="menu_identity"),
        InlineKeyboardButton("📸 इंस्टाग्राम टूलकिट", callback_data="menu_instagram")
    )
    markup.add(
        InlineKeyboardButton("👻 स्नैपचैट टूलकिट", callback_data="menu_snapchat"),
        InlineKeyboardButton("📦 टेराबॉक्स प्लेयर 🎬", callback_data="menu_terabox")
    )
    markup.add(
        InlineKeyboardButton("🌐 वेबसाइट व IP नेटवर्क", callback_data="menu_geo"),
        InlineKeyboardButton("🤖 AI व अन्य सुविधाएं", callback_data="menu_ai")
    )
    markup.add(InlineKeyboardButton("💎 मेरी प्रोफाइल (VIP)", callback_data="profile"))
    return markup

def identity_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📧 ईमेल इंफो lookup", callback_data="ask_email_info"),
        InlineKeyboardButton("🚗 व्हीकल इंफो & RC डिटेल्स", callback_data="ask_vehicle")
    )
    markup.add(
        InlineKeyboardButton("📱 फोन नंबर इंफो", callback_data="ask_phone"),
        InlineKeyboardButton("📞 ट्रूकॉलर सर्च", callback_data="ask_truecaller")
    )
    markup.add(
        InlineKeyboardButton("🪪 आधार इंफो", callback_data="ask_aadhar"),
        InlineKeyboardButton("📇 पैन कार्ड डिटेल्स", callback_data="ask_pan")
    )
    markup.add(
        InlineKeyboardButton("🏢 GST सर्च", callback_data="ask_gst"),
        InlineKeyboardButton("🏦 बैंक IFSC कोड", callback_data="ask_ifsc")
    )
    markup.add(
        InlineKeyboardButton("📱 IMEI नंबर जांच", callback_data="ask_imei"),
        InlineKeyboardButton("🔙 मुख्य मेनू", callback_data="menu_main")
    )
    return markup

def instagram_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("👤 प्रोफाइल सर्च (सर्वश्रेष्ठ)", callback_data="ask_ig_best"),
        InlineKeyboardButton("⬇️ रील / पोस्ट डाउनलोड", callback_data="ask_ig_dl")
    )
    markup.add(
        InlineKeyboardButton("📸 मीडिया व फोटोज़", callback_data="ask_ig_media"),
        InlineKeyboardButton("📝 हाल की पोस्ट्स", callback_data="ask_ig_posts")
    )
    markup.add(
        InlineKeyboardButton("📂 संपूर्ण डेटा डाउनलोड", callback_data="ask_ig_downloads"),
        InlineKeyboardButton("📊 अकाउंट स्टेट्स", callback_data="ask_ig_stats")
    )
    markup.add(InlineKeyboardButton("🔙 मुख्य मेनू", callback_data="menu_main"))
    return markup

def snapchat_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("👻 स्नैपचैट प्रोफाइल व ऑल डेटा", callback_data="ask_snap_all"),
        InlineKeyboardButton("🌟 स्नैपचैट हाइलाइट्स", callback_data="ask_snap_high")
    )
    markup.add(
        InlineKeyboardButton("🎞️ स्नैपचैट स्टोरी (वीडियो डाउनलोड)", callback_data="ask_snap_story"),
        InlineKeyboardButton("🔙 मुख्य मेनू", callback_data="menu_main")
    )
    return markup

def terabox_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🎬 डायरेक्ट वीडियो स्ट्रीम", callback_data="ask_tb_s1"),
        InlineKeyboardButton("📥 फास्ट वीडियो डाउनलोड", callback_data="ask_tb_v2")
    )
    markup.add(InlineKeyboardButton("🔙 मुख्य मेनू", callback_data="menu_main"))
    return markup

def geo_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🌐 वेबसाइट स्क्रैपर", callback_data="ask_web"),
        InlineKeyboardButton("📍 IP एड्रेस इंफो", callback_data="ask_ip1")
    )
    markup.add(
        InlineKeyboardButton("📮 पिनकोड इंफो", callback_data="ask_pin"),
        InlineKeyboardButton("🇮🇳 देश की जानकारी (Country)", callback_data="ask_country")
    )
    markup.add(
        InlineKeyboardButton("🌤️ मौसम की जानकारी", callback_data="ask_weather"),
        InlineKeyboardButton("💻 गिटहब (GitHub) सर्च", callback_data="ask_github")
    )
    markup.add(InlineKeyboardButton("🔙 मुख्य मेनू", callback_data="menu_main"))
    return markup

def ai_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💖 AI चैट असिस्टेंट", callback_data="ask_aigf"),
        InlineKeyboardButton("🎨 AI इमेज जनरेटर", callback_data="ask_aiimg")
    )
    markup.add(
        InlineKeyboardButton("✨ इमेज प्रॉमप्ट जनरेटर", callback_data="ask_promptgen"),
        InlineKeyboardButton("🎮 BGMI प्लेयर इंफो", callback_data="ask_bgmi")
    )
    markup.add(InlineKeyboardButton("🔙 मुख्य मेनू", callback_data="menu_main"))
    return markup

# ================= START COMMAND (HINDI CLEAN WELCOME) =================
@bot.message_handler(commands=["start"])
def start(message):
    get_user(message.from_user.id)
    user_steps[message.from_user.id] = None 

    welcome_text = (
        f"<b>वेलकम टू क्राउन बोट 👑 M4 आपका स्वागत करते हैं!</b>\n\n"
        f"<i>नीचे दिए गए किसी भी बटन पर क्लिक करके इस्तेमाल करें:</i>\n"
        f"──────────────────────\n"
        f"⚡ <b>रिसर्च व हेल्प:</b> @team_lifexy"
    )

    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode="HTML")
    bot.send_message(message.chat.id, "👇 <b>त्वरित मेनू (Quick Keyboard):</b>", reply_markup=get_reply_keyboard(), parse_mode="HTML")

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
            f"👑 <b><u>क्राउन प्रोफाइल M4</u></b> 👑\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>यूज़र:</b> <i>{call.from_user.first_name}</i>\n"
            f"💎 <b>क्रेडिट्स:</b> {credits_display}\n"
            f"🔍 <b>कुल खोज:</b> <b>{user['lookups']}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⚡ <b>Developer:</b> @team_lifexy"
        )
        bot.send_message(chat_id, info_text, parse_mode="HTML")

    else:
        prompts = {
            "ask_email_info": "📧 <b>ईमेल दर्ज करें:</b> (उदा. test@gmail.com)",
            "ask_vehicle": "🚗 <b>गाड़ी/व्हीकल नंबर दर्ज करें:</b> (उदा. MH12DE1433)",
            "ask_phone": "📱 <b>10 अंकों का फोन नंबर दर्ज करें:</b>",
            "ask_truecaller": "📞 <b>ट्रूकॉलर जांच के लिए नंबर दर्ज करें:</b>",
            "ask_aadhar": "🪪 <b>12 अंकों का आधार नंबर दर्ज करें:</b>",
            "ask_pan": "📇 <b>10 अक्षरों का पैन कार्ड नंबर दर्ज करें:</b>",
            "ask_gst": "🏢 <b>15 अक्षरों का GSTIN नंबर दर्ज करें:</b>",
            "ask_ifsc": "🏦 <b>बैंक का IFSC कोड दर्ज करें:</b>",
            "ask_imei": "📱 <b>15 अंकों का IMEI नंबर दर्ज करें:</b>",
            
            # Instagram
            "ask_ig_best": "🏆 <b>इंस्टाग्राम यूज़रनेम दर्ज करें:</b>",
            "ask_ig_dl": "⬇️ <b>इंस्टाग्राम रील या पोस्ट का लिंक भेजें:</b>",
            "ask_ig_media": "🎬 <b>इंस्टाग्राम यूज़रनेम (मीडिया जांच) दर्ज करें:</b>",
            "ask_ig_posts": "📝 <b>इंस्टाग्राम पोस्ट्स जांच के लिए यूज़रनेम भेजें:</b>",
            "ask_ig_downloads": "📂 <b>डाउनलोड के लिए यूज़रनेम दर्ज करें:</b>",
            "ask_ig_stats": "📊 <b>अकाउंट स्टेट्स के लिए यूज़रनेम भेजें:</b>",
            
            # Snapchat
            "ask_snap_all": "👻 <b>स्नैपचैट यूज़रनेम दर्ज करें:</b>",
            "ask_snap_high": "🌟 <b>स्नैपचैट हाइलाइट के लिए यूज़रनेम दर्ज करें:</b>",
            "ask_snap_story": "🎞️ <b>स्नैपचैट स्टोरी/वीडियो डाउनलोड के लिए यूज़रनेम भेजें:</b>",
            
            # Terabox
            "ask_tb_s1": "🎬 <b>टेराबॉक्स वीडियो लिंक भेजें:</b>",
            "ask_tb_v2": "📥 <b>डाउनलोड के लिए टेराबॉक्स लिंक भेजें:</b>",
            
            # Geo & Utilities
            "ask_web": "🌐 <b>वेबसाइट का पूरा URL भेजें:</b>",
            "ask_ip1": "🌐 <b>IP एड्रेस दर्ज करें:</b>",
            "ask_pin": "📍 <b>6 अंकों का पिनकोड दर्ज करें:</b>",
            "ask_country": "🇮🇳 <b>देश का नाम दर्ज करें (उदा. india):</b>",
            "ask_weather": "🌤️ <b>शहर का नाम दर्ज करें:</b>",
            "ask_github": "💻 <b>गिटहब यूज़रनेम या क्वेरी भेजें:</b>",
            
            # AI & Games
            "ask_aigf": "💖 <b>AI चैट के लिए कोई भी सवाल लिखें:</b>",
            "ask_aiimg": "🎨 <b>इमेज बनाने के लिए प्रॉमप्ट लिखें:</b>",
            "ask_promptgen": "✨ <b>इमेज का URL भेजें:</b>",
            "ask_bgmi": "🎮 <b>BGMI प्लेयर आईडी (Character ID) दर्ज करें:</b>"
        }
        
        if call.data in prompts:
            user_steps[user_id] = call.data
            bot.send_message(chat_id, f"👑 <b>इनपुट की आवश्यकता है:</b>\n{prompts[call.data]}", parse_mode="HTML")

    bot.answer_callback_query(call.id)

# ================= TERABOX ENGINE =================
def execute_terabox_call(message, search_val):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user_id != ADMIN_ID and user["credits"] < 1:
        bot.reply_to(message, "❌ <i>पर्याप्त क्रेडिट नहीं हैं!</i>", parse_mode="HTML")
        return

    wait_msg = bot.reply_to(message, "🎬🍿 <b><i>वीडियो लोड हो रहा है, कृपया प्रतीक्षा करें...</i></b>", parse_mode="HTML")
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
            InlineKeyboardButton("▶️ अभी वीडियो देखें (WATCH NOW)", url=stream_link),
            InlineKeyboardButton("📥 डायरेक्ट डाउनलोड करें", url=stream_link)
        )
        
        caption = (
            f"👑 <b>क्राउन टेराबॉक्स प्लेयर M4</b> 👑\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎬 <b>स्टेटस:</b> <i>वीडियो स्ट्रीम तैयार है!</i>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👇 <b>नीचे बटन पर क्लिक करके वीडियो चलाएं:</b>"
        )
        bot.edit_message_text(caption, message.chat.id, wait_msg.message_id, reply_markup=markup, parse_mode="HTML")
        auto_delete(message.chat.id, wait_msg.message_id)
    else:
        bot.edit_message_text("❌ <b>वीडियो लोड करने में असमर्थ।</b> कृपया दूसरा लिंक आज़माएं।", message.chat.id, wait_msg.message_id, parse_mode="HTML")

# ================= STANDARD API ENGINE WITH MEDIA BUTTON DETECTOR =================
def execute_api_call(message, endpoint_url, query_label, search_val, params=None):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user_id != ADMIN_ID and user["credits"] < 1:
        bot.reply_to(message, "❌ <i>क्रेडिट समाप्त हो गए हैं। contact @team_lifexy</i>", parse_mode="HTML")
        return

    wait_msg = bot.reply_to(message, "👑📡 <b><i>डेटा प्राप्त किया जा रहा है...</i></b>", parse_mode="HTML")

    try:
        r = requests.get(endpoint_url, params=params, timeout=25)
        
        if r.status_code == 404:
            bot.edit_message_text("⚠️ <b>त्रुटि (404):</b> डेटा प्राप्त नहीं हुआ।", message.chat.id, wait_msg.message_id, parse_mode="HTML")
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
👑 <b>क्राउन इंटेल रिजल्ट (CROWN M4)</b> 👑
━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 <b>सेवा:</b> <i>{query_label}</i>
📌 <b>इनपुट:</b> <code>{search_val}</code>
━━━━━━━━━━━━━━━━━━━━━━━━━━
<b><u>परिणाम (DATA OUTPUT):</u></b>
<pre>{result_json}</pre>
━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ <b>Power: @team_lifexy</b>
"""
        markup = None
        if media_link:
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("▶️ डायरेक्ट वीडियो/मीडिया देखें", url=media_link),
                InlineKeyboardButton("📥 फाइल डाउनलोड करें", url=media_link)
            )

        bot.edit_message_text(text, message.chat.id, wait_msg.message_id, reply_markup=markup, parse_mode="HTML")
        auto_delete(message.chat.id, wait_msg.message_id)

    except Exception:
        bot.edit_message_text("❌ <b>सिस्टम त्रुटि:</b> समय सीमा समाप्त या API प्रतिक्रिया उपलब्ध नहीं है।", message.chat.id, wait_msg.message_id, parse_mode="HTML")

# ================= SMART QUERY ROUTER =================
@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def handle_queries(message):
    txt = message.text.strip()
    user_id = message.from_user.id

    # 0. Quick Buttons Handlers
    if txt == "📧 ईमेल इंफो (Email Info)":
        user_steps[user_id] = "ask_email_info"
        bot.reply_to(message, "👑 <b>ईमेल दर्ज करें:</b>\n<i>(उदा. test@gmail.com)</i>", parse_mode="HTML")
        return
    elif txt == "🚗 व्हीकल इंफो & RC":
        user_steps[user_id] = "ask_vehicle"
        bot.reply_to(message, "👑 <b>गाड़ी का नंबर दर्ज करें:</b>\n<i>(उदा. MH12DE1433)</i>", parse_mode="HTML")
        return
    elif txt == "📦 टेराबॉक्स प्लेयर":
        bot.reply_to(message, "👑 <b>टेराबॉक्स मेनू:</b>", reply_markup=terabox_menu(), parse_mode="HTML")
        return
    elif txt == "📸 इंस्टाग्राम हब":
        bot.reply_to(message, "👑 <b>इंस्टाग्राम मेनू:</b>", reply_markup=instagram_menu(), parse_mode="HTML")
        return
    elif txt == "👻 स्नैपचैट टूल्स":
        bot.reply_to(message, "👑 <b>स्नैपचैट मेनू:</b>", reply_markup=snapchat_menu(), parse_mode="HTML")
        return
    elif txt == "🌐 नेटवर्क व IP खोज":
        bot.reply_to(message, "👑 <b>नेटवर्क मेनू:</b>", reply_markup=geo_menu(), parse_mode="HTML")
        return
    elif txt == "💎 मेरे क्रेडिट्स":
        user = get_user(user_id)
        bot.reply_to(message, f"👑 <b>आपके क्रेडिट्स:</b> {user['credits']}\n<b>हेल्प:</b> @team_lifexy", parse_mode="HTML")
        return
    elif txt == "🔙 मुख्य मेनू":
        bot.reply_to(message, "👑 <b>मुख्य मेनू:</b>", reply_markup=main_menu(), parse_mode="HTML")
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
        msg = bot.reply_to(message, "❌ <b>अमान्य इनपुट!</b>\n<i>कृपया /start दबाकर मेनू से विकल्प चुनें।</i>", parse_mode="HTML")
        auto_delete(msg.chat.id, msg.message_id)

# ================= RUN SERVER =================
if __name__ == "__main__":
    print("👑 CROWN BOT M4 IS ONLINE!")
    keep_alive()
    bot.infinity_polling()
