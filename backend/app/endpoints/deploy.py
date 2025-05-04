from fastapi import HTTPException
from app.models import DeployRequest
from app.services import GithubService, YamlGenerator

def deploy_app(request: DeployRequest):
    github_service = GithubService()
    yaml_generator = YamlGenerator()

    try:
        repo_url = github_service.create_repo_from_template(request.app_name)
        print(f"New repo created: {repo_url}")  
        github_service.import_user_repo(repo_url, request.user_repo_url)

        yaml_str = yaml_generator.generate(
            app_name=request.app_name,
            language=request.language,
            has_dockerfile=request.has_dockerfile
        )

        github_service.push_file_to_repo(
            repo_name=request.app_name,
            file_path="k8s/deployment.yaml",
            content=yaml_str
        )

        return {
            "status": "success",
            "repo_url": repo_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
