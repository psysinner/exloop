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

@app.on_callback_query(filters.regex("chk"))
async def chk(_, cb: CallbackQuery):
    try:
        await app.get_chat_member(cfg.CHANNEL_ID, cb.from_user.id)
    except errors.UserNotParticipant:
        await cb.answer("Not requested. Request then try again.", show_alert=True)
        return
    except Exception as e:
        print(f"[chk] {e}")
        return

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("Channel", url="https://t.me/telegram"),
        InlineKeyboardButton("Support", url="https://t.me/telegram")
    ]])
    add_user(cb.from_user.id)
    await cb.edit_message_text(
        f"Hello {cb.from_user.mention}!\n"
        "I am an auto approve join request bot.\n"
        "Add me to your chat and promote me to admin with add members permission.",
        reply_markup=keyboard
    )


@app.on_message(filters.command("users") & filters.user(cfg.SUDO))
async def dbtool(_, m: Message):
    await m.reply_text(
        f"Chat Stats\n"
        f"Users  : {all_users()}\n"
        f"Groups : {all_groups()}\n"
        f"Total  : {all_users() + all_groups()}"
    )

@app.on_message(filters.command("media") & filters.user(cfg.SUDO))
async def media_count(_, m: Message):
    from database import videos
    await m.reply_text(f"**Saved Videos : `{videos.count_documents({})}`**")


async def _broadcast(m: Message, method: str):
    lel = await m.reply_text("Processing...")
    success = failed = deactivated = blocked = 0

    for doc in users.find():
        uid = int(doc["user_id"])
        try:
            if method == "copy":
                await m.reply_to_message.copy(uid)
            else:
                await m.reply_to_message.forward(uid)
            success += 1
        except FloodWait as ex:
            await asyncio.sleep(ex.value)
            try:
                if method == "copy":
                    await m.reply_to_message.copy(uid)
                else:
                    await m.reply_to_message.forward(uid)
                success += 1
            except Exception:
                failed += 1
        except errors.InputUserDeactivated:
            deactivated += 1
            remove_user(doc["user_id"])
        except errors.UserIsBlocked:
            blocked += 1
        except Exception as e:
            print(f"[broadcast] {e}")
            failed += 1

    await lel.edit(
        f"Sent: {success}\n"
        f"Failed: {failed}\n"
        f"Blocked: {blocked}\n"
        f"Deactivated: {deactivated}"
    )


@app.on_message(filters.command("bcast") & filters.user(cfg.SUDO))
async def bcast(_, m: Message):
    await _broadcast(m, "copy")


@app.on_message(filters.command("fcast") & filters.user(cfg.SUDO))
async def fcast(_, m: Message):
    await _broadcast(m, "forward")

print("Bot started!")
app.run()