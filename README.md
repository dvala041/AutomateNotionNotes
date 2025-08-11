# AutomateNotionNotes

### Housekeeping before coding
1. Create virtual environment: `python -m venv fastapi-env`
2. On mac: `source fastapi-env/bin/activate`
3. Upgraded pip: `python -m pip install --upgrade pip`
4. Install dependencies: `pip install -r requirements.txt`
5. Run with `uvicorn app.main:app --reload`

### Managing Dependencies
- **Install a new package**: `pip install package_name`
- **Update requirements.txt**: `pip freeze > requirements.txt`
- **Install from requirements**: `pip install -r requirements.txt`

### API
- **/api/audio/extract: extracts audio from short form content and converts to an mp3 in specified directory
