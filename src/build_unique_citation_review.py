import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILENAME = "citation_retrieval_verification_115.csv"

OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "processed"
OUTPUT_CSV = OUTPUT_DIRECTORY / "unique_citation_review.csv"
OUTPUT_JSON = OUTPUT_DIRECTORY / "unique_citation_review.json"


def find_file(filename):
    matches = list(PROJECT_ROOT.rglob(filename))

    if not matches:
        raise FileNotFoundError(
            f"Cannot find {filename} inside:\n{PROJECT_ROOT}"
        )

    return sorted(
        matches,
        key=lambda path: len(path.parts)
    )[0]


def read_csv(path):
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        return list(csv.DictReader(file))


def normalize(value):
    text = str(value or "").lower()
    text = text.replace("&", " and ")
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r"\bv\.", " v ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)

    return re.sub(r"\s+", " ", text).strip()


def extract_case_name(value):
    text = str(value or "")

    text = re.sub(
        r"\[\d{4}\].*$",
        "",
        text
    ).strip()

    text = re.sub(
        r"\(\d{4}\).*$",
        "",
        text
    ).strip()

    has_case_pattern = (
        re.search(r"\bv\.?\s", text, re.IGNORECASE)
        or text.lower().startswith("re ")
    )

    if not has_case_pattern:
        return ""

    normalized = normalize(text)

    normalized = re.sub(
        r"\b(?:and)?\s*(?:anor|another|ors|others)\b",
        " ",
        normalized
    )

    normalized = re.sub(
        r"\bcase\s+c\s+\d+\s+\d+\b$",
        "",
        normalized
    )

    return re.sub(
        r"\s+",
        " ",
        normalized
    ).strip()


def build_authority_key(row):
    matching_citation = (
        row.get("citation_used_for_matching")
        or row.get("citation")
        or ""
    )

    case_name = extract_case_name(
        matching_citation
    )

    if case_name:
        return f"case:{case_name}"

    return (
        f"{row.get('citation_type', 'reference')}:"
        f"{normalize(matching_citation)}"
    )


def joined_unique(values):
    cleaned = sorted({
        str(value).strip()
        for value in values
        if str(value).strip()
    })

    return " || ".join(cleaned)


def main():
    input_path = find_file(INPUT_FILENAME)
    rows = read_csv(input_path)

    grouped_rows = defaultdict(list)

    for row in rows:
        authority_key = build_authority_key(row)
        grouped_rows[authority_key].append(row)

    review_rows = []

    for authority_key, records in grouped_rows.items():
        display_counter = Counter(
            record.get(
                "citation_used_for_matching",
                record.get("citation", "")
            )
            for record in records
        )

        authority_display = (
            display_counter.most_common(1)[0][0]
        )

        status_counter = Counter(
            record["verification_status"]
            for record in records
        )

        real_records = [
            record
            for record in records
            if record["input_type"] == "real"
        ]

        synthetic_records = [
            record
            for record in records
            if record["input_type"] == "synthetic"
        ]

        mismatch_mentions = sum(
            count
            for status, count in status_counter.items()
            if "mismatch" in status
        )

        conflict_mentions = sum(
            count
            for status, count in status_counter.items()
            if "conflict" in status
        )

        invalid_id_mentions = sum(
            1
            for record in records
            if record.get(
                "invalid_source_case_ids",
                ""
            ).strip()
        )

        not_found_mentions = status_counter.get(
            "not_found_in_corpus_registry",
            0
        )

        corpus_not_retrieved_mentions = (
            status_counter.get(
                "in_corpus_not_retrieved",
                0
            )
        )

        retrieved_mentions = status_counter.get(
            "retrieved_and_cited",
            0
        )

        if (
            mismatch_mentions > 0
            or conflict_mentions > 0
            or invalid_id_mentions > 0
        ):
            review_priority = "high"

        elif (
            not_found_mentions > 0
            or corpus_not_retrieved_mentions > 0
        ):
            review_priority = "medium"

        else:
            review_priority = "low"

        manual_review_needed = (
            "yes"
            if review_priority in {"high", "medium"}
            else "no"
        )

        review_rows.append({
            "authority_key": authority_key,
            "authority": authority_display,
            "citation_type": records[0][
                "citation_type"
            ],
            "mention_count": len(records),
            "judgment_count": len({
                record["draft_id"]
                for record in records
            }),
            "real_mentions": len(real_records),
            "real_judgment_count": len({
                record["draft_id"]
                for record in real_records
            }),
            "synthetic_mentions": len(
                synthetic_records
            ),
            "synthetic_judgment_count": len({
                record["draft_id"]
                for record in synthetic_records
            }),
            "retrieved_and_cited_mentions": (
                retrieved_mentions
            ),
            "corpus_not_retrieved_mentions": (
                corpus_not_retrieved_mentions
            ),
            "not_found_in_registry_mentions": (
                not_found_mentions
            ),
            "source_id_mismatch_mentions": (
                mismatch_mentions
            ),
            "citation_conflict_mentions": (
                conflict_mentions
            ),
            "invalid_source_id_mentions": (
                invalid_id_mentions
            ),
            "statuses_observed": " || ".join(
                f"{status}: {count}"
                for status, count
                in sorted(status_counter.items())
            ),
            "citation_variants": joined_unique(
                record["citation"]
                for record in records
            ),
            "matched_retrieved_cases": joined_unique(
                record.get(
                    "matched_retrieved_case_title",
                    ""
                )
                for record in records
            ),
            "matched_corpus_cases": joined_unique(
                record.get(
                    "matched_corpus_case_title",
                    ""
                )
                for record in records
            ),
            "invalid_source_ids": joined_unique(
                record.get(
                    "invalid_source_case_ids",
                    ""
                )
                for record in records
            ),
            "review_priority": review_priority,
            "manual_review_needed": (
                manual_review_needed
            ),
            "case_exists_external": "",
            "citation_correct_external": "",
            "authoritative_source_url": "",
            "review_notes": "",
        })

    priority_order = {
        "high": 0,
        "medium": 1,
        "low": 2,
    }

    review_rows.sort(
        key=lambda row: (
            priority_order[row["review_priority"]],
            -row["mention_count"],
            row["authority"].lower(),
        )
    )

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    if review_rows:
        with OUTPUT_CSV.open(
            "w",
            encoding="utf-8-sig",
            newline=""
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=list(review_rows[0].keys())
            )

            writer.writeheader()
            writer.writerows(review_rows)

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            review_rows,
            file,
            indent=2,
            ensure_ascii=False
        )

    priority_counts = Counter(
        row["review_priority"]
        for row in review_rows
    )

    print()
    print("Unique citation review table completed")
    print("--------------------------------------")
    print(f"Original citation records: {len(rows)}")
    print(
        f"Unique authority groups: {len(review_rows)}"
    )

    print("\nReview priorities:")

    for priority in ["high", "medium", "low"]:
        print(
            f"- {priority}: "
            f"{priority_counts.get(priority, 0)}"
        )

    print(f"\nCSV output: {OUTPUT_CSV}")
    print(f"JSON output: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()