# AutoExtractOCR

AutoExtractOCR is a Windows-first desktop prototype for medical-form OCR workflows.

## Features
- Local authentication (Admin / Operator) with hashed passwords (passlib PBKDF2-SHA256)
- OCR intake for PNG/JPG/JPEG/PDF
- OpenCV preprocessing + Tesseract OCR baseline
- Template-aware extraction strategy (generic + category/template patterns)
- Editable extracted fields before save
- Record details update workflow (review/edit/update after save)
- SQLite storage via SQLAlchemy
- Category-based record organization and search filters (patient, status, form type, date, record #)
- Audit log tracking + file-based application logging
- User management (create, activate/deactivate)

## Requirements
- Python 3.12 (target)
- Tesseract OCR installed and available in PATH
- Windows recommended (works on other OS for development)

## Install
### Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### macOS/Linux Bash
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
python run.py
```

## Run tests
```bash
python -m pytest -q
```

## Seeded users
- admin / `Admin@123`
- operator / `Operator@123`

Change these credentials immediately in non-demo environments.

## Tesseract on Windows
1. Install from UB Mannheim build or official binaries.
2. Add install directory (containing `tesseract.exe`) to PATH.
3. Restart terminal and run `tesseract --version`.

## Packaging (future)
You can package the prototype with PyInstaller:
```bash
pyinstaller --noconfirm --onefile --windowed run.py
```

## Three-form DB seed example
```bash
python scripts/seed_three_forms.py
```
