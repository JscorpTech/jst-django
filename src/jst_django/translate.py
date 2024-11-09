from typing import Union, List, Dict, Tuple, Any
import requests
from .logger import logging
from polib import pofile
from tqdm import tqdm
import questionary
import os


class Translate:
    messages = None

    def __init__(self) -> None:
        self.langs: Union[List] = [
            "uzn_Latn",
            "uzn_Cyrl",
            "rus_Cyrl",
            "eng_Latn",
        ]

    def translate(self, message, source, target) -> Union[Tuple]:
        url = "https://websocket.tahrirchi.uz/handle-batch"

        payload = {
            "jobs": [{ "text": message }],
            "source_lang": source,
            "target_lang": target
        }
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "uz,en-US;q=0.9,en;q=0.8,ru;q=0.7",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Origin": "https://tahrirchi.uz",
            "Referer": "https://tahrirchi.uz/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Linux\"",
            "content-type": "application/json"
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            return True, response.json()['sentences'][0]['translated']
        except Exception as e:
            logging.error(e)
            return False, message
    
    def get_messages(self, path: Union[str]) -> Any:
        messages = pofile(path)
        self.messages = messages
        return messages
    
    def get_pofiles(self) -> Union[List]:
        res = []
        for i in os.listdir(os.path.join(os.getcwd(), "resources/locale")):
            if not i.startswith("."):
                res.append(i)
        return res

    def run(self) -> None:
        pofiles = self.get_pofiles()
        file = questionary.select("Fayil joylashgan papkani tanlang: resources/locale", choices=pofiles).ask()
        source = questionary.select("Hozirli fayil tilini tanlang: ", choices=self.langs).ask()
        target = questionary.select("Tarjima qilish kerak bo'lgan til: ", choices=self.langs).ask()
        self.get_messages(os.path.join(os.getcwd(), "resources/locale/{}/LC_MESSAGES/django.po".format(file)))
        progress = tqdm(total=len(self.messages))
        for index, message in enumerate(self.messages):
            if message.msgstr != "":
                continue
            message.msgstr = self.translate(message.msgid, source, target)[1]
            progress.update(1)
            if index % 10 == 0:
                self.messages.save()
        self.messages.save()
        logging.info("Tarjima qilish yakunlandi!!!")
