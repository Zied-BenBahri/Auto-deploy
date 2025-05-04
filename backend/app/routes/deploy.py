from fastapi import APIRouter
from app.models import DeployRequest
from app.endpoints.deploy import deploy_app

router = APIRouter()

@router.post("/deploy")
def deploy_route(request: DeployRequest):
    return deploy_app(request)
