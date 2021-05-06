import scrapy
from scrapy.http import HtmlResponse
import re
import json
from urllib.parse import quote
from copy import deepcopy
from instaparser.items import InstaparserItem
from pprint import pprint


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    login_url = "https://www.instagram.com/accounts/login/ajax/"

    username = "karinkaparser"
    enc_password = "#PWD_INSTAGRAM_BROWSER:10:1620211072:Aa5QAMlShUyfx6LoqVbqr3AAkolOt355vdV8VVa/QwzJrJZuCqAktQbiKL0FR3uJa8s8Bdhxz7j9jPHAil6yL2UAVfO8dr9waTl8T0g01Y2kEiduf77nVUZUm7/DSioz5J7QBTIeYSoW2Q=="

    user_to_parse_url_template = "/%s"
    graphql_url = "https://www.instagram.com/graphql/query/?"

    variables_follow = ['followers', 'followings']
    follow_variables = {
        "first": 24,
        "id": "389801252"
    }
    follow_hash = {'followers': "5aefa9893005572d237da5068082d8d5",
                   'followings': "3dec7e2c57367ef3da3d987d89f9dbc8"}


    def __init__(self, search):
        super(InstagramSpider, self).__init__()
        self.user_followers_parse = None
        self.users_to_parse = search


    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.login_url,
            method="POST",
            callback=self.user_loging,
            formdata={
                "username": self.username,
                "enc_password": self.enc_password
            },
            headers={
                "x-csrftoken": csrf_token
            }
        )

    def user_loging(self, response: HtmlResponse):
        print(f"Залогинились! Вход под {self.username}")
        data = response.json()
        if data['authenticated']:
            for user in self.users_to_parse:
                print(f"Переходим на страницу пользователя {user} из введенного списка {self.users_to_parse}")
                yield response.follow(
                    self.user_to_parse_url_template % user,
                    callback=self.user_data_parse,
                    cb_kwargs={
                        "username": user,
                    }
                )

    def make_str_variables(self, variables):
        str_variables = quote(
            str(variables).replace(" ", "").replace("'", '"')
        )
        return str_variables

    def user_data_parse(self, response: HtmlResponse, username):
        print(f"Получаем информацию по пользователю {username}, user_data_parse")
        user_id = self.fetch_user_id(response.text, username)
        self.follow_variables['id'] = user_id
        variables = deepcopy(self.follow_variables)
        str_variables = self.make_str_variables(variables)
        for i, f_hash in enumerate(self.variables_follow):
            print(f"{f_hash}, {i}")
            url = f"{self.graphql_url}query_hash={self.follow_hash[f_hash]}&variables={str_variables}"
            yield response.follow(
                url,
                callback=self.user_follow_parse,
                cb_kwargs={
                    "username": username,
                    "variables": deepcopy(variables),
                    "options": i
                }
            )

    def user_follow_parse(self, response: HtmlResponse, username, variables, options):
        """
        Сбор информации о пользователях, которые подписаны / на которых подписан пользователь
        из стартового списка пользователей
        :param response:
        :param username: имя пользователя, из стартового списка пользователей
        :param variables:
        :param options: принимает значения 0 - если собираем информацию о 'followers', 1 - если о 'followings'
        :return: item с информацией пользователях {имя, id, фото}
        """
        print(f"user_follow_parse: {username}, {variables}, {options}")
        data = response.json()
        with open(f'{username}_{options}.json', 'w', encoding='utf-8') as write_f:
            print("Сохраняем файл")
            json.dump(data, write_f)

        try:
            if options == 0:
                info = data["data"]["user"]["edge_followed_by"]
                pprint(info)
            elif options == 1:
                info = data["data"]["user"]["edge_follow"]
                pprint(info)
            following = info["edges"]
            for follow in following:
                item = InstaparserItem()
                node = follow["node"]
                item["user_id"] = node["id"]
                item["user_name"] = node["username"]
                item["user_photo"] = node["profile_pic_url"]
                item[self.variables_follow[options]] = variables["id"]
                item["head_user_name"] = username
                yield item
        except Exception as e:
            print(e)

        page_info = info["page_info"]
        if page_info["has_next_page"]:
            variables["after"] = page_info["end_cursor"]
            str_variables = self.make_str_variables(variables)
            url = f"{self.graphql_url}query_hash={self.follow_hash[self.variables_follow[options]]}&variables={str_variables}"
            yield response.follow(
                url,
                callback=self.user_follow_parse,
                cb_kwargs={
                    "username": username,
                    "variables": deepcopy(variables),
                    "options": options
                }
            )


    def fetch_csrf_token(self, text):
        """
        Получаем токен для авторизации
        :param text:
        :return: строка вида "anHcFxWiCyEQEZiorAmwMeTD8u30AH9p"
        """
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        """
        Получаем id желаемого пользователя
        :param text:
        :param username: имя пользователя
        :return:
        """
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
