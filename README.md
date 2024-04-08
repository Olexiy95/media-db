# Media-DB

### Docker Commands:

```bash
# Bring up containers in docker-compose.
docker compose -f docker-compose.yml up

# Bring down containers in docker-compose.
docker compose -f docker-compose.yml down

# Rebuild containers in docker-compose.
docker-compose -f docker-compose.yml build --no-cache
```

### Virtual Environment Setup:

```bash
# Create a virtual environment.
python -m venv venv

# Mac venv activation.
source venv/bin/activate

# Windows venv activation.
.\venv\Scripts\activate

# Install all dependencies used by all services for local testing in virtual environment.
pip install -r venv_requirements.txt
```
