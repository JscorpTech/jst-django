import requests


class Gitlab:

    def __init__(self) -> None:
        self.project_id = "56597109"

    def request(self, action):
        url = "https://gitlab.com/api/v4/projects/{}/repository/{}".format(
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
            if str(branch).startswith("V"):
                response.append(branch)
        response.reverse()
        return response
