"""
Парсинг Instagram
1) Написать приложение, которое будет проходиться по указанному списку(делать через ввод input) двух и/или более
пользователей и собирать данные об их подписчиках и подписках.
2) По каждому пользователю, который является подписчиком или на которого подписан исследуемый объект нужно извлечь
имя, id, фото (остальные данные по желанию).
Фото можно дополнительно скачать(необязательно).
3) Собранные данные необходимо сложить в базу данных.
Структуру данных нужно заранее продумать(!), чтобы:
4) Написать функцию, которая будет делать запрос к базе, который вернет
список подписчиков только указанного пользователя
5) Написать функцию, которая будет делать запрос к базе, который вернет
список профилей, на кого подписан указанный пользователь
"""

import scrapy
from scrapy.loader.processors import Compose, TakeFirst


def make_list_users(user_name):
    res = []
    return res.append(user_name)


class InstaparserItem(scrapy.Item):
    _id = scrapy.Field()
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    user_photo = scrapy.Field()
    followers = scrapy.Field(input_processor=Compose(make_list_users))# кто подписан на пользователя
    followings = scrapy.Field(input_processor=Compose(make_list_users))# на кого подписан пользователь
    head_user_name = scrapy.Field()
