import requests
import time
from app.config import GITHUB_TOKEN, GITHUB_USERNAME, TEMPLATE_REPO, WEBHOOK_URL

GITHUB_API = "https://api.github.com"


class GithubService:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        })

    def create_repo_from_template(self, user_repo_url: str, username: str) -> str:
        """
        Create a new repo from the predefined template repo.
        The new repo name is based on the user's repo name and username.
        Returns the name of the newly created repo.
        """
        user_repo_name = user_repo_url.rstrip("/").split("/")[-1].replace(".git", "")
        new_repo_name = f"{username.lower()}-{user_repo_name}-deployed"

        url = f"{GITHUB_API}/repos/{GITHUB_USERNAME}/{TEMPLATE_REPO}/generate"
        data = {
            "owner": GITHUB_USERNAME,
            "name": new_repo_name,
            "include_all_branches": False,
            "private": False
        }

        response = self.session.post(url, json=data)
        if response.status_code == 422:
            print("GitHub error:", response.json())
        response.raise_for_status()

        return new_repo_name

        

    def wait_for_workflow(self,repo_name: str, workflow_filename: str, timeout=15):
        """
        Waits for a workflow file to become available in the newly created repo.
        """
        url = f"{GITHUB_API}/repos/{GITHUB_USERNAME}/{repo_name}/actions/workflows/{workflow_filename}"
        start = time.time()
        while time.time() - start < timeout:
            response = self.session.get(url)
            if response.status_code == 200:
                return True
            time.sleep(1)
        raise Exception("Workflow file not found in time")

 


    def trigger_import_workflow(self, repo_name: str, user_repo_url: str,workflow_file) -> None:
            """
            Triggers the GitHub Actions workflow in the new repo to import the user repo.
            """
            url = f"{GITHUB_API}/repos/{GITHUB_USERNAME}/{repo_name}/actions/workflows/{workflow_file}/dispatches"

            data = {
                "ref": "main",
                "inputs": {
                    "user_repo_url": user_repo_url
                }
            }

            print(f"Triggering workflow in repo {repo_name} with input {user_repo_url}")
            response = self.session.post(url, json=data)
            if response.status_code != 204:
                print("GitHub API error:", response.status_code, response.text)
            response.raise_for_status()




    def create_github_webhook(self, repo_url: str, username: str,deployed_repo_name):
        """
        Creates a webhook for the user's GitHub repo using the app's internal username.
        """
        owner_repo = repo_url.replace("https://github.com/", "").rstrip(".git")
        api_url = f"https://api.github.com/repos/{owner_repo}/hooks"

        # Include your internal app username in the webhook URL
        webhook_url = f"{WEBHOOK_URL}/{username}/{deployed_repo_name}"

        payload = {
            "name": "web",  
            "active": True,
            "events": ["push"],
            "config": {
                "url": webhook_url,
                "content_type": "json",
                "insecure_ssl": "0"
            }
        }

        print(f"Creating webhook at: {webhook_url}")
        response = self.session.post(api_url, json=payload)

        if response.status_code == 201:
            print("✅ Webhook created successfully.")
        else:
            print(f"❌ Failed to create webhook: {response.status_code}")
            print(response.json())




