import requests
from bs4 import BeautifulSoup
import json
from flask import Flask, render_template, request
from instagrapi import Client
import os

cl = Client()
cl.login("aizh.an2669", "1234567890aiz")
app = Flask(__name__)

class Parsing:
    def __init__(self, vk_user_nick, insta_user_name):
        self.vk_nick = vk_user_nick
        self.insta_username = insta_user_name
        self.fake_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
        self.vk_req = requests.get(f"https://vk.com/{self.vk_nick}",
                                headers={
                                    "User-Agent": self.fake_user_agent,
                                })
        self.vk_soup = BeautifulSoup(self.vk_req.content, "lxml")
        self.insta_req = requests.get(f"https://www.instagram.com/{self.insta_username}/",
                                headers={
                                    "User-Agent": self.fake_user_agent,
                                })
        self.insta_soup = BeautifulSoup(self.insta_req.content, "lxml")
        self.data_for_write = {"VK": {f"{self.vk_nick}": {}}, "Instagram": {f"{self.insta_username}": {}}}
        if self.vk_req.status_code == 200:
            self.vk_main_information(self.data_for_write["VK"][f"{self.vk_nick}"])
            self.vk_about_user(self.data_for_write["VK"][f"{self.vk_nick}"])
        if self.insta_req.status_code == 200:
            self.insta_main_information(self.data_for_write["Instagram"][f"{self.insta_username}"])
        Write(self.vk_nick, self.data_for_write).write_to_json()

    def vk_main_information(self, all_info):
        current_info = {}
        try:
            name = self.vk_soup.find(class_="page_name").text.strip()
        except AttributeError:
            name = "Not found"
        finally:
            current_info.update(Name=str(name))

        all_info.update({"Main info": current_info})

    def vk_about_user(self, all_info):
        current_info = {}

        try:
            labeled = self.vk_soup.find_all("div", class_="labeled")
            data = []

            for l in labeled[2:]:
                data.append(l.find("a").text)

        except AttributeError:
            data = "Not found"
        finally:
            current_info.update(AboutUser=data)

        all_info.update({"Data": current_info})



    def insta_main_information(self, all_info):
        current_info = {}
        try:
            name1 = cl.user_info_by_username(self.insta_username).dict()
            name = name1["full_name"]
            bio = name1["biography"]
            media = name1["media_count"]
            follower = name1["follower_count"]
            following = name1["following_count"]
            cpn = name1["contact_phone_number"]
            ppn = name1["public_phone_number"]
            mail = name1["public_email"]
            url = name1["profile_pic_url_hd"]
            dir_path = "static/img"
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            filename = "profile_photo.jpg"
            file_path = os.path.join(dir_path, filename)
            response = requests.get(url)
            with open(file_path, "wb") as f:
                f.write(response.content)
            if os.path.exists(file_path):
                print("Profile photo downloaded successfully to", file_path)
            else:
                print("Failed to download profile photo")
        except AttributeError:
            name = "Not found"
            bio = "Not found"
        finally:
            current_info.update(Name=str(name))
            current_info.update(Bio=str(bio))
            current_info.update(Media=str(media))
            current_info.update(Follower=str(follower))
            current_info.update(Following=str(following))
            current_info.update(Cpn=str(cpn))
            current_info.update(Ppn=str(ppn))
            current_info.update(Mail=str(mail))
        print(name1)
        all_info.update({"Main info": current_info})

class Write():
    def __init__(self, user_nick, dict_for_write):
        self.user_nick = user_nick
        self.file_name = f"{self.user_nick}.json"
        self.file_path = f"data/{self.file_name}"
        self.dick_for_write = dict_for_write
    def write_to_json(self):
        with open(self.file_path, "w") as file:
            json.dump(self.dick_for_write, file, indent=4)

    def print(self, file_name):
        with open(file_name, "rb") as f:
            data = json.load(f)
            print(data)
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/result", methods=["POST"])
def result():
    vk_user_nick = request.form["vk_user_nick"]
    insta_user_name = request.form["insta_user_name"]
    data_for_write = Parsing(vk_user_nick, insta_user_name).data_for_write
    Write(vk_user_nick, data_for_write).write_to_json()
    return render_template("result.html", data=data_for_write, vk_nick=vk_user_nick, insta_name=insta_user_name)

if __name__ == "__main__":
    app.run(debug=True)


