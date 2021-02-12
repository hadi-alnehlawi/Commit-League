from flask_dance.contrib.github import github
from flask import jsonify
import time, operator


class Contributor():
    def __init__(self,
                 login=None,
                 id=None,
                 total=None,
                 contributions=None,
                 payload=None,
                 last_commit_date=None,
                 first_commit_date=None,
                 avg_additions=None,
                 avg_deletions=None,
                 avg_commits=None,
                 active_week=None):
        self.login = login
        self.total = total
        self.contributions = contributions
        self.last_commit_date = last_commit_date
        self.first_commit_date = first_commit_date
        self.avg_deletions = avg_deletions
        self.avg_commits = avg_commits
        self.active_week = active_week
        if payload:
            self.set_properties(payload)

    def set_properties(self, payload):
        actvties = {}
        for item in payload:
            if item["author"]["login"] == self.login:
                # iterate on contirbutor week data
                self.total = item["total"]
                actvties = self.parse_activity(item["weeks"])
        self.avg_additions = round(
            actvties["activities"][0] / len(item["weeks"]), 2)
        self.avg_deletions = round(
            actvties["activities"][1] / len(item["weeks"]), 2)
        self.avg_commits = round(
            actvties["activities"][2] / len(item["weeks"]), 2)
        self.active_week = actvties["active_week"][0]

    def parse_activity(self, weeks):
        activities = (0, 0, 0)  # (sum(a), sum(d) , sum(c))
        active_week = (None, 0)  # (w, sum(activitiy of this week))
        for week in weeks:
            w = week["w"]
            activity = week["a"], week["d"], week["c"]
            if activity != (0, 0, 0):
                self.first_commit_date = min(
                    self.first_commit_date, w) if self.first_commit_date else w
                self.last_commit_date = max(self.last_commit_date,
                                            w) if self.last_commit_date else w
                sum_activity = sum(list(activity))
                if (not active_week[0]) or (active_week[1] < sum_activity):
                    active_week = (w, sum_activity)
                activities = tuple(map(operator.add, activities, activity))
        return {"activities": activities, "active_week": active_week}

    def to_dict_repo(self):
        return {"login": self.login, "contributions": self.contributions}

    def to_dict(self):
        return {
            "login":
            self.login,
            "contributions":
            self.contributions,
            "total":
            self.total,
            "first_commit_date":
            time.strftime('%Y-%m-%d %H:%M:%S',
                          time.localtime(self.first_commit_date)),
            "last_commit_date":
            time.strftime('%Y-%m-%d %H:%M:%S',
                          time.localtime(self.last_commit_date)),
            "avg_additions":
            self.avg_additions,
            "avg_deletions":
            self.avg_deletions,
            "avg_commits":
            self.avg_commits,
            "active_week":
            time.strftime('%Y-%m-%d', time.localtime(self.active_week))
        }


class Repo():
    def __init__(self, url, payload, id=None, num_contributors=None):
        self.url = url
        self.id = id
        self.num_contributors = num_contributors
        self.full_name = ""
        self.contributors = []
        self.set_properties(payload)

    def to_dict(self):
        keys = ["login", "contributions"]
        return {
            "full_name":
            self.full_name,
            "contributors":
            [contributor.to_dict_repo() for contributor in self.contributors]
        }

    def set_properties(self, payload):
        '''
        GitHub identifies contributors by author email address.
        This endpoint groups contribution counts by GitHub user,
        which includes all associated email addresses.
        To improve performance, only the first 500 author email addresses in the repository link to GitHub users.
        '''
        self.id = payload.get("id")
        self.full_name = payload.get("full_name")

        for page in range(1, 10):
            url = self.url + f"/contributors?per_page=100&page={page}"
            resp_contributors = github.get(url)
            # The history or contributor list is too large to list contributors for this repository via the API
            if resp_contributors.status_code != 403 or resp_contributors.json(
            ):
                self.set_contributors(payload=resp_contributors.json())
            else:
                break
        self.num_contributors = len(self.contributors)

    def set_contributors(self, payload):
        for contributor in payload:
            login = contributor.get("login")
            contributions = contributor.get("contributions")
            contributor = Contributor(login=login, contributions=contributions)
            self.contributors.append(contributor)