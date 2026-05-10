from pymongo import MongoClient
from configs import cfg

client = MongoClient(cfg.MONGO_URI)

users  = client['main']['users']
groups = client['main']['groups']
videos = client['main']['videos']

def already_db(user_id):
    return bool(users.find_one({"user_id": str(user_id)}))

def add_user(user_id):
    if not already_db(user_id):
        users.insert_one({"user_id": str(user_id)})

def remove_user(user_id):
    if already_db(user_id):
        users.delete_one({"user_id": str(user_id)})

def all_users():
    return users.count_documents({})   # fixed: was list(find({})) = loads ALL docs into RAM


def already_dbg(chat_id):
    return bool(groups.find_one({"chat_id": str(chat_id)}))

def add_group(chat_id):
    if not already_dbg(chat_id):
        groups.insert_one({"chat_id": str(chat_id)})

def all_groups():
    return groups.count_documents({})  # fixed: same RAM issue

def add_video(file_id: str):
    if not videos.find_one({"file_id": file_id}):
        videos.insert_one({"file_id": file_id})

def get_random_video() -> str | None:
    count = videos.count_documents({})
    if count == 0:
        return None
    import random
    doc = videos.find().skip(random.randint(0, count - 1)).limit(1)[0]
    return doc["file_id"]