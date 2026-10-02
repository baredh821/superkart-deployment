# SuperKart Sales Forecast - containerized deployment

## Run in a GitHub Codespace
```bash
docker network create superkart-net

# Backend (Flask API on 7860)
docker build -t superkart-backend ./backend_files
docker run -d --name backend --network superkart-net -p 7860:7860 superkart-backend

# Frontend (Streamlit on 8501), talks to the backend over the Docker network
docker build -t superkart-frontend ./frontend_files
docker run -d --name frontend --network superkart-net -p 8501:8501 -e BACKEND_URL=http://backend:7860 superkart-frontend
```
Then set port 7860 (and 8501) to **Public** in the Codespace Ports tab.
