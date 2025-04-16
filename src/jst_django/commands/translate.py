from typing import Union, List, Tuple, Any
import requests
from jst_django.utils.logger import logging
from polib import pofile
from tqdm import tqdm
import questionary
import os
from jst_django.utils import Jst, cancel
from rich.console import Console
import time
from jst_django.cli.app import app

console = Console()


class Translate:
    messages = None
    _token = None

    def __init__(self) -> None:
        self.langs: Union[List] = [
            "uzn_Latn",
            "uzn_Cyrl",
            "rus_Cyrl",
            "eng_Latn",
        ]
        self.config = Jst().load_config()

    @property
    def token(self) -> str:
        if self._token is not None:
            return self._token
        auth = "https://auth.tahrirchi.uz/v1/guest"
        response = requests.post(auth, data={})
        token = response.json().get("data").get("access_token")
        self._token = token
        if token is None:
            raise Exception("Token olishda xatolik yuz berdi")
        return token

    def translate(self, message, source, target) -> Union[Tuple]:
        url = "https://websocket.tahrirchi.uz/handle-batch"

        payload = {"jobs": [{"text": message}], "source_lang": source, "target_lang": target}
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "uz,en-US;q=0.9,en;q=0.8,ru;q=0.7",
            "Authorization": "Bearer " + self.token,
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Origin": "https://tahrirchi.uz",
            "Referer": "https://tahrirchi.uz/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "content-type": "application/json",
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            return True, response.json()["sentences"][0]["translated"]
        except Exception as e:
            logging.error(e)
            return False, message

    def get_messages(self, path: Union[str]) -> Any:
        messages = pofile(path)
        self.messages = messages
        return messages

    def get_pofiles(self) -> Union[List]:
        res = []
        for i in os.listdir(os.path.join(os.getcwd(), self.config["dirs"]["locale"])):
            if not i.startswith("."):
                res.append(i)
        return res

    def run(self) -> None:
        pofiles = self.get_pofiles()
        file = questionary.select(
            "Fayil joylashgan papkani tanlang: %s" % self.config["dirs"]["locale"], choices=pofiles
        ).ask()
        if file is None:
            return cancel()

        source = questionary.select("Hozirgi fayil tilini tanlang: ", choices=self.langs).ask()
        if source is None:
            return cancel()

        target = questionary.select("Tarjima qilish kerak bo'lgan til: ", choices=self.langs).ask()
        if target is None:
            return cancel()

        self.get_messages(
            os.path.join(os.getcwd(), "{}/{}/LC_MESSAGES/django.po".format(self.config["dirs"]["locale"], file))
        )

        progress = tqdm(total=len(self.messages), dynamic_ncols=True, position=0)
        logs = []  # Oxirgi 10 ta logni saqlash uchun ro'yxat

        for index, message in enumerate(self.messages):
            if message.msgstr.strip() != "":
                time.sleep(0.01)
                progress.update(1)
                logs.append(
                    f"\033[90m{message.msgid[:50]}\033[0m → \033[90m{message.msgstr[:50]}\033[0m"
                )  # Cyan va Green
            else:
                progress.update(1)
                message.msgstr = self.translate(message.msgid, source, target)[1]
                logs.append(
                    f"\033[36m{message.msgid[:50]}\033[0m → \033[32m{message.msgstr[:50]}\033[0m"
                )  # Cyan va Green

            # Loglarni yangilash
            if len(logs) > 5:
                logs.pop(0)

            # Terminalni tozalamasdan faqat oxirgi 10 ta logni o‘zgartiramiz
            tqdm.write("\n".join(logs))
            tqdm.write("\033[%sA" % len(logs), end="")

            if index % 10 == 0:
                self.messages.save()

        self.messages.save()
        progress.close()

        logging.info("Tarjima qilish yakunlandi!!!")


@app.command(name="translate", help="Avtomatik tarjima")
def translate():
    Translate().run()
