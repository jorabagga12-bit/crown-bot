 
import os
import re
import json
import time
import threading
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from flask import Flask

# ================= FLASK SERVER FOR 24/7 HOSTING =================
app = Flask('')

@app.route('/')
def home():
    return "👑 CROWN BOT M4 ULTRA - ONLINE 24/7"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

# ================= CONFIGURATION & CONSTANTS =================
BOT_TOKEN = "8887168683:AAFU5xQN389gI1WSOhEom41FY0I4-fRy3fs"
ADMIN_ID = 8407090614

# API Base Configurations
OSINT_KEY = "demo"
BASE_URL_OSINT = "https://osint-api-delta.vercel.app/api"

DARRIFY_TOKEN = "xpol_Demo_combo_a811c2fb"
BASE_URL_DARRIFY = "https://xpolitesupgrade-api.darrify-api.workers.dev/api"

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

def extract_media_url(data):
    if isinstance(data, str):
        if data.startswith("http") and any(ext in data.lower() for ext in [".mp4", ".mov", "m3u8", ".jpg", ".jpeg", ".png", ".mp3", "video", "stream", "download", "play"]):
            return data
        return None

    if isinstance(data, dict):
        priority_keys = ["video_url", "stream_url", "download_url", "play_url", "media_url", "display_url", "image_url", "audio_url", "direct_link", "url", "link"]
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

# ================= KEYBOARD MENUS =================
def get_reply_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📸 Instagram Suite"),
        KeyboardButton("👻 Snapchat Suite")
    )
    markup.add(
        KeyboardButton("🆔 Phone & Identity Tracker"),
        KeyboardButton("🏦 Bank, PAN & GST Tools")
    )
    markup.add(
        KeyboardButton("🚗 Vehicle Master & RC"),
        KeyboardButton("▶️ YouTube & Terabox DL")
    )
    markup.add(
        KeyboardButton("🌐 IP, Domain & Mail Check"),
        KeyboardButton("🤖 AI & Utility Tools")
    )
    markup.add(
        KeyboardButton("💎 VIP Profile"),
        KeyboardButton("🔙 Main Menu")
    )
    return markup

def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📸 Instagram Suite", callback_data="menu_instagram"),
        InlineKeyboardButton("👻 Snapchat Suite", callback_data="menu_snapchat")
    )
    markup.add(
        InlineKeyboardButton("🆔 Tracker & Identity", callback_data="menu_identity"),
        InlineKeyboardButton("🏦 Finance & GST", callback_data="menu_finance")
    )
    markup.add(
        InlineKeyboardButton("🚗 Vehicle RC & Master", callback_data="menu_vehicle"),
        InlineKeyboardButton("📥 Downloaders (YT/Terabox)", callback_data="menu_download")
    )
    markup.add(
        InlineKeyboardButton("🌐 Network & Mail Tools", callback_data="menu_network"),
        InlineKeyboardButton("🤖 AI & Generator Tools", callback_data="menu_ai")
    )
    markup.add(InlineKeyboardButton("👑 VIP Profile", callback_data="profile"))
    return markup

def instagram_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("⬇️ Reel DL", callback_data="ask_ig_dl"),
        InlineKeyboardButton("📸 Profile V1", callback_data="ask_ig_v1"),
        InlineKeyboardButton("📸 Profile V2", callback_data="ask_ig_v2"),
        InlineKeyboardButton("📸 Profile V3", callback_data="ask_ig_v3"),
        InlineKeyboardButton("🌟 Best Profile V1", callback_data="ask_ig_best"),
        InlineKeyboardButton("🎞️ Media V1", callback_data="ask_ig_media"),
        InlineKeyboardButton("📝 Posts V2", callback_data="ask_ig_posts"),
        InlineKeyboardButton("📊 Account Stats", callback_data="ask_ig_stats"),
        InlineKeyboardButton("🆔 User ID Finder", callback_data="ask_ig_user")
    )
    markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main"))
    return markup

def snapchat_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("👻 Snap All Data", callback_data="ask_snap_all"),
        InlineKeyboardButton("🌟 Snap Highlight", callback_data="ask_snap_high"),
        InlineKeyboardButton("🎞️ Snap Story", callback_data="ask_snap_story")
    )
    markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main"))
    return markup

def identity_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📞 Phone Tracker (New)", callback_data="ask_ph_tracker"),
        InlineKeyboardButton("📞 Truecaller Info", callback_data="ask_tc"),
        InlineKeyboardButton("📄 Aadhaar Info", callback_data="ask_aadhar"),
        InlineKeyboardButton("📧 Email Intelligence", callback_data="ask_email"),
        InlineKeyboardButton("📲 IMEI Details", callback_data="ask_imei")
    )
    markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main"))
    return markup

def finance_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🏦 Bank IFSC Info", callback_data="ask_ifsc"),
        InlineKeyboardButton("📇 PAN Card Search", callback_data="ask_pan"),
        InlineKeyboardButton("🏢 GST Search", callback_data="ask_gst"),
        InlineKeyboardButton("🏢 GST Direct Check", callback_data="ask_gst_direct")
    )
    markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main"))
    return markup

def vehicle_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🚗 Vehicle Master (New)", callback_data="ask_veh_master"),
        InlineKeyboardButton("🔢 Vehicle Number", callback_data="ask_veh_num"),
        InlineKeyboardButton("🏎️ Vehicle RC V1", callback_data="ask_veh_v1"),
        InlineKeyboardButton("🏎️ Vehicle RC V2", callback_data="ask_veh_v2"),
        InlineKeyboardButton("🏎️ Vehicle RC V3", callback_data="ask_veh_v3"),
        InlineKeyboardButton("🏎️ Vehicle RC V4", callback_data="ask_veh_v4")
    )
    markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main"))
    return markup

def download_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("▶️ Terabox Stream V1", callback_data="ask_tb_s1"),
        InlineKeyboardButton("▶️ Terabox Stream V2", callback_data="ask_tb_s2"),
        InlineKeyboardButton("▶️ Terabox Stream V3", callback_data="ask_tb_s3"),
        InlineKeyboardButton("📥 Terabox Video V2", callback_data="ask_tb_v2"),
        InlineKeyboardButton("📄 Terabox File V2", callback_data="ask_tb_file2")
    )
    markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main"))
    return markup

def network_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✉️ Mail Domain Check (New)", callback_data="ask_mail_check"),
        InlineKeyboardButton("📍 IP Info V1", callback_data="ask_ip1"),
        InlineKeyboardButton("📍 IP Info V2", callback_data="ask_ip2"),
        InlineKeyboardButton("📍 IP Info V3", callback_data="ask_ip3"),
        InlineKeyboardButton("📍 Pincode Search", callback_data="ask_pincode"),
        InlineKeyboardButton("💻 Website Source", callback_data="ask_web_source")
    )
    markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main"))
    return markup

def ai_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🎨 AI Image Generator", callback_data="ask_aiimg"),
        InlineKeyboardButton("🎮 BGMI Player Info", callback_data="ask_bgmi"),
        InlineKeyboardButton("🌍 Country Details", callback_data="ask_country"),
        InlineKeyboardButton("☁️ Weather Details", callback_data="ask_weather"),
        InlineKeyboardButton("💬 Telegram User Info", callback_data="ask_tg_info")
    )
    markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main"))
    return markup

# ================= COMMAND HANDLERS =================
@bot.message_handler(commands=["start"])
def start(message):
    get_user(message.from_user.id)
    user_steps[message.from_user.id] = None

    welcome_text = (
        f"👑 <b>Welcome to Crown OSINT Bot</b> 👑\n\n"
        f"<i>All 50+ APIs Integrated with High Speed Fallback.</i>\n"
        f"──────────────────────────────\n"
        f"⚡ <b>Developer:</b> @team_lifexy\n"
        f"✨ <i>Select an option from the menu below:</i>"
    )

    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode="HTML")
    bot.send_message(message.chat.id, "👇 <b>Quick Keyboard Active:</b>", reply_markup=get_reply_keyboard(), parse_mode="HTML")

# ================= CALLBACK ROUTER =================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    
    menus = {
        "menu_main": main_menu(),
        "menu_instagram": instagram_menu(),
        "menu_snapchat": snapchat_menu(),
        "menu_identity": identity_menu(),
        "menu_finance": finance_menu(),
        "menu_vehicle": vehicle_menu(),
        "menu_download": download_menu(),
        "menu_network": network_menu(),
        "menu_ai": ai_menu()
    }

    if call.data in menus:
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=menus[call.data])
        bot.answer_callback_query(call.id)
        return

    if call.data == "profile":
        user = get_user(user_id)
        credits_disp = "♾️ <b>Unlimited (VIP)</b>" if user_id == ADMIN_ID else f"<b>{user['credits']}</b>"
        info_text = (
            f"👑 <b><u>Crown VIP Profile</u></b> 👑\n"
            f"──────────────────────────────\n"
            f"👤 <b>User:</b> <i>{call.from_user.first_name}</i>\n"
            f"💎 <b>Credits:</b> {credits_disp}\n"
            f"🔍 <b>Searches Completed:</b> <b>{user['lookups']}</b>\n"
            f"──────────────────────────────\n"
            f"⚡ <b>Powered By:</b> @team_lifexy"
        )
        bot.send_message(chat_id, info_text, parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return

    prompts = {
        "ask_ph_tracker": "📞 Enter Phone Number to Track:",
        "ask_mail_check": "✉️ Enter Mail Domain (e.g. gmail.com):",
        "ask_veh_master": "🚗 Enter Vehicle RC Number (Vehicle Master):",
        "ask_aadhar": "📄 Enter ID Number for Lookup:",
        
        "ask_ig_dl": "⬇️ Send Instagram Reel / Video URL:",
        "ask_ig_v1": "📸 Enter IG Username (Profile V1):",
        "ask_ig_v2": "📸 Enter IG Username (Profile V2):",
        "ask_ig_v3": "📸 Enter IG Username (Profile V3):",
        "ask_ig_best": "🌟 Enter IG Username (Best Profile V1):",
        "ask_ig_media": "🎞️ Enter IG Username (Media V1):",
        "ask_ig_posts": "📝 Enter IG Username (Posts V2):",
        "ask_ig_stats": "📊 Enter IG Username for Stats:",
        "ask_ig_user": "🆔 Enter IG Username for User ID:",
        
        "ask_snap_all": "👻 Enter Snapchat Username (All Data):",
        "ask_snap_high": "🌟 Enter Snapchat Username (Highlight):",
        "ask_snap_story": "🎞️ Enter Snapchat Username (Story):",
        
        "ask_tc": "📞 Enter 10-Digit Phone Number:",
        "ask_email": "📧 Enter Target Email Address:",
        "ask_imei": "📲 Enter 15-Digit IMEI Number:",
        
        "ask_ifsc": "🏦 Enter 11-Digit Bank IFSC Code:",
        "ask_pan": "📇 Enter 10-Character PAN Number:",
        "ask_gst": "🏢 Enter 15-Digit GSTIN Number:",
        "ask_gst_direct": "🏢 Enter GSTIN for Direct Check:",
        
        "ask_veh_num": "🔢 Enter Vehicle Number:",
        "ask_veh_v1": "🏎️ Enter Vehicle RC Number (V1):",
        "ask_veh_v2": "🏎️ Enter Vehicle RC Number (V2):",
        "ask_veh_v3": "🏎️ Enter Vehicle RC Number (V3):",
        "ask_veh_v4": "🏎️ Enter Vehicle RC Number (V4):",
        
        "ask_tb_s1": "▶️ Send Terabox URL (Stream V1):",
        "ask_tb_s2": "▶️ Send Terabox URL (Stream V2):",
        "ask_tb_s3": "▶️ Send Terabox URL (Stream V3):",
        "ask_tb_v2": "📥 Send Terabox URL (Video V2):",
        "ask_tb_file2": "📄 Send Terabox URL (File V2):",
        
        "ask_ip1": "📍 Enter IP Address (V1):",
        "ask_ip2": "📍 Enter IP Address (V2):",
        "ask_ip3": "📍 Enter IP Address (V3):",
        "ask_pincode": "📍 Enter 6-Digit Indian Pincode:",
        "ask_web_source": "💻 Enter Website URL:",
        
        "ask_aiimg": "🎨 Enter Prompt for AI Image Generator:",
        "ask_bgmi": "🎮 Enter BGMI Player ID:",
        "ask_country": "🌍 Enter Country Name:",
        "ask_weather": "☁️ Enter City Name for Weather:",
        "ask_tg_info": "💬 Enter Telegram User ID:"
    }

    if call.data in prompts:
        user_steps[user_id] = call.data
        bot.send_message(chat_id, f"📝 <b>Input Required:</b>\n{prompts[call.data]}", parse_mode="HTML")
    
    bot.answer_callback_query(call.id)

# ================= EXECUTOR =================
def execute_request(message, endpoint_list, query_label, search_val):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user_id != ADMIN_ID and user["credits"] < 1:
        bot.reply_to(message, "❌ <i>Credits exhausted. Contact @team_lifexy</i>", parse_mode="HTML")
        return

    wait_msg = bot.reply_to(message, f"⚡ <b><i>Fetching Data for {query_label}... Please wait!</i></b>", parse_mode="HTML")

    final_response = None
    media_url = None

    for ep, params in endpoint_list:
        try:
            r = requests.get(ep, params=params, timeout=20)
            if r.status_code == 200:
                try:
                    res = r.json()
                except Exception:
                    continue
                
                if isinstance(res, dict):
                    err_msg = str(res.get("error", "")).lower()
                    if "invalid" in err_msg or "inactive" in err_msg or res.get("success") == False:
                        continue
                
                final_response = res
                media_url = extract_media_url(res)
                if final_response:
                    break
        except Exception:
            continue

    if user_id != ADMIN_ID:
        user["credits"] -= 1

    user["lookups"] += 1
    global total_lookups
    total_lookups += 1
    save_data()

    # Special handling for Terabox / Media Links to give direct Chrome Open / Download buttons
    if "Terabox" in query_label or media_url:
        target_link = media_url if media_url else search_val
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🌐 Open in Chrome", url=target_link),
            InlineKeyboardButton("📥 Download Directly", url=target_link)
        )
        bot.edit_message_text(
            f"👑 <b>Terabox File / Stream Ready!</b> 👑\n"
            f"──────────────────────────────\n"
            f"🔗 <b>Link:</b> <code>{search_val}</code>\n"
            f"──────────────────────────────\n"
            f"✨ <i>Choose an action below to open or download directly:</i>",
            message.chat.id, wait_msg.message_id, reply_markup=markup, parse_mode="HTML"
        )
        return

    if final_response:
        result_str = json.dumps(final_response, indent=2, ensure_ascii=False)
        scrub_targets = [r"(?i)onlyh4ckerzon", r"(?i)onlyhackerzon", r"(?i)rohit", r"(?i)@froxtdevil", r"(?i)optimusprime"]
        for target in scrub_targets:
            result_str = re.sub(target, "Crown 👑", result_str)

        if len(result_str) > 3500:
            result_str = result_str[:3500] + "\n... [Output Truncated]"

        out_msg = (
            f"👑 <b>Crown OSINT Intelligence</b> 👑\n"
            f"──────────────────────────────\n"
            f"🔍 <b>Type:</b> <i>{query_label}</i>\n"
            f"📌 <b>Input:</b> <code>{search_val}</code>\n"
            f"──────────────────────────────\n"
            f"<b>Output Data:</b>\n"
            f"<pre>{result_str}</pre>\n"
            f"──────────────────────────────\n"
            f"⚡ <b>Powered By: @team_lifexy</b>"
        )
        bot.edit_message_text(out_msg, message.chat.id, wait_msg.message_id, parse_mode="HTML")
        auto_delete(message.chat.id, wait_msg.message_id)
    else:
        bot.edit_message_text("❌ <b>API Error:</b> Data not found or API temporarily down. Please try again later.", message.chat.id, wait_msg.message_id, parse_mode="HTML")

# ================= MESSAGE ROUTER =================
@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def handle_text(message):
    txt = message.text.strip()
    user_id = message.from_user.id
    current_step = user_steps.get(user_id)
    user_steps[user_id] = None

    if txt == "📸 Instagram Suite":
        bot.reply_to(message, "👑 <b>Instagram Suite:</b>", reply_markup=instagram_menu(), parse_mode="HTML")
        return
    elif txt == "👻 Snapchat Suite":
        bot.reply_to(message, "👑 <b>Snapchat Suite:</b>", reply_markup=snapchat_menu(), parse_mode="HTML")
        return
    elif txt == "🆔 Phone & Identity Tracker":
        bot.reply_to(message, "👑 <b>Identity Tools:</b>", reply_markup=identity_menu(), parse_mode="HTML")
        return
    elif txt == "🏦 Bank, PAN & GST Tools":
        bot.reply_to(message, "👑 <b>Finance & Tax Tools:</b>", reply_markup=finance_menu(), parse_mode="HTML")
        return
    elif txt == "🚗 Vehicle Master & RC":
        bot.reply_to(message, "👑 <b>Vehicle Information Tools:</b>", reply_markup=vehicle_menu(), parse_mode="HTML")
        return
    elif txt == "▶️ YouTube & Terabox DL":
        bot.reply_to(message, "👑 <b>Media Downloader Suite:</b>", reply_markup=download_menu(), parse_mode="HTML")
        return
    elif txt == "🌐 IP, Domain & Mail Check":
        bot.reply_to(message, "👑 <b>Network & Mail Tools:</b>", reply_markup=network_menu(), parse_mode="HTML")
        return
    elif txt == "🤖 AI & Utility Tools":
        bot.reply_to(message, "👑 <b>AI & Utility Tools:</b>", reply_markup=ai_menu(), parse_mode="HTML")
        return
    elif txt == "💎 VIP Profile":
        user = get_user(user_id)
        bot.reply_to(message, f"👑 <b>Credits:</b> {user['credits']}\n<b>Developer:</b> @team_lifexy", parse_mode="HTML")
        return
    elif txt == "🔙 Main Menu":
        bot.reply_to(message, "👑 <b>Main Control Menu:</b>", reply_markup=main_menu(), parse_mode="HTML")
        return

    if current_step:
        mapping = {
            # New Darrify APIs
            "ask_ph_tracker": ([(f"{BASE_URL_DARRIFY}/ph-tracker", {"token": DARRIFY_TOKEN, "number": txt})], "Phone Tracker"),
            "ask_mail_check": ([(f"{BASE_URL_DARRIFY}/mail-check", {"token": DARRIFY_TOKEN, "domain": txt})], "Mail Check"),
            "ask_veh_master": ([(f"{BASE_URL_DARRIFY}/vehicle-master", {"token": DARRIFY_TOKEN, "rc": txt.upper()})], "Vehicle Master"),
            "ask_aadhar": ([(f"{BASE_URL_DARRIFY}/aadhar-info", {"token": DARRIFY_TOKEN, "id": txt})], "Aadhaar Info"),

            # OSINT Delta APIs
            "ask_ig_dl": ([(f"{BASE_URL_OSINT}/instagram-download", {"key": OSINT_KEY, "type": "download", "url": txt})], "Instagram Download"),
            "ask_ig_v1": ([(f"{BASE_URL_OSINT}/instagram-profile-v1", {"key": OSINT_KEY, "type": "profile", "username": txt})], "Instagram Profile V1"),
            "ask_ig_v2": ([(f"{BASE_URL_OSINT}/instagram-profile-v2", {"key": OSINT_KEY, "type": "profile", "username": txt})], "Instagram Profile V2"),
            "ask_ig_v3": ([(f"{BASE_URL_OSINT}/instagram-profile-v3", {"key": OSINT_KEY, "type": "profile", "username": txt})], "Instagram Profile V3"),
            "ask_ig_best": ([(f"{BASE_URL_OSINT}/instagram-best-v1", {"key": OSINT_KEY, "type": "best", "username": txt})], "Instagram Best V1"),
            "ask_ig_media": ([(f"{BASE_URL_OSINT}/instagram-media-v1", {"key": OSINT_KEY, "type": "media", "username": txt})], "Instagram Media V1"),
            "ask_ig_posts": ([(f"{BASE_URL_OSINT}/instagram-posts-v2", {"key": OSINT_KEY, "type": "posts", "username": txt})], "Instagram Posts V2"),
            "ask_ig_stats": ([(f"{BASE_URL_OSINT}/instagram-stats-v1", {"key": OSINT_KEY, "type": "stats", "username": txt})], "Instagram Stats"),
            "ask_ig_user": ([(f"{BASE_URL_OSINT}/instagram-user-v1", {"key": OSINT_KEY, "type": "user", "username": txt})], "Instagram User ID"),

            "ask_snap_all": ([(f"{BASE_URL_OSINT}/snapchat-all", {"key": OSINT_KEY, "action": "all", "username": txt})], "Snapchat All Data"),
            "ask_snap_high": ([(f"{BASE_URL_OSINT}/snapchat-highlight", {"key": OSINT_KEY, "action": "highlights", "username": txt})], "Snapchat Highlight"),
            "ask_snap_story": ([(f"{BASE_URL_OSINT}/snapchat-story", {"key": OSINT_KEY, "action": "stories", "username": txt})], "Snapchat Story"),

            "ask_tc": ([(f"{BASE_URL_OSINT}/truecaller-info", {"key": OSINT_KEY, "number": txt})], "Truecaller Info"),
            "ask_email": ([(f"{BASE_URL_OSINT}/email-info", {"key": OSINT_KEY, "mail": txt})], "Email Info"),
            "ask_imei": ([(f"{BASE_URL_OSINT}/imei-info", {"key": OSINT_KEY, "imei_number": txt})], "IMEI Info"),

            "ask_ifsc": ([(f"{BASE_URL_OSINT}/ifsc-info", {"key": OSINT_KEY, "ifsc": txt.upper()})], "Bank IFSC Info"),
            "ask_pan": ([(f"{BASE_URL_OSINT}/pan-info", {"key": OSINT_KEY, "pan": txt.upper()})], "PAN Card Info"),
            "ask_gst": ([(f"{BASE_URL_OSINT}/gst-search", {"key": OSINT_KEY, "gstin": txt.upper()})], "GST Search"),
            "ask_gst_direct": ([(f"{BASE_URL_OSINT}/gst-direct", {"key": OSINT_KEY, "gstin": txt.upper()})], "GST Direct Check"),

            "ask_veh_num": ([(f"{BASE_URL_OSINT}/vehicle-number", {"key": OSINT_KEY, "number": txt.upper()})], "Vehicle Number Details"),
            "ask_veh_v1": ([(f"{BASE_URL_OSINT}/vehicle-v1", {"key": OSINT_KEY, "type": "v1", "rc": txt.upper()})], "Vehicle RC V1"),
            "ask_veh_v2": ([(f"{BASE_URL_OSINT}/vehicle-v2", {"key": OSINT_KEY, "type": "v2", "rc": txt.upper()})], "Vehicle RC V2"),
            "ask_veh_v3": ([(f"{BASE_URL_OSINT}/vehicle-v3", {"key": OSINT_KEY, "type": "v3", "rc": txt.upper()})], "Vehicle RC V3"),
            "ask_veh_v4": ([(f"{BASE_URL_OSINT}/vehicle-v4", {"key": OSINT_KEY, "type": "v4", "rc": txt.upper()})], "Vehicle RC V4"),

            "ask_tb_s1": ([(f"{BASE_URL_OSINT}/terabox-stream", {"key": OSINT_KEY, "type": "video_stream", "url": txt})], "Terabox Stream V1"),
            "ask_tb_s2": ([(f"{BASE_URL_OSINT}/terabox-stream-v2", {"key": OSINT_KEY, "type": "video_streamv2", "url": txt})], "Terabox Stream V2"),
            "ask_tb_s3": ([(f"{BASE_URL_OSINT}/terabox-stream-v3", {"key": OSINT_KEY, "type": "video_streamv3", "url": txt})], "Terabox Stream V3"),
            "ask_tb_v2": ([(f"{BASE_URL_OSINT}/terabox-video-v2", {"key": OSINT_KEY, "type": "video_downloadv2", "url": txt})], "Terabox Video V2"),
            "ask_tb_file2": ([(f"{BASE_URL_OSINT}/terabox-file-v2", {"key": OSINT_KEY, "type": "file_downloadv2", "url": txt})], "Terabox File V2"),

            "ask_ip1": ([(f"{BASE_URL_OSINT}/ip-v1", {"key": OSINT_KEY, "query": txt})], "IP Info V1"),
            "ask_ip2": ([(f"{BASE_URL_OSINT}/ip-v2", {"key": OSINT_KEY, "ip": txt})], "IP Info V2"),
            "ask_ip3": ([(f"{BASE_URL_OSINT}/ip-v3", {"key": OSINT_KEY, "ip": txt})], "IP Info V3"),
            "ask_pincode": ([(f"{BASE_URL_OSINT}/pincode-info", {"key": OSINT_KEY, "pincode": txt})], "Pincode Info"),
            "ask_web_source": ([(f"{BASE_URL_OSINT}/website-source", {"key": OSINT_KEY, "url": txt})], "Website Source Scraper"),

            "ask_aiimg": ([(f"{BASE_URL_OSINT}/image-generator", {"key": OSINT_KEY, "prompt": txt})], "AI Image Generator"),
            "ask_bgmi": ([(f"{BASE_URL_OSINT}/bgmi-info", {"key": OSINT_KEY, "user": txt})], "BGMI Player Info"),
            "ask_country": ([(f"{BASE_URL_OSINT}/country-info", {"key": OSINT_KEY, "name": txt})], "Country Info"),
            "ask_weather": ([(f"{BASE_URL_OSINT}/weather-info", {"key": OSINT_KEY, "city": txt})], "Weather Info"),
            "ask_tg_info": ([(f"{BASE_URL_OSINT}/telegram-info", {"key": OSINT_KEY, "tg": txt})], "Telegram User Info")
        }

        if current_step in mapping:
            eps, label = mapping[current_step]
            execute_request(message, eps, label, txt)
            return

    # Direct Pattern Detection
    if re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", txt.upper()):
        execute_request(message, [(f"{BASE_URL_OSINT}/ifsc-info", {"key": OSINT_KEY, "ifsc": txt.upper()})], "Bank IFSC Info", txt.upper())
    elif txt.isdigit() and len(txt) == 6:
        execute_request(message, [(f"{BASE_URL_OSINT}/pincode-info", {"key": OSINT_KEY, "pincode": txt})], "Pincode Info", txt)
    elif txt.isdigit() and len(txt) == 10:
        execute_request(message, [
            (f"{BASE_URL_DARRIFY}/ph-tracker", {"token": DARRIFY_TOKEN, "number": txt}),
            (f"{BASE_URL_OSINT}/truecaller-info", {"key": OSINT_KEY, "number": txt})
        ], "Phone Tracker / Truecaller", txt)
    elif "1024terabox.com" in txt.lower() or "terabox.com" in txt.lower():
        execute_request(message, [(f"{BASE_URL_OSINT}/terabox-stream", {"key": OSINT_KEY, "type": "video_stream", "url": txt})], "Terabox Stream V1", txt)
    else:
        err = bot.reply_to(message, "⚠️ <b>Unrecognized Input!</b> Press /start to view options.", parse_mode="HTML")
        auto_delete(err.chat.id, err.message_id)

# ================= LAUNCH BOT =================
if __name__ == "__main__":
    print("👑 CROWN BOT M4 ULTRA ONLINE - ALL APIs ACTIVE!")
    keep_alive()
    bot.infinity_polling()
