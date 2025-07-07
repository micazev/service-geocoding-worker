# Geocoding Worker Service

A Python service for geocoding addresses, designed for integration with real estate auction data pipelines.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and fill in your API token and folder paths as needed.

## Usage

To start the worker:

```bash
python worker.py
```

If you later expose a script entrypoint (e.g., via `setup.py` or `pyproject.toml`):

```bash
geocode
```# service-geocoding-worker
