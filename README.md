# Geocoding Worker Service 🗺️

A Python service for geocoding addresses, designed for integration with real estate data pipelines.

## 🚀 Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## ⚙️ Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and fill in your API token and folder paths as needed.
   - `INPUT_DIR`: directory with JSON files to geocode
   - `PROCESSED_DIR`: directory where processed files will be moved
   - `REPROCESS_DIR`: directory for items that could not be geocoded


## 📥 Input Fields

To generate longitude and latitude, provide the following fields in your data:

- `endereco` (address) 🏠 **[required]**
- `localidade` (city/locality) 🏙️ **[required]**
- `estado` (state) 🗺️ **[required]**

**Optional recommended ideas for address fields:**
- `cep` (postal code) 🏷️
- `numero` (street number) 🔢
- `complemento` (address complement) 📝

They are not included in this service, but you can use them to improve the geocoding results.
The more details you provide, the more accurate the geocoding!

The worker performs up to three geocoding attempts for each item:
1. address + locality + state
2. address + state
3. locality + state

Items still without coordinates are stored in a file prefixed with `reprocessar_` inside `REPROCESS_DIR` for later inspection.

## ▶️ Usage

To start the worker:

```bash
python worker.py
```

If you later expose a script entrypoint (e.g., via `setup.py` or `pyproject.toml`):

```bash
geocode
```
