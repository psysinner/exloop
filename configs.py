from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

class Config:
    API_ID      = int("your_api_id_here")
    API_HASH    = "your_api_hash_here"
    BOT_TOKEN   = "your_bot_token_here"
    MONGO_URI   = "your_mongodb_uri_here"
    DB_CHANNEL  = -1001234567890
    SUDO        = [123456789]

    CUSTOM_BUTTONS_ENABLED = True

    CUSTOM_BUTTONS = [
        [
            InlineKeyboardButton("Example 1", url="https://t.me/example"),
            InlineKeyboardButton("Example 2", url="https://t.me/example"),
        ],
        [
            InlineKeyboardButton("Example 3", url="https://t.me/example"),
        ],
    ]

    WELCOME_CAPTION = ("**Hello {mention}!\nWelcome To {chat_title}\n\nName : {first} {last}\nID : `{id}`\nusername : {username}\n\n")

cfg = Config()
