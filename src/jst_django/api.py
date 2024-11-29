import requests
from typing import Union, List


class Github:

    def __init__(self) -> None:
        self.project_id = "JscorpTech"
        self.relase_urls = {
            "list": "releases",
            "latest": "releases/latest",
            "detail": "releases/tags/{}",
        }

    def request(self, action):
        url = "https://api.github.com/repos/{}/django/{}".format(
            self.project_id, action
        )
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        raise Exception("Server bilan aloqa yo'q")

    def releases(self) -> Union[List[str]]:
        """Barcha releaselarni"""
        return list(map(lambda x: x["name"], self.request(self.relase_urls["list"])))

    def latest_release(self) -> Union[str]:
        """Oxirgi release"""
        return self.request(self.relase_urls["latest"])["name"]

    def branches(self):
        response = []
        branches = list(map(lambda branch: branch["name"], self.request("branches")))
        for branch in branches:
            if str(branch).startswith("V") or branch == "main" or branch == "dev":
                response.append(branch)
        response.reverse()
        return response
