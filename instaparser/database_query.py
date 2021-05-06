"""
4) Написать функцию, которая будет делать запрос к базе, который вернет
список подписчиков только указанного пользователя
5) Написать функцию, которая будет делать запрос к базе, который вернет
список профилей, на кого подписан указанный пользователь
"""
from pprint import pprint
from pymongo import MongoClient


MONGO_URL = "127.0.0.1:27017"
MONGO_DB = "Instagram"

client = MongoClient(MONGO_URL)
db = client[MONGO_DB]
collection = db["instagram"]


def get_user_followers(db_collection, user_name):
    followers = []
    res = db_collection.find({"$and": [{"head_user_name": "elena_30287"}, {"followers": {"$exists": "true"}}]})
    for item in res:
        followers.append(item["user_name"])
    print(f"Количество подписчиков пользователя {user_name}: {len(followers)}")
    return followers


def get_user_followings(db_collection, user_name):
    followings = []
    res = db_collection.find({"$and": [{"head_user_name": "elena_30287"}, {"followings": {"$exists": "true"}}]})
    for item in res:
        followings.append(item["user_name"])
    print(f"Количество профилей, на которые подписан пользователь {user_name}: {len(followings)}")
    return followings


if __name__ == '__main__':
    user = "elena_30287"

    pprint(get_user_followers(collection, user))
    print()
    print()
    pprint(get_user_followings(collection, user))
