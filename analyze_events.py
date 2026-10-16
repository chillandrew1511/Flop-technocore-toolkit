
#!/usr/bin/env python3
"""
Technocore Toolkit — Event Analytics

Analyze user-provided JSON or CSV event data.
This script does not connect to Technocore or submit transactions.
"""

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


EVENT_KEYS = ("event_type", "type", "event")
TIME_KEYS = ("timestamp", "created_at", "time")


def load_events(path: Path) -> list[dict]:
    """Load events from a JSON or CSV file."""
    suffix = path.suffix.lower()

    if suffix == ".json":
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, dict):
            data = data.get("events", [data])

        if not isinstance(data, list):
            raise ValueError("JSON must contain an event list or an object.")

        if not all(isinstance(item, dict) for item in data):
            raise ValueError("Every event must be a JSON object.")

        return data

    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            return list(csv.DictReader(file))

    raise ValueError("Unsupported file format. Use .json or .csv.")


def first_value(event: dict, keys: tuple[str, ...]):
    """Return the first non-empty value matching the provided keys."""
    for key in keys:
        value = event.get(key)
        if value is not None and str(value).strip():
            return value
    return None


def parse_timestamp(value) -> datetime | None:
    """Parse common ISO-8601 timestamps or Unix timestamps."""
    if value is None:
        return None

    try:
        if isinstance(value, (int, float)):
            # Interpret numeric timestamps as Unix seconds.
            return datetime.fromtimestamp(value, tz=timezone.utc)

        text = str(value).strip()

        if text.isdigit():
            return datetime.fromtimestamp(int(text), tz=timezone.utc)

        if text.endswith("Z"):
            text = text[:-1] + "+00:00"

        parsed = datetime.fromisoformat(text)

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed.astimezone(timezone.utc)

    except (ValueError, OverflowError, OSError):
        return None


def analyze_events(events: list[dict]) -> dict:
    """Summarize event types and valid timestamps."""
    event_counts = Counter()
    timestamps = []
    missing_type = 0

    for event in events:
        event_type = first_value(event, EVENT_KEYS)

        if event_type is None:
            missing_type += 1
            event_type = "unknown"

        event_counts[str(event_type)] += 1

        timestamp = parse_timestamp(first_value(event, TIME_KEYS))
        if timestamp is not None:
            timestamps.append(timestamp)

    timestamps.sort()

    return {
        "total_events": len(events),
        "event_types": dict(sorted(event_counts.items())),
        "events_missing_type": missing_type,
        "valid_timestamps": len(timestamps),
        "invalid_or_missing_timestamps": len(events) - len(timestamps),
        "first_event_utc": (
            timestamps[0].isoformat() if timestamps else None
        ),
        "last_event_utc": (
            timestamps[-1].isoformat() if timestamps else None
        ),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "data_source": "user-provided file",
        "limitations": [
            "This report summarizes the supplied data only.",
            "It does not verify events against Technocore.",
            "It does not establish airdrop eligibility or rewards.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize event records from JSON or CSV."
    )
    parser.add_argument("input", help="Path to an input .json or .csv file")
    parser.add_argument(
        "-o",
        "--output",
        help="Optional path for the JSON report",
    )
    args = parser.parse_args()

    input_path = Path(args.input)

    try:
        events = load_events(input_path)
        report = analyze_events(events)
        output = json.dumps(report, indent=2, ensure_ascii=False)

        if args.output:
            output_path = Path(args.output)
            if output_path.resolve() == input_path.resolve():
                raise ValueError("Output path must differ from input path.")

            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output + "\n", encoding="utf-8")
            print(f"Report saved to: {output_path}")
        else:
            print(output)

        return 0

    except (OSError, json.JSONDecodeError, csv.Error, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
