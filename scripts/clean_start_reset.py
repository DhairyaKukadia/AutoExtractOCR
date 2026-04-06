"""Hard reset script for a clean local prototype start.

What it does:
1) Deletes the current SQLite DB file.
2) Recreates schema.
3) Seeds core auth/template data.
4) Sets schema version.
5) (Optional) inserts one sample row for each of the 3 medical forms.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.data.database import SessionLocal, init_db, reset_runtime_state
from app.data.migrations import ensure_schema_version
from app.data.seed import seed_data
from scripts.seed_three_forms import main as seed_three_forms_main


def main() -> None:
    parser = argparse.ArgumentParser(description='Reset local AutoExtractOCR runtime state')
    parser.add_argument('--with-sample-forms', action='store_true', help='Insert one sample for each selected medical form')
    parser.add_argument('--remove-logs', action='store_true', help='Also clear log files under logs/')
    args = parser.parse_args()

    reset_runtime_state(remove_logs=args.remove_logs)
    init_db()

    session = SessionLocal()
    try:
        seed_data(session)
        ensure_schema_version(session)
    finally:
        session.close()

    if args.with_sample_forms:
        seed_three_forms_main()

    print('Clean start reset completed successfully.')


if __name__ == '__main__':
    main()
