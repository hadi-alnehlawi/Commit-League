from flask_dance.contrib.github import github
from mapping.Repository import Repository
from mapping.Contributor import Contributor


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