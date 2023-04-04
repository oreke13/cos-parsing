import requests  # импортируем модуль requests для отправки HTTP-запросов
from bs4 import BeautifulSoup  # импортируем BeautifulSoup для парсинга HTML-кода
import json  # импортируем модуль json для работы с JSON
from flask import Flask, render_template, request  # импортируем Flask для создания веб-приложения и render_template для вывода шаблонов
from instagrapi import Client  # импортируем instagrapi для работы с Instagram API
import os  # импортируем модуль os для работы с операционной системой

# создаем экземпляр клиента Instagrapi
cl = Client()
# осуществляем вход в Instagram аккаунт
cl.login("aizh.an2669", "1234567890aiz")

# создаем экземпляр Flask-приложения
app = Flask(__name__)

class Parsing:
    """Выполняет запрос и парсит всю нужную информацию"""
    def __init__(self, vk_user_nick, insta_user_name):
        self.vk_nick = vk_user_nick  # сохраняем ник пользователя ВКонтакте
        self.insta_username = insta_user_name  # сохраняем имя пользователя Instagram
        self.fake_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
        # сохраняем поддельный User-Agent для заголовка запроса
        self.vk_req = requests.get(f"https://vk.com/{self.vk_nick}",  # отправляем GET-запрос на страницу пользователя ВКонтакте
                                headers={
                                    "User-Agent": self.fake_user_agent,  # передаем поддельный User-Agent в заголовке запроса
                                })
        self.vk_soup = BeautifulSoup(self.vk_req.content, "lxml")  # парсим HTML-код страницы ВКонтакте
        self.insta_req = requests.get(f"https://www.instagram.com/{self.insta_username}/",  # отправляем GET-запрос на страницу пользователя Instagram
                                headers={
                                    "User-Agent": self.fake_user_agent,  # передаем поддельный User-Agent в заголовке запроса
                                })
        self.insta_soup = BeautifulSoup(self.insta_req.content, "lxml")  # парсим HTML-код страницы Instagram
        self.data_for_write = {"VK": {f"{self.vk_nick}": {}}, "Instagram": {f"{self.insta_username}": {}}}
        # создаем пустой словарь для хранения информации, полученной из VK и Instagram
        if self.vk_req.status_code == 200:  # если запрос на страницу ВКонтакте успешен
            self.vk_main_information(self.data_for_write["VK"][f"{self.vk_nick}"])  # получаем основную информацию из страницы ВКонтакте и записываем ее в словарь data_for_write
            self.vk_about_user(self.data_for_write["VK"][f"{self.vk_nick}"])  # получаем дополнительную информацию о

        class Write():
            def __init__(self, user_nick, dict_for_write):
                self.user_nick = user_nick
                self.file_name = f"{self.user_nick}.json"
                self.file_path = f"data/{self.file_name}"
                self.dick_for_write = dict_for_write

            def write_to_json(self):
                # Записываем словарь в формате JSON в файл
                with open(self.file_path, "w") as file:
                    json.dump(self.dick_for_write, file, indent=4)

            def print(self, file_name):
                # Читаем и выводим содержимое файла с данными в формате JSON
                with open(file_name, "rb") as f:
                    data = json.load(f)
                    print(data)
