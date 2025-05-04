import requests
import base64
import time

from app.config import GITHUB_TOKEN, GITHUB_USERNAME, TEMPLATE_REPO

GITHUB_API = "https://api.github.com"


class GithubService:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        })

    def create_repo_from_template(self, repo_name: str) -> str:
        """
        Create a new repo from the predefined template repo.
        Returns the HTTPS GitHub URL of the new repo.
        """
        url = f"{GITHUB_API}/repos/{GITHUB_USERNAME}/{TEMPLATE_REPO}/generate"
        data = {
            "owner": GITHUB_USERNAME,
            "name": repo_name,
            "include_all_branches": False,
            "private": False
        }
        response = self.session.post(url, json=data)
        if response.status_code == 422:
            print("GitHub error:", response.json())
        response.raise_for_status()
        return f"https://github.com/{GITHUB_USERNAME}/{repo_name}"
        

    def wait_for_repo_availability(self, repo_name: str, timeout=10):
            check_url = f"{GITHUB_API}/repos/{GITHUB_USERNAME}/{repo_name}"
            for _ in range(timeout):
                r = self.session.get(check_url)
                if r.status_code == 200:
                    return True
                time.sleep(1)
            raise Exception("Repo did not become available in time")
        


    def import_user_repo(self, new_repo_url: str, user_repo_url: str) -> None:
        """
        Imports code from the user's repo into the newly created repo.
        """
        repo_name = new_repo_url.split("/")[-1]
        import_url = f"{GITHUB_API}/repos/{GITHUB_USERNAME}/{repo_name}/import"
        print(f"Importing {user_repo_url} into {import_url}")
        data = {
            "vcs": "git",
            "vcs_url": user_repo_url
        }

        response = self.session.put(import_url, json=data)
        response.raise_for_status()

    def push_file_to_repo(self, repo_name: str, file_path: str, content: str) -> None:
        """
        Pushes a file (e.g., deployment.yaml) to the given repo.
        """
        url = f"{GITHUB_API}/repos/{GITHUB_USERNAME}/{repo_name}/contents/{file_path}"

        encoded_content = base64.b64encode(content.encode()).decode()
        data = {
            "message": "Add deployment manifest",
            "content": encoded_content
        }

        response = self.session.put(url, json=data)
        response.raise_for_status()
