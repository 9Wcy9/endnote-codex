#!/usr/bin/env python3
"""Match a citation plan to EndNote records and write a temporary-citation audit."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


OUTPUT_FIELDS = [
    "citation_id",
    "location",
    "requested_title",
    "requested_doi",
    "matched_title",
    "record_number",
    "temporary_citation",
    "status",
    "notes",
]


def clean(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def normalize_title(value: Any) -> str:
    text = unicodedata.normalize("NFKC", clean(value)).casefold()
    text = re.sub(r"[\W_]+", " ", text, flags=re.UNICODE)
    return " ".join(text.split())


def normalize_doi(value: Any) -> str:
    doi = clean(value).lower()
    doi = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", doi)
    return doi.rstrip(" .")


def first_present(record: dict[str, Any], names: Iterable[str]) -> Any:
    for name in names:
        if name in record and clean(record[name]):
            return record[name]
    return ""


def first_author(record: dict[str, Any]) -> str:
    direct = clean(first_present(record, ("first_author", "author", "authors")))
    value = record.get("authors")
    if isinstance(value, list) and value:
        author = value[0]
        if isinstance(author, dict):
            return clean(author.get("family") or author.get("literal"))
        return clean(author).split(",", 1)[0]
    if direct:
        return direct.split(";", 1)[0].split(" and ", 1)[0].split(",", 1)[0]
    return ""


def canonical_record(raw: dict[str, Any]) -> dict[str, str]:
    return {
        "record_number": clean(
            first_present(raw, ("record_number", "record number", "record-number", "rec_number", "rec-number"))
        ),
        "title": clean(first_present(raw, ("title", "secondary_title", "reference_title"))),
        "doi": normalize_doi(first_present(raw, ("doi", "DOI"))),
        "author": first_author(raw),
        "year": clean(first_present(raw, ("year", "publication_year", "date")))[:4],
    }


def load_records(path: Path) -> list[dict[str, str]]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        with path.open("r", encoding="utf-8-sig") as handle:
            payload = json.load(handle)
        raw_records = payload.get("records") if isinstance(payload, dict) else payload
        if not isinstance(raw_records, list):
            raise ValueError("JSON must be an array or an object with a 'records' array")
    elif suffix in {".csv", ".tsv"}:
        delimiter = "\t" if suffix == ".tsv" else ","
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            raw_records = list(csv.DictReader(handle, delimiter=delimiter))
    else:
        raise ValueError("library records must be JSON, CSV, or TSV")

    records = [canonical_record(record) for record in raw_records if isinstance(record, dict)]
    return [record for record in records if any(record.values())]


def load_plan(path: Path) -> list[dict[str, str]]:
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter=delimiter))
    if not rows:
        raise ValueError("citation plan is empty")
    return [{key: clean(value) for key, value in row.items()} for row in rows]


def temporary_citation(record: dict[str, str]) -> str:
    missing = [key for key in ("record_number", "author", "year") if not record[key]]
    if missing:
        raise ValueError("matched record lacks " + ", ".join(missing))
    return f"{{{record['author']}, {record['year']} #{record['record_number']}}}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("library_records", type=Path)
    parser.add_argument("citation_plan", type=Path)
    parser.add_argument("output_audit", type=Path)
    args = parser.parse_args()

    try:
        records = load_records(args.library_records)
        plan = load_plan(args.citation_plan)
    except (OSError, csv.Error, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    by_doi: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_title: dict[str, list[dict[str, str]]] = defaultdict(list)
    for record in records:
        if record["doi"]:
            by_doi[record["doi"]].append(record)
        title_key = normalize_title(record["title"])
        if title_key:
            by_title[title_key].append(record)

    output: list[dict[str, str]] = []
    counts = defaultdict(int)
    for index, row in enumerate(plan, start=1):
        requested_title = clean(row.get("title") or row.get("requested_title"))
        requested_doi = normalize_doi(row.get("doi") or row.get("requested_doi"))
        citation_id = clean(row.get("citation_id")) or f"C{index:03d}"
        location = clean(row.get("location"))

        if requested_doi:
            candidates = by_doi.get(requested_doi, [])
            match_basis = "DOI"
        elif requested_title:
            candidates = by_title.get(normalize_title(requested_title), [])
            match_basis = "title"
        else:
            candidates = []
            match_basis = ""

        matched_title = ""
        record_number = ""
        citation = ""
        notes = ""

        if not requested_doi and not requested_title:
            status = "missing"
            notes = "citation plan row has neither DOI nor title"
        elif len(candidates) == 0:
            status = "missing"
            notes = f"no exact {match_basis} match in supplied EndNote records"
        elif len(candidates) > 1:
            status = "ambiguous"
            notes = f"{len(candidates)} exact {match_basis} matches in supplied EndNote records"
        else:
            record = candidates[0]
            matched_title = record["title"]
            record_number = record["record_number"]
            try:
                citation = temporary_citation(record)
                status = "matched"
                notes = f"unique exact {match_basis} match"
            except ValueError as exc:
                status = "missing"
                notes = str(exc)

        counts[status] += 1
        output.append(
            {
                "citation_id": citation_id,
                "location": location,
                "requested_title": requested_title,
                "requested_doi": requested_doi,
                "matched_title": matched_title,
                "record_number": record_number,
                "temporary_citation": citation,
                "status": status,
                "notes": notes,
            }
        )

    args.output_audit.parent.mkdir(parents=True, exist_ok=True)
    with args.output_audit.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(output)

    print(
        "processed " + str(len(output)) + " citation location(s): "
        + ", ".join(f"{status}={counts[status]}" for status in ("matched", "ambiguous", "missing"))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
