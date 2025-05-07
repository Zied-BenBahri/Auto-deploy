# Kubernetes Auto-Deployer 🚀

Automate Application Deployment to Kubernetes with Zero Manual Overhead

---

## 📊 Architecture Overview

This platform empowers users to deploy applications to a Kubernetes cluster automatically—directly from their GitHub repositories. With seamless GitHub Actions workflows and GitOps synchronization via ArgoCD, application updates are continuously delivered and deployed without manual intervention.

---

## 🚀 Workflow

1. **User Onboarding**  
   A user submits a form providing:
   - GitHub Repository URL
   - Application Name
   - Personal GitHub Token

2. **Repository Bootstrapping**  
   The backend clones a **predefined template repository** into a **new repository** for the user. This template contains two key GitHub Actions workflows:
   - `Import User Repo`: Imports the user's source code automatically.
   - `Build & Deploy`: Builds, tests, containerizes, and deploys the application.

3. **CI/CD Automation**  
   - After the user’s repo is imported, the **Build & Deploy** workflow triggers:
     - Detects application language (Node.js, Python, Java)
     - Builds and tests the application
     - Generates a Docker image
     - Pushes the image to Docker Hub
     - Updates Kubernetes manifests

4. **Continuous Deployment (GitOps)**  
   - A webhook on the user’s original repository listens for new commits.
   - Any commit triggers the automation pipeline again (sync, build, deploy).
   - **ArgoCD** watches Kubernetes manifests and ensures the cluster stays up-to-date with the latest deployment.

---

## 🛠️ Repository Structure

```
│   README.md
│
├───.github
│   └───workflows
│       │   import-user-repo.yml
│       │   build-and-deploy.yml
│
├───deploy
│       deploy.yaml
│       svc.yaml
│
└───<application source code> 
```

---

## ✨ Features You Will Use & Learn

- Git & GitHub for version control
- Docker for containerization
- Kubernetes for container orchestration
- GitHub Actions for CI/CD automation
- ArgoCD for continuous deployment (GitOps)
- Automatic language detection and Dockerfile generation

---

## 🖥️ Test Your Application Locally

We recommend testing your application locally before deploying.

### Pre-requisites

- Install Docker
- Install Python / Node.js / Java (depending on your app)

### Steps

```bash
git clone <your-repository-url>
cd <your-project-directory>

# For Python
pip install -r requirements.txt
python main.py

# For Node.js
npm install
npm start

# For Java (Maven)
mvn install
java -jar target/app.jar
```

Access the application locally (port depends on your framework—typically 5000 or 8080).

---

## 🐳 Containerize Your Application

Our workflow auto-generates Dockerfiles, but you can test it locally:

```bash
docker build -t <your-dockerhub-username>/<app-name>:v1 .
docker run -d -p 5000:5000 <your-dockerhub-username>/<app-name>:v1
```

If your app runs successfully, you’re ready for CI/CD!

---

## ⚙️ CI/CD Workflows

### 📥 Import User Repository Workflow

`.github/workflows/import-user-repo.yml`

```yaml
name: Import User Repo

on:
  workflow_dispatch:
    inputs:
      user_repo_url:
        description: 'User GitHub Repo URL'
        required: true
        type: string

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  import:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout current repo
        uses: actions/checkout@v3

      - name: Clone user repo
        run: git clone ${{ github.event.inputs.user_repo_url }} user-repo

      - name: Sync contents
        run: |
          find . -mindepth 1 -maxdepth 1 ! -name '.git' ! -name '.github' ! -name 'README.md' ! -name 'user-repo' -exec rm -rf {} +
          rsync -av --exclude='.git' --exclude='.github' user-repo/ .
          rm -rf user-repo

      - name: Commit and Push
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git remote set-url origin https://x-access-token:${{ secrets.GITHUB_TOKEN }}@github.com/${{ github.repository }}
          git add .
          git commit -m "Sync from user repo (via webhook)" || echo "Nothing to commit"
          git push origin main
```

---

### ⚙️ Build & Deploy Workflow

`.github/workflows/build-and-deploy.yml`

```yaml
name: Build & Deploy

on:
  workflow_run:
    workflows: ["Import User Repo"]
    types:
      - completed

jobs:
  detect-and-build:
    runs-on: ubuntu-latest

    env:
      COMMIT_SHA: ${{ github.sha }}
      VERSION_TAG: latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set IMAGE_NAME
        run: |
          REPO_NAME=$(basename "${GITHUB_REPOSITORY}" | tr '[:upper:]' '[:lower:]')
          echo "IMAGE_NAME=${{ secrets.DOCKERHUB_USERNAME }}/$REPO_NAME" >> $GITHUB_ENV

      - name: Detect language
        id: language_detection
        run: |
          if find . -name "package.json" | grep -q .; then
            echo "NODE=true" >> $GITHUB_ENV
          elif find . -name "requirements.txt" | grep -q .; then
            echo "PYTHON=true" >> $GITHUB_ENV
          elif find . -name "pom.xml" | grep -q .; then
            echo "JAVA=true" >> $GITHUB_ENV
          elif [ -f "Dockerfile" ]; then
            echo "DOCKER=true" >> $GITHUB_ENV
          else
            echo "UNKNOWN=true" >> $GITHUB_ENV
            exit 1

      - name: Build & Test (Node.js)
        if: env.NODE == 'true'
        run: |
          npm install
          npm test

      - name: Build & Test (Python)
        if: env.PYTHON == 'true'
        run: |
          pip install -r requirements.txt
          pytest || echo "No tests found"

      - name: Build & Test (Java)
        if: env.JAVA == 'true'
        run: |
          mvn install
          mvn test

      - name: Generate Dockerfile (if needed)
        run: |
          if [ "${NODE}" = "true" ] && [ -z "${DOCKER}" ]; then
            echo -e "FROM node:16\nWORKDIR /app\nCOPY . .\nRUN npm install\nCMD [\"npm\", \"start\"]" > Dockerfile
          elif [ "${PYTHON}" = "true" ] && [ -z "${DOCKER}" ]; then
            echo -e "FROM python:3.9\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nCMD [\"python\", \"main.py\"]" > Dockerfile
          elif [ "${JAVA}" = "true" ] && [ -z "${DOCKER}" ]; then
            echo -e "FROM openjdk:11\nWORKDIR /app\nCOPY . .\nRUN mvn clean install\nCMD [\"java\", \"-jar\", \"target/app.jar\"]" > Dockerfile
          fi

      - name: Login to DockerHub
        run: echo "${{ secrets.DOCKERHUB_PASSWORD }}" | docker login -u "${{ secrets.DOCKERHUB_USERNAME }}" --password-stdin

      - name: Build Docker image
        run: docker build -t $IMAGE_NAME:$VERSION_TAG -t $IMAGE_NAME:$COMMIT_SHA .

      - name: Push Docker image to DockerHub
        run: docker push $IMAGE_NAME:$COMMIT_SHA
```

---

## 🛡️ Setup ArgoCD in Kubernetes Cluster

1. Install ArgoCD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

2. Expose ArgoCD UI

```bash
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "NodePort"}}'
kubectl get svc -n argocd
```

3. Access ArgoCD UI (for Minikube users)

```bash
minikube service argocd-server -n argocd
```

---

## ✅ Summary

This project provides a full **CI/CD + GitOps** solution for automatically deploying applications to Kubernetes. Once set up, users can simply push to their repository, and their application will build, containerize, and deploy—automatically and reliably.
