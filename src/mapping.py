from flask_dance.contrib.github import github
from flask import jsonify
import time, operator
import datetime, os


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
                 active_week=None,
                 load_stats=None):
        self.login = login
        self.total = total
        self.contributions = contributions
        self.last_commit_date = last_commit_date
        self.first_commit_date = first_commit_date
        self.avg_additions = avg_additions
        self.avg_deletions = avg_deletions
        self.avg_commits = avg_commits
        self.active_week = active_week
        if load_stats:
            self.set_properties()

    def set_properties(self):
        actvties = {}
        payload = Repository.get_stats_res().json()
        for item in payload:
            if item["author"]["login"] == self.login:
                # iterate on contirbutor week data
                self.total = item["total"]
                actvties = self.parse_activity(item["weeks"])
        if actvties:
            # last_commit_date
            last_week = actvties["last_week"]
            self.last_commit_date = self.get_last_commit_date(last_week)
            #  first_commit_date
            first_week = actvties["first_week"]
            self.first_commit_date = self.get_first_commit_date(first_week)
            # avg_additions
            self.avg_additions = round(
                actvties["activities"][0] / len(item["weeks"]), 2)
            # avg_deletions
            self.avg_deletions = round(
                actvties["activities"][1] / len(item["weeks"]), 2)
            # avg_commits
            self.avg_commits = round(
                actvties["activities"][2] / len(item["weeks"]), 2)
            # active_week
            self.active_week = actvties["active_week"][0]
        else:
            #commits happened in one week for that reason github not connsider it stats
            # I have to look on commit end point directly :/commits?author=
            commits_url = Repository.commits_url + f"?author={self.login}"
            commits_resp = github.get(commits_url)
            # get days of commit in a list
            # extract max & min of commits date
            weeks = []
            for item in commits_resp.json():
                date = item["commit"]["author"]["date"]
                weeks.append(date)
            self.last_commit_date = max(weeks)
            self.first_commit_date = min(weeks)
            # get any item from list and extract the first day of week for these commits as an acitve
            commit_date_dt = datetime.datetime.strptime(
                self.first_commit_date, '%Y-%m-%dT%H:%M:%SZ')
            self.active_week = commit_date_dt - datetime.timedelta(
                days=commit_date_dt.weekday())

    def parse_activity(self, weeks):
        activities = (0, 0, 0)  # (sum(a), sum(d) , sum(c))
        active_week = (None, 0)  # (w, sum(activitiy of this week))
        first_week = None
        last_week = None
        for week in weeks:
            w = week["w"]
            activity = week["a"], week["d"], week["c"]
            if activity != (0, 0, 0):
                first_week = min(first_week, w) if first_week else w
                last_week = max(last_week, w) if last_week else w
                sum_activity = sum(list(activity))
                if (not active_week[0]) or (active_week[1] < sum_activity):
                    active_week = (w, sum_activity)
                activities = tuple(map(operator.add, activities, activity))
        return {
            "activities": activities,
            "active_week": active_week,
            "first_week": first_week,
            "last_week": last_week
        }

    def get_last_commit_date(self, last_week):
        '''
        githup api requirements: convert epoch time to This is a timestamp in ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ.
        since=Only show notifications updated after the given time. This is a timestamp in ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ.
        '''
        last_week_dt = datetime.datetime.fromtimestamp(last_week)
        # get next date of week as using >
        last_week_dt -= datetime.timedelta(days=1)
        last_week_str = last_week_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        #e.g. /commits??author=mitsuhiko&since=2020-07-05T00:00:00Z
        commits_url = Repository.commits_url + f"?author={self.login}&since={last_week_str}"
        commits_resp = github.get(commits_url)
        commits_date = []
        if commits_resp.status_code == 200:
            payload = commits_resp.json()
            for commit in payload:
                commit_date = commit["commit"]["author"]["date"]
                commits_date.append(commit_date)
        return max(commits_date)

    def get_first_commit_date(self, first_week):
        '''
        githup api requirements: convert epoch time to This is a timestamp in ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ.
        since=Only show notifications updated after the given time. This is a timestamp in ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ.
        until=Only commits before this date will be returned. This is a timestamp in ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ.
        get the time range greater than first week and less than next week
        '''
        first_week_dt = datetime.datetime.fromtimestamp(first_week)
        # get previosue date of week as using >
        first_week_dt -= datetime.timedelta(days=1)
        next_week_dt = first_week_dt + datetime.timedelta(days=7)
        first_week_str = first_week_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        next_week_str = next_week_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        # e.g. /commits??author=mitsuhiko&until=2011-02-05T00:00:00Z
        commits_url = Repository.commits_url + f"?author={self.login}&since={first_week_str}&until={next_week_str}"
        commits_resp = github.get(commits_url)
        commits_date = []
        if commits_resp.status_code == 200:
            payload = commits_resp.json()
            for commit in payload:
                commit_date = commit["commit"]["author"]["date"]
                commits_date.append(commit_date)
        return min(commits_date)

    def to_dict_repo(self):
        return {"login": self.login, "contributions": self.contributions}

    def to_dict(self):
        active_week = self.active_week
        # convert epoch time to str for fomrat
        # this happens for contritburo who has stats in api otherws will return string already
        if type(active_week) == int:
            active_week = datetime.datetime.fromtimestamp(self.active_week)
        active_week = active_week.strftime("%Y-%m-%d")
        # 1- convert string to datetime
        first_commit_date = datetime.datetime.strptime(self.first_commit_date,
                                                       "%Y-%m-%dT%H:%M:%SZ")
        last_commit_date = datetime.datetime.strptime(self.last_commit_date,
                                                      "%Y-%m-%dT%H:%M:%SZ")

        # 2- format datetime
        first_commit_date = first_commit_date.strftime("%Y-%m-%d")
        last_commit_date = last_commit_date.strftime("%Y-%m-%d")

        return {
            "login": self.login,
            "contributions": self.contributions,
            "total": self.total,
            "first_commit_date": first_commit_date,
            "last_commit_date": last_commit_date,
            "avg_additions": self.avg_additions,
            "avg_deletions": self.avg_deletions,
            "avg_commits": self.avg_commits,
            "active_week": active_week
        }


class Repo():
    def __init__(self, id=None, num_contributors=None, full_name=None):
        self.id = id
        self.num_contributors = num_contributors
        self.full_name = full_name
        self.contributors = []
        self.set_properties()

    def to_dict(self):
        return {
            "full_name":
            self.full_name,
            "contributors":
            [contributor.to_dict_repo() for contributor in self.contributors]
        }

    def set_properties(self):
        '''
        GitHub identifies contributors by author email address.
        This endpoint groups contribution counts by GitHub user,
        which includes all associated email addresses.
        To improve performance, only the first 500 author email addresses in the repository link to GitHub users.
        '''
        payload = Repository.get_repo_res().json()
        self.id = payload.get("id")
        self.full_name = payload.get("full_name")

        for page in range(1, 10):
            url = Repository.contribtuor_ul + f"?per_page=100&page={page}"
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