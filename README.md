# Tiny Team HQ

A small employee management web app with an automated CI/CD pipeline.
Add, edit, search and remove teammates. Every push to GitHub is tested, packaged
into a Docker image and deployed to a cloud VM automatically.

## Tech used

| Part | Tool |
|---|---|
| App | Python, Flask, SQLite |
| Tests | pytest |
| Packaging | Docker, docker-compose |
| Pipeline | GitHub Actions |
| Image storage | Docker Hub |
| Cloud | Azure Virtual Machine (Ubuntu) |

## Folder layout

```
employee-mgmt/
├── app.py                  the Flask app (all routes + database code)
├── templates/              HTML pages (base, list, form)
├── static/style.css        the cute styling
├── tests/test_app.py       automated tests
├── requirements.txt        Python libraries
├── Dockerfile              how to build the container image
├── docker-compose.yml      run the app locally with one command
└── .github/workflows/
    └── ci-cd.yml           the pipeline (test -> build -> deploy)
```

## Run it on your laptop

```
pip install -r requirements.txt
python app.py
```
Open http://localhost:5000

## Run the tests

```
pip install pytest
pytest -v
```

## Run it with Docker

```
docker compose up --build
```
Open http://localhost:5000

## How the pipeline works

```
git push  ->  run tests  ->  build Docker image  ->  push to Docker Hub  ->  deploy to Azure VM
```

- Push to `develop`: deploys the **staging** copy (port 8080)
- Push to `main`: deploys the **production** copy (port 80)
- If any test fails, nothing is built or deployed.

## GitHub secrets the pipeline needs

| Secret | What it is |
|---|---|
| `DOCKERHUB_USERNAME` | your Docker Hub username |
| `DOCKERHUB_TOKEN` | a Docker Hub access token |
| `VM_HOST` | public IP of the Azure VM |
| `VM_USER` | VM login name (`azureuser`) |
| `VM_SSH_KEY` | contents of the VM's private key (.pem) file |
