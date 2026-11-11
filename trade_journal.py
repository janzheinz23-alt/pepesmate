"""CSV trade journal helpers. No broker or exchange execution."""


def append_journal_entry(path, asset, decision, notes=""):
    import csv
    from datetime import datetime, timezone
    from pathlib import Path

    file_path = Path(path)
    file_exists = file_path.exists()
    with file_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["timestamp_utc", "asset", "decision", "notes"]
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "asset": asset,
            "decision": decision,
            "notes": notes,
        })
