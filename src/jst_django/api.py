import requests


class Github:

    def __init__(self) -> None:
        self.project_id = "JscorpTech"

    def request(self, action):
        url = "https://api.github.com/repos/{}/django/{}".format(
            self.project_id, action
        )
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        raise Exception("Server bilan aloqa yo'q")

    def branches(self):
        response = []
        branches = list(map(lambda branch: branch["name"], self.request("branches")))
        for branch in branches:
            if str(branch).startswith("V") or branch == "main" or branch == "dev":
                response.append(branch)
        response.reverse()
        return response
