from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

class Config:
    API_ID      = int("21375775")
    API_HASH    = "24a8567a7fa9209f79d4643b191c1ae4"
    BOT_TOKEN   = "8396523207:AAFrxVSkTzsq_bMGYBJj48xBvuMwkBpsvB8"
    MONGO_URI   = "mongodb+srv://exch:exch@cluster0.l4ijigx.mongodb.net/?appName=Cluster0"
    DB_CHANNEL  = -1003781025193
    SUDO        = [8076259467]

    CUSTOM_BUTTONS_ENABLED = True

    CUSTOM_BUTTONS = [
        [
            InlineKeyboardButton("𝐕𝐈𝐏 𝐃𝐄𝐌𝐎", url="https://t.me/+ujfAp7uNmdEzYjMx"),
            InlineKeyboardButton("αυnтчѕ ωσяℓ∂", url="https://t.me/+PTjuwfOIkLxlMjA9"),
        ],
        [
            InlineKeyboardButton("Aᴘᴘʀᴏᴠᴇ Mᴇ ✅", url="https://t.me/ThundExBot?start=start"),
        ],
    ]

    WELCOME_CAPTION = ("**Hello {mention}!\nWelcome To {chat_title}\n\nName : {first} {last}\nID : `{id}`\nusername : {username}\n\n[{chat_title}](YOUR_GROUP_LINK)\n[{chat_title}](YOUR_GROUP_LINK)\n[{chat_title}](YOUR_GROUP_LINK)")

cfg = Config()
