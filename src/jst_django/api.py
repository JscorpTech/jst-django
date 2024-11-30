import requests
from typing import Union, List


class Github:

    def __init__(self, repo: str = "django") -> None:
        self.project_id = "JscorpTech"
        self.repo = repo
        self.relase_urls = {
            "list": "releases",
            "latest": "releases/latest",
            "detail": "releases/tags/{}",
        }

    def request(self, action):
        url = "https://api.github.com/repos/{}/{}/{}".format(self.project_id, self.repo, action)
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        raise Exception("Server bilan aloqa yo'q")

    def releases(self, version=None) -> Union[List[str]]:
        """Barcha releaselarni"""
        versions = list(map(lambda x: x["name"], self.request(self.relase_urls["list"])))
        if version:
            return self.check_version(version, versions)
        return versions

    def latest_release(self) -> Union[str]:
        """Oxirgi release"""
        return self.request(self.relase_urls["latest"])["name"]

    def check_version(self, version: Union[str], versions: Union[List[str]]):
        """Versionni tekshirish"""
        if version not in versions:
            raise Exception("{} mavjud emas boshqa versiya tanlang: {}".format(version, ", ".join(versions)))
        return versions

    def branches(self):
        response = []
        branches = list(map(lambda branch: branch["name"], self.request("branches")))
        for branch in branches:
            if str(branch).startswith("V") or branch == "main" or branch == "dev":
                response.append(branch)
        response.reverse()
        return response
