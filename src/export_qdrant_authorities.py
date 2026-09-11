import csv
import os
import re
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv
from qdrant_client import QdrantClient


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data/frozen/neon_case_registry_2026-08-19.csv"
OUTPUT_PATH = ROOT / "data/frozen/qdrant_authorities_2026-08-19.csv"
COLLECTION = "legal_cases"

load_dotenv(ROOT / ".env")

client = QdrantClient(
    url=os.environ["QDRANT_URL"],
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=120,
)


def normalise_title(value):
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


# Load citation information exported from Neon.
registry_by_id = {}
registry_by_title = {}

with REGISTRY_PATH.open("r", encoding="utf-8-sig", newline="") as stream:
    for row in csv.DictReader(stream):
        case_id = (row.get("case_id") or "").strip()
        title = (row.get("title") or "").strip()

        if case_id:
            registry_by_id[case_id] = row
        if title:
            registry_by_title.setdefault(normalise_title(title), row)


# Collect all Qdrant chunks by case.
cases = defaultdict(
    lambda: {
        "title": "",
        "source_url": "",
        "chunks": [],
    }
)

offset = None
point_count = 0
skipped = 0

while True:
    points, offset = client.scroll(
        collection_name=COLLECTION,
        limit=256,
        offset=offset,
        with_payload=True,
        with_vectors=False,
    )

    for point in points:
        payload = point.payload or {}
        metadata = payload.get("metadata") or {}

        case_id = str(payload.get("case_id") or "").strip()
        content = str(payload.get("content") or "").strip()

        if not case_id or not content:
            skipped += 1
            continue

        chunk_id = str(payload.get("chunk_id") or point.id)
        title = str(metadata.get("title") or "").strip()
        source_url = str(
            metadata.get("document_url")
            or metadata.get("source_filename")
            or ""
        ).strip()

        record = cases[case_id]

        if title and not record["title"]:
            record["title"] = title
        if source_url and not record["source_url"]:
            record["source_url"] = source_url

        record["chunks"].append((chunk_id, content))
        point_count += 1

    if point_count and point_count % 5000 < len(points):
        print(f"Processed {point_count:,} text chunks...")

    if offset is None:
        break


# Write one authoritative-text row per case.
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

fieldnames = [
    "case_id",
    "title",
    "citation",
    "authoritative_text",
    "source_url",
    "source_paragraphs",
]

missing_registry = 0
missing_citation = 0

with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=fieldnames)
    writer.writeheader()

    for case_id, record in sorted(cases.items()):
        registry = registry_by_id.get(case_id)

        if registry is None and record["title"]:
            registry = registry_by_title.get(
                normalise_title(record["title"])
            )

        if registry is None:
            registry = {}
            missing_registry += 1

        title = (
            registry.get("title")
            or record["title"]
            or ""
        ).strip()

        citation = (registry.get("citation") or "").strip()
        if not citation:
            missing_citation += 1

        source_url = (
            registry.get("source_url")
            or record["source_url"]
            or ""
        ).strip()

        # Sort chunks and remove duplicate text.
        unique_chunks = []
        seen_text = set()
        chunk_ids = []

        for chunk_id, content in sorted(
            record["chunks"],
            key=lambda item: item[0],
        ):
            if content in seen_text:
                continue

            seen_text.add(content)
            chunk_ids.append(chunk_id)
            unique_chunks.append(content)

        writer.writerow(
            {
                "case_id": case_id,
                "title": title,
                "citation": citation,
                "authoritative_text": "\n\n".join(unique_chunks),
                "source_url": source_url,
                "source_paragraphs": "; ".join(chunk_ids),
            }
        )

print(f"Exported {len(cases):,} cases from {point_count:,} chunks.")
print(f"Skipped chunks without case_id/content: {skipped:,}")
print(f"Cases not matched to Neon registry: {missing_registry:,}")
print(f"Cases without citation metadata: {missing_citation:,}")
print(f"Output: {OUTPUT_PATH}")