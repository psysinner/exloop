from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import filters, Client, errors
from pyrogram.errors.exceptions.flood_420 import FloodWait
import asyncio
import logging
from database import (
    add_user, add_group, all_users, all_groups,
    remove_user, add_video, get_random_video, users, videos
)
from configs import cfg

# ====================== LOGGING ======================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Client(
    "reqmedia",
    api_id=cfg.API_ID,
    api_hash=cfg.API_HASH,
    bot_token=cfg.BOT_TOKEN
)

# ====================== SAVE VIDEO ======================
@app.on_message(filters.chat(cfg.DB_CHANNEL) & filters.video)
async def save_video(_, m: Message):
    try:
        add_video(m.video.file_id)
        logger.info(f"[DB] Saved video: {m.video.file_id}")
    except Exception as e:
        logger.error(f"[save_video] {e}")

# ====================== AUTO APPROVE (FIXED) ======================
@app.on_chat_join_request(filters.group | filters.channel)
async def approve(_, m: Message):
    chat = m.chat
    user = m.from_user

    try:
        add_group(chat.id)
        add_user(user.id)

        file_id = get_random_video()
        markup = InlineKeyboardMarkup(cfg.CUSTOM_BUTTONS) if cfg.CUSTOM_BUTTONS_ENABLED else None

        # ================= SAFE CAPTION FORMATTING =================
        try:
            caption = cfg.WELCOME_CAPTION.format(
                first=user.first_name or "",
                last=user.last_name or "",
                username=f"@{user.username}" if user.username else "None",
                mention=user.mention,
                id=user.id,
                chat_title=chat.title or "Unknown Chat"
            )
        except Exception as fmt_err:
            logger.error(f"[approve] WELCOME_CAPTION format error: {fmt_err}")
            # Fallback caption
            caption = f"👋 Hello {user.mention}!\nWelcome to **{chat.title or 'Our Group'}**"

        # Send welcome message
        if file_id:
            await app.send_video(
                user.id, 
                video=file_id, 
                caption=caption, 
                reply_markup=markup
            )
        else:
            await app.send_message(user.id, caption, reply_markup=markup)

        logger.info(f"✅ Approved join request | User: {user.id} | Chat: {chat.id}")

    except errors.PeerIdInvalid:
        logger.warning(f"User {user.id} never started the bot")
    except errors.UserIsBlocked:
        logger.warning(f"User {user.id} blocked the bot")
    except Exception as e:
        logger.error(f"[approve] Critical error for user {user.id}: {e}", exc_info=True)


# ====================== START COMMAND ======================
@app.on_message(filters.private & filters.command("start"))
async def start(_, m: Message):
    bot = await app.get_me()
   
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me To Your Group", url=f"https://t.me/{bot.username}?startgroup=true")],
        [
            InlineKeyboardButton("𝐓𝐇𝐔𝐍𝐃𝐔 𝐏𝐋𝐀𝐂𝐄", url="https://t.me/+vesZeXROYnc2MjU1"),
            InlineKeyboardButton("𝐏α𝗋αᑯ𝗂𝗌𝖾 𝚰𝗌ᥣα𐓣ᑯ", url="https://t.me/+mZAQAdr3BpZjZTNk")
        ],
        [
            InlineKeyboardButton("💞 കഴപ്പി ഗ്രാമം 💞", url="https://t.me/+bY3Gxr1la4tiMzNl"),
            InlineKeyboardButton("🍭 രതിമധുരം 🍬", url="https://t.me/+ispV_nJ6cKE0NWM9")
        ],
        [InlineKeyboardButton("Aᴘᴘʀᴏᴠᴇ Mᴇ ✅", url="https://t.me/ThundExBot?start=start")]
    ])

    add_user(m.from_user.id)

    await m.reply_text(
        f"👋 **Hello {m.from_user.mention}!**\n\n"
        f"**🌸 𝐇ᴀᴠᴇ 𝐀 𝐆ᴏᴏᴅ 𝐃ᴀʏ 🥀**\n\n"
        " •◈•\n"
        "° 𝗥𝘂𝗹𝗲𝘀 :- 👻🧞 🔞🔥🧙‍♂️കേരളത്തിലെ ഏറ്റവും വലിയ കുത്ത് ഗ്രൂപ്പ്‌\n\n"
        "🔥🧙‍♂️🔞ദിവസവും 1000കണക്കിന് വീഡിയോസ് ഫോട്ടോസ് വരുന്ന ഗ്രൂപ്പ് ആണ് ഇത്\n\n"
        "✊💦ലിങ്ക് വഴി കയറി വന്നാൽ നിങ്ങളുടെ കയ് വശം ഉള്ള വീഡിയോസ് ഗ്രൂപ്പിൽ ഇടുക\n\n"
        "⚔️☠️❌. 𝗪𝗮𝗿𝗻𝗶𝗻𝗴 𝗡𝗼𝘁𝗶𝗰𝗲. ❌ ☠️ ⚔️\n"
        "═══❖•ೋ° ★ °ೋ•❖═══\n\n"
        "👉 താഴെ കാണുന്ന G1 G2 ഗ്രൂപ്പുകളിൽ REQUEST അയക്കുക 🔗\n"
        "👉 Approval ആവശ്യമില്ല ✅\n"
        "👉 Request അയച്ച ശേഷം RECHECK ചെയ്യുക 🔁\n\n"
        "⚠️ NOTE: ഇത് JOIN REQUEST ഗ്രൂപ്പാണ്.\n"
        "✅ Request അയച്ചാൽ മതി (Admin approve ആവശ്യമില്ല)!\n",
        reply_markup=keyboard,
        disable_web_page_preview=True
    )


# ====================== STATS ======================
@app.on_message(filters.command("stats") & filters.user(cfg.SUDO))
async def stats_command(_, m: Message):
    total_users = all_users()
    total_groups = all_groups()
    total_videos = videos.count_documents({})
    await m.reply_text(
        f"**📊 Bot Statistics**\n\n"
        f"**Chat Stats**\n"
        f"👤 Users : `{total_users}`\n"
        f"👥 Groups : `{total_groups}`\n"
        f"📊 Total : `{total_users + total_groups}`\n\n"
        f"**Media Stats**\n"
        f"🎬 Saved Videos : `{total_videos}`"
    )


# ====================== BROADCAST ======================
@app.on_message(filters.command("broadcast") & filters.user(cfg.SUDO))
async def broadcast_cmd(_, m: Message):
    if not m.reply_to_message:
        return await m.reply_text("Please reply to a message to broadcast.")

    lel = await m.reply_text("Broadcast started...")
    success = failed = deactivated = blocked = 0

    for doc in users.find():
        uid = int(doc["user_id"])
        try:
            await m.reply_to_message.copy(uid)
            success += 1
            await asyncio.sleep(0.1)
        except FloodWait as ex:
            await asyncio.sleep(ex.value + 1)
            try:
                await m.reply_to_message.copy(uid)
                success += 1
            except Exception:
                failed += 1
        except errors.InputUserDeactivated:
            deactivated += 1
            remove_user(uid)
        except errors.UserIsBlocked:
            blocked += 1
            remove_user(uid)
        except Exception as e:
            logger.error(f"[broadcast] User {uid}: {e}")
            failed += 1

    await lel.edit_text(
        f"✅ **Broadcast Completed**\n\n"
        f"📨 Sent: `{success}`\n"
        f"❌ Failed: `{failed}`\n"
        f"🚫 Blocked: `{blocked}`\n"
        f"📴 Deactivated: `{deactivated}`"
    )


print("Bot started successfully!")
app.run()
