import csv
import json
import re
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

CITATIONS_FILENAME = "judgment_citations_59.csv"
LINKAGE_FILENAME = "retrieval_linkage_59.csv"
CORPUS_FILENAME = "qdrant_corpus_registry_2026-08-14.csv"

OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "processed"
OUTPUT_CSV = OUTPUT_DIRECTORY / "citation_retrieval_verification_115.csv"
OUTPUT_JSON = OUTPUT_DIRECTORY / "citation_retrieval_verification_115.json"


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


def split_joined(value):
    return [
        part.strip()
        for part in str(value or "").split("||")
        if part.strip()
    ]


def normalize(value):
    text = str(value or "").lower()
    text = text.replace("&", " and ")
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r"\bv\.", " v ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)

    return re.sub(r"\s+", " ", text).strip()


def extract_identifiers(value):
    text = str(value or "")

    patterns = [
        r"\[\d{4}\]\s+(?:UKSC|UKHL|UKPC)\s+\d+",
        r"\[\d{4}\]\s+EWCA\s+(?:Civ|Crim)\s+\d+",
        r"\[\d{4}\]\s+EWHC\s+\d+(?:\s+\([^)]+\))?",
        (
            r"\[\d{4}\]\s+\d+\s+"
            r"(?:WLR|AC|Ch|QB|ICR|All\s+ER|P&CR)\s+\d+"
        ),
        (
            r"\(\d{4}\)\s+\d+\s+"
            r"(?:WLR|AC|Ch|QB|ICR|All\s+ER|P&CR)\s+\d+"
        ),
        (
            r"[\[(]\d{4}[\])]\s+EWCA\s+"
            r"(?:Civ|Crim)\s+\d+"
        ),
    ]

    identifiers = []

    for pattern in patterns:
        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        for match in matches:
            normalized = normalize(match)

            if normalized and normalized not in identifiers:
                identifiers.append(normalized)

    return identifiers


def case_name(value):
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

    if (
        re.fullmatch(r"[\d\sA-Za-z&()]+", text)
        and not re.search(r"\bv\.?\s", text, re.IGNORECASE)
    ):
        return ""

    normalized = normalize(text)

    normalized = re.sub(
        r"\b(?:and|&)?\s*(?:anor|another|ors|others)\b",
        " ",
        normalized
    )

    return re.sub(r"\s+", " ", normalized).strip()


def text_match(citation, record):
    searchable = " ".join([
        str(record.get("title", "")),
        str(record.get("neutral_citation", "")),
        str(record.get("citation", "")),
    ])

    citation_identifiers = extract_identifiers(citation)
    record_identifiers = extract_identifiers(searchable)

    for identifier in citation_identifiers:
        if identifier in record_identifiers:
            return "citation_identifier", 1.0

    citation_name = case_name(citation)
    record_name = case_name(record.get("title", ""))

    if citation_name and record_name:
        if citation_name == record_name:
            return "exact_case_name", 1.0

        if (
            len(citation_name) >= 12
            and (
                citation_name in record_name
                or record_name in citation_name
            )
        ):
            return "contained_case_name", 0.96

        # Do not use fuzzy matching when a formal citation
        # number is present. This prevents false matches.
        if citation_identifiers:
            return "", 0.0

        score = SequenceMatcher(
            None,
            citation_name,
            record_name
        ).ratio()

        if score >= 0.94:
            return "fuzzy_case_name", round(score, 4)

    return "", 0.0


def best_text_match(citation, records):
    best_record = None
    best_method = ""
    best_score = 0.0

    for record in records:
        method, score = text_match(citation, record)

        if score > best_score:
            best_record = record
            best_method = method
            best_score = score

    return best_record, best_method, best_score


def identifier_family(identifier):
    families = [
        "ewca civ",
        "ewca crim",
        "ewhc",
        "uksc",
        "ukhl",
        "ukpc",
        "wlr",
        "all er",
        "p cr",
        "icr",
        "ac",
        "ch",
        "qb",
    ]

    for family in families:
        if family in identifier:
            return family

    return "other"


def has_identifier_conflict(citation, record):
    citation_identifiers = set(
        extract_identifiers(citation)
    )

    record_text = " ".join([
        str(record.get("title", "")),
        str(record.get("neutral_citation", "")),
        str(record.get("citation", "")),
    ])

    record_identifiers = set(
        extract_identifiers(record_text)
    )

    citation_by_family = {}
    record_by_family = {}

    for identifier in citation_identifiers:
        family = identifier_family(identifier)

        citation_by_family.setdefault(
            family,
            set()
        ).add(identifier)

    for identifier in record_identifiers:
        family = identifier_family(identifier)

        record_by_family.setdefault(
            family,
            set()
        ).add(identifier)

    shared_families = (
        set(citation_by_family)
        & set(record_by_family)
    )

    return any(
        citation_by_family[family].isdisjoint(
            record_by_family[family]
        )
        for family in shared_families
    )


def main():
    citations_path = find_file(CITATIONS_FILENAME)
    linkage_path = find_file(LINKAGE_FILENAME)
    corpus_path = find_file(CORPUS_FILENAME)

    citations = read_csv(citations_path)
    linkages = read_csv(linkage_path)
    corpus_rows = read_csv(corpus_path)

    linkage_by_draft = {
        row["draft_id"]: row
        for row in linkages
    }

    corpus_records = [
        {
            "id": row.get("qdrant_point_id", ""),
            "case_id": row.get("case_id", ""),
            "title": row.get("title", ""),
            "neutral_citation": row.get(
                "neutral_citation",
                ""
            ),
            "citation": row.get("citation", ""),
        }
        for row in corpus_rows
    ]

    corpus_ids = {
        identifier
        for row in corpus_records
        for identifier in (
            row["id"],
            row["case_id"]
        )
        if identifier
    }

    # Build aliases for citations that appear elsewhere
    # with both a case name and citation number.
    alias_candidates = {}

    for citation_row in citations:
        full_citation = citation_row["citation"]

        if not case_name(full_citation):
            continue

        for identifier in extract_identifiers(
            full_citation
        ):
            alias_candidates.setdefault(
                identifier,
                Counter()
            )[full_citation] += 1

    identifier_aliases = {
        identifier: counts.most_common(1)[0][0]
        for identifier, counts
        in alias_candidates.items()
    }

    results = []

    for citation_row in citations:
        draft_id = citation_row["draft_id"]

        if draft_id not in linkage_by_draft:
            raise ValueError(
                f"No retrieval linkage found for {draft_id}"
            )

        linkage = linkage_by_draft[draft_id]

        retrieved_ids = split_joined(
            linkage["retrieved_case_ids"]
        )

        retrieved_titles = split_joined(
            linkage["retrieved_case_titles"]
        )

        retrieved_records = [
            {
                "id": retrieved_id,
                "case_id": "",
                "title": retrieved_title,
                "neutral_citation": "",
                "citation": "",
            }
            for retrieved_id, retrieved_title
            in zip(retrieved_ids, retrieved_titles)
        ]

        citation_for_matching = citation_row["citation"]

        if not case_name(citation_for_matching):
            for identifier in extract_identifiers(
                citation_for_matching
            ):
                if identifier in identifier_aliases:
                    citation_for_matching = (
                        identifier_aliases[identifier]
                    )
                    break

        explicit_ids = split_joined(
            citation_row["source_case_ids"]
        )

        valid_explicit_ids = [
            source_id
            for source_id in explicit_ids
            if source_id in retrieved_ids
        ]

        invalid_explicit_ids = [
            source_id
            for source_id in explicit_ids
            if (
                source_id not in retrieved_ids
                and source_id not in corpus_ids
            )
        ]

        explicit_records = [
            record
            for record in retrieved_records
            if record["id"] in valid_explicit_ids
        ]

        (
            explicit_match,
            explicit_method,
            explicit_score
        ) = best_text_match(
            citation_for_matching,
            explicit_records
        )

        (
            retrieved_match,
            retrieved_method,
            retrieved_score
        ) = best_text_match(
            citation_for_matching,
            retrieved_records
        )

        (
            corpus_match,
            corpus_method,
            corpus_score
        ) = best_text_match(
            citation_for_matching,
            corpus_records
        )

        selected_retrieval_match = (
            explicit_match or retrieved_match
        )

        retrieval_identifier_conflict = (
            has_identifier_conflict(
                citation_for_matching,
                selected_retrieval_match
            )
            if selected_retrieval_match
            else False
        )

        corpus_identifier_conflict = (
            has_identifier_conflict(
                citation_for_matching,
                corpus_match
            )
            if corpus_match
            else False
        )

        if citation_row["citation_type"] != "case_law":
            status = "not_applicable_non_case_reference"
            manual_review = "no"
            reason = (
                "Legislation or procedural rule; "
                "not tested as a case citation."
            )

        elif (
            valid_explicit_ids
            and explicit_match
            and retrieval_identifier_conflict
        ):
            status = "retrieved_case_name_citation_conflict"
            manual_review = "yes"
            reason = (
                "The source ID points to the named retrieved "
                "case, but its citation identifier conflicts "
                "with the generated citation."
            )

        elif valid_explicit_ids and explicit_match:
            status = "retrieved_and_cited"
            manual_review = "no"
            reason = (
                "The explicit source ID points to a retrieved "
                "record matching the cited authority."
            )

        elif (
            valid_explicit_ids
            and retrieved_match
            and retrieval_identifier_conflict
        ):
            status = "retrieved_case_name_citation_conflict"
            manual_review = "yes"
            reason = (
                "The named case appears in the retrieval, but "
                "its citation identifier conflicts and the "
                "source ID points elsewhere."
            )

        elif valid_explicit_ids and retrieved_match:
            status = (
                "retrieved_text_match_source_id_mismatch"
            )
            manual_review = "yes"
            reason = (
                "The authority appears in the retrieval, but "
                "the explicit source ID points to a different "
                "case."
            )

        elif valid_explicit_ids:
            status = "retrieved_id_citation_mismatch"
            manual_review = "yes"
            reason = (
                "The source ID is present in the retrieval, "
                "but it points to a record that does not match "
                "the generated citation."
            )

        elif (
            retrieved_match
            and retrieval_identifier_conflict
        ):
            status = "retrieved_case_name_citation_conflict"
            manual_review = "yes"
            reason = (
                "The case name appears in the retrieval, but "
                "the citation identifier conflicts with the "
                "retrieved record."
            )

        elif retrieved_match:
            status = "retrieved_and_cited"

            manual_review = (
                "yes"
                if invalid_explicit_ids
                else "no"
            )

            reason = (
                "Citation text matches a case in the linked "
                "retrieval."
            )

            if invalid_explicit_ids:
                reason += (
                    " The supplied source ID is invalid."
                )

        elif (
            corpus_match
            and corpus_identifier_conflict
        ):
            status = "corpus_case_name_citation_conflict"
            manual_review = "yes"
            reason = (
                "The case name appears in the corpus registry, "
                "but its citation identifier conflicts with "
                "the corpus record."
            )

        elif corpus_match:
            status = "in_corpus_not_retrieved"
            manual_review = "yes"
            reason = (
                "The citation matches a corpus case but not "
                "the retrieval linked to this judgment."
            )

        else:
            status = "not_found_in_corpus_registry"
            manual_review = "yes"
            reason = (
                "No standalone case-title or citation match "
                "was found in the linked retrieval or corpus "
                "registry."
            )

            if invalid_explicit_ids:
                reason += (
                    " The supplied source ID is invalid."
                )

        selected_match_method = (
            f"explicit_source_id+{explicit_method}"
            if explicit_match
            else retrieved_method
            if retrieved_match
            else corpus_method
            if corpus_match
            else "no_match"
        )

        selected_match_score = (
            explicit_score
            if explicit_match
            else retrieved_score
            if retrieved_match
            else corpus_score
            if corpus_match
            else 0.0
        )

        matched_retrieved_record = (
            explicit_match
            or retrieved_match
            or {}
        )

        results.append({
            **citation_row,
            "citation_used_for_matching": (
                citation_for_matching
            ),
            "search_id": linkage["search_id"],
            "verification_status": status,
            "citation_in_linked_retrieval": (
                "yes"
                if (
                    explicit_match
                    or retrieved_match
                )
                else "no"
            ),
            "citation_in_corpus_registry": (
                "yes"
                if (
                    corpus_match
                    or explicit_match
                    or retrieved_match
                )
                else "no"
            ),
            "match_method": selected_match_method,
            "match_score": selected_match_score,
            "matched_retrieved_case_id": (
                matched_retrieved_record.get(
                    "id",
                    ""
                )
            ),
            "matched_retrieved_case_title": (
                matched_retrieved_record.get(
                    "title",
                    ""
                )
            ),
            "explicit_source_case_id": " || ".join(
                valid_explicit_ids
            ),
            "explicit_source_case_title": " || ".join(
                record["title"]
                for record in explicit_records
            ),
            "matched_corpus_case_id": (
                corpus_match.get("case_id", "")
                if corpus_match
                else ""
            ),
            "matched_corpus_case_title": (
                corpus_match.get("title", "")
                if corpus_match
                else ""
            ),
            "invalid_source_case_ids": " || ".join(
                invalid_explicit_ids
            ),
            "citation_identifier_conflict": (
                "yes"
                if (
                    retrieval_identifier_conflict
                    or corpus_identifier_conflict
                )
                else "no"
            ),
            "manual_review_required": manual_review,
            "review_reason": reason,
        })

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    if results:
        with OUTPUT_CSV.open(
            "w",
            encoding="utf-8-sig",
            newline=""
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=list(results[0].keys())
            )

            writer.writeheader()
            writer.writerows(results)

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False
        )

    status_counts = Counter(
        row["verification_status"]
        for row in results
    )

    invalid_id_count = sum(
        1
        for row in results
        if row["invalid_source_case_ids"]
    )

    manual_review_count = sum(
        1
        for row in results
        if row["manual_review_required"] == "yes"
    )

    print()
    print("Citation retrieval verification completed")
    print("-----------------------------------------")
    print(f"Citation records checked: {len(results)}")
    print(f"Corpus registry cases: {len(corpus_records)}")
    print(
        f"Manual-review records: {manual_review_count}"
    )
    print(
        f"Records containing invalid source IDs: "
        f"{invalid_id_count}"
    )

    print("\nVerification statuses:")

    for status, count in sorted(
        status_counts.items()
    ):
        print(f"- {status}: {count}")

    print(f"\nCSV output: {OUTPUT_CSV}")
    print(f"JSON output: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()