from flask_dance.contrib.github import github
import datetime, time, operator
from mapping.Repository import Repository


class Contributor():
    def __init__(self,
                 login=None,
                 id=None,
                 total=None,
                 contributions=None,
                 payload=None,
                 last_commit_date=None,
                 first_commit_date=None,
                 avg_additions="N/A",
                 avg_deletions="N/A",
                 avg_commits="N/A",
                 active_week="N/A",
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
                break

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
            if weeks:
                self.last_commit_date = max(weeks)
                self.first_commit_date = min(weeks)
                # get any item from list and extract the first day of week for these commits as an acitve
                commit_date_dt = datetime.datetime.strptime(
                    self.first_commit_date, '%Y-%m-%dT%H:%M:%SZ')
                self.active_week = commit_date_dt - datetime.timedelta(
                    days=commit_date_dt.weekday())
            else:
                self.last_commit_date = None
                self.first_commit_date = None
                self.active_week = None

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
        #e.g. /commits?author=mitsuhiko&since=2020-07-05T00:00:00Z
        commits_url = Repository.commits_url + f"?author={self.login}&since={last_week_str}"
        commits_resp = github.get(commits_url)
        commits_date = []
        if commits_resp.status_code == 200:
            payload = commits_resp.json()
            for commit in payload:
                commit_date = commit["commit"]["author"]["date"]
                commits_date.append(commit_date)
        return max(commits_date) if commits_date else None

    def get_first_commit_date(self, first_week):
        '''
        githup api requirements: convert epoch time to This is a timestamp in ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ.
        since=Only show notifications updated after the given time. This is a timestamp in ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ.
        until=Only commits before this date will be returned. This is a timestamp in ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ.
        get the time range greater than first week and less than next week
        '''
        # get previosu date of first week as using since >
        first_week_dt = datetime.datetime.fromtimestamp(first_week)
        first_week_dt -= datetime.timedelta(days=1)
        # get proceed date of first week as using unitl <
        next_week_dt = first_week_dt + datetime.timedelta(days=7)
        next_week_dt += datetime.timedelta(days=1)
        # convert to str
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
        return min(commits_date) if commits_date else None

    def to_dict_repo(self):
        return {"login": self.login, "contributions": self.contributions}

    def to_dict(self):
        # convert epoch time to str for fomrat
        # this happens for contritburo who has stats in api otherws will return string already
        if self.active_week:
            if type(self.active_week) == int:
                self.active_week = datetime.datetime.fromtimestamp(
                    self.active_week)
            self.active_week = self.active_week.strftime("%Y-%m-%d")
        # some contributors have statics but when calling commits it returs []
        # Therefore cannot determine first and last commit, may be bug in github api
        # e.g. /commits?author=jab
        if self.first_commit_date and self.last_commit_date:
            # 1- convert string to datetime
            self.first_commit_date = datetime.datetime.strptime(
                self.first_commit_date, "%Y-%m-%dT%H:%M:%SZ")
            self.last_commit_date = datetime.datetime.strptime(
                self.last_commit_date, "%Y-%m-%dT%H:%M:%SZ")
            # 2- format datetime
            self.first_commit_date = self.first_commit_date.strftime(
                "%Y-%m-%d")
            self.last_commit_date = self.last_commit_date.strftime("%Y-%m-%d")

        return {
            "login": self.login,
            "contributions": self.contributions,
            "total": self.total,
            "first_commit_date": self.first_commit_date,
            "last_commit_date": self.last_commit_date,
            "avg_additions": self.avg_additions,
            "avg_deletions": self.avg_deletions,
            "avg_commits": self.avg_commits,
            "active_week": self.active_week
        }