from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import filters, Client, errors
from pyrogram.errors.exceptions.flood_420 import FloodWait
from database import add_user, add_group, all_users, all_groups, users, remove_user, add_video, get_random_video
from configs import cfg
import asyncio

app = Client(
    "reqmedia",
    api_id=cfg.API_ID,
    api_hash=cfg.API_HASH,
    bot_token=cfg.BOT_TOKEN
)

@app.on_message(filters.chat(cfg.DB_CHANNEL) & filters.video)
async def save_video(_, m: Message):
    try:
        add_video(m.video.file_id)
        print(f"[DB] Saved video: {m.video.file_id}")
    except Exception as e:
        print(f"[save_video] {e}")


@app.on_chat_join_request(filters.group | filters.channel)
async def approve(_, m: Message):
    chat = m.chat
    user = m.from_user
    try:
        add_group(chat.id)
        add_user(user.id)

        file_id = get_random_video()
        markup  = InlineKeyboardMarkup(cfg.CUSTOM_BUTTONS) if cfg.CUSTOM_BUTTONS_ENABLED else None
        caption = cfg.WELCOME_CAPTION.format(
            first=user.first_name,
            last=user.last_name or "",
            username=f"@{user.username}" if user.username else "None",
            mention=user.mention,
            id=user.id,
            chat_title=chat.title
        )

        if file_id:
            await app.send_video(user.id, video=file_id, caption=caption, reply_markup=markup)
        else:
            await app.send_message(user.id, caption, reply_markup=markup)

    except errors.PeerIdInvalid:
        print(f"[approve] User {user.id} never started bot -- can't DM")
    except Exception as e:
        print(f"[approve] {e}")


@app.on_message(filters.private & filters.command("start"))
async def start(_, m: Message):
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("Channel", url="https://t.me/telegram"),
        InlineKeyboardButton("Support", url="https://t.me/telegram")
    ]])
    add_user(m.from_user.id)
    await m.reply_text(
        f"Hello {m.from_user.mention}!\n"
        "I am an auto approve join request bot.\n"
        "Add me to your chat and promote me to admin with add members permission.",
        reply_markup=keyboard
    )

@app.on_message(filters.command("stats") & filters.user(cfg.SUDO))
async def stats_command(_, m: Message):
    from database import videos
    
    total_users = all_users()
    total_groups = all_groups()
    total_videos = videos.count_documents({})
    
    await m.reply_text(
        f"**📊 Bot Statistics**\n\n"
        f"**Chat Stats**\n"
        f"👤 Users  : `{total_users}`\n"
        f"👥 Groups : `{total_groups}`\n"
        f"📊 Total  : `{total_users + total_groups}`\n\n"
        f"**Media Stats**\n"
        f"🎬 Saved Videos : `{total_videos}`"
    )

@app.on_message(filters.command("broadcast") & filters.user(cfg.SUDO))
async def broadcast_cmd(_, m: Message):
    if not m.reply_to_message:
        await m.reply_text("Reply to a message to broadcast it.")
        return

    lel = await m.reply_text("Processing broadcast...")
    success = failed = deactivated = blocked = 0

    for doc in users.find():  # assuming 'users' collection is accessible
        uid = int(doc["user_id"])
        try:
            await m.reply_to_message.copy(uid)
            success += 1
        except FloodWait as ex:
            await asyncio.sleep(ex.value)
            try:
                await m.reply_to_message.copy(uid)
                success += 1
            except Exception:
                failed += 1
        except errors.InputUserDeactivated:
            deactivated += 1
            remove_user(doc["user_id"])  # assuming you have this function
        except errors.UserIsBlocked:
            blocked += 1
        except Exception as e:
            print(f"[broadcast] {e}")
            failed += 1

    await lel.edit(
        f"✅ Broadcast completed\n\n"
        f"📨 Sent: {success}\n"
        f"❌ Failed: {failed}\n"
        f"🚫 Blocked: {blocked}\n"
        f"📴 Deactivated: {deactivated}"
    )

print("Bot started!")
app.run()
