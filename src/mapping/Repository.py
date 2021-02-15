import os
from flask_dance.contrib.github import github


class Repository():
    repo = os.environ.get("REPOSITORY")
    owner = os.environ.get("OWNER")
    repo_url = "repos" + f"/{owner}/{repo}"
    contribtuor_ul = repo_url + "/contributors"
    stats_url = repo_url + "/stats/contributors"
    commits_url = repo_url + f"/commits"

    @classmethod
    def get_repo_res(cls):
        return github.get(cls.repo_url)

    @classmethod
    def get_contribtuor_res(cls):
        return github.get(cls.contribtuor_ul)

    @classmethod
    def get_stats_res(cls):
        return github.get(cls.stats_url)