import csv
import json
import re
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DRAFTS_FILENAME = "draft_decisions_59_2026-08-14.json"

OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "processed"
OUTPUT_CSV = OUTPUT_DIRECTORY / "judgment_citations_59.csv"
OUTPUT_JSON = OUTPUT_DIRECTORY / "judgment_citations_59.json"


def find_file(filename):
    matches = list(PROJECT_ROOT.rglob(filename))

    if not matches:
        raise FileNotFoundError(
            f"Cannot find {filename} anywhere inside:\n{PROJECT_ROOT}"
        )

    return matches[0]


def load_json(path):
    with path.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def parse_json_field(value, default):
    if value is None:
        return default

    if isinstance(value, (dict, list)):
        return value

    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return default

    return default


def normalize_text(value):
    text = str(value or "").lower()

    text = (
        text.replace("’", "'")
        .replace("‘", "'")
        .replace("–", "-")
        .replace("—", "-")
    )

    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def classify_citation(citation):
    citation_lower = citation.lower()

    legislation_terms = [
        " act ",
        "regulation",
        "regulations",
        "rules",
        "practice direction",
        "cpr ",
        "section ",
        "article ",
    ]

    padded_citation = f" {citation_lower} "

    if any(
        term in padded_citation
        for term in legislation_terms
    ):
        return "legislation_or_rule"

    case_patterns = [
        r"\bv\.?\s+",
        r"^\s*re\s+",
        r"\[\d{4}\]\s+(uksc|ukhl|ukpc|ewca|ewhc|ukut|ukut|ukut)",
        r"\[\d{4}\]\s+\d+\s+(wlr|ac|ch|qb|all er|p&cr)",
    ]

    if any(
        re.search(pattern, citation, flags=re.IGNORECASE)
        for pattern in case_patterns
    ):
        return "case_law"

    return "other_reference"


def main():
    drafts_path = find_file(DRAFTS_FILENAME)
    drafts = load_json(drafts_path)

    citation_rows = []
    judgments_without_citations = []

    for draft in drafts:
        draft_decision = parse_json_field(
            draft.get("draft_decision"),
            {}
        )

        legal_framework = draft_decision.get(
            "legalFramework",
            {}
        ) or {}

        precedent_citations = legal_framework.get(
            "precedentCitations",
            []
        ) or []

        if not precedent_citations:
            judgments_without_citations.append(
                draft.get("draft_id")
            )

        for citation_index, citation_record in enumerate(
            precedent_citations,
            start=1
        ):
            citation_text = str(
                citation_record.get("citation", "")
            ).strip()

            source_cases = citation_record.get(
                "sourceCases",
                []
            ) or []

            source_case_ids = []
            source_case_titles = []
            source_case_citations = []

            for source_case in source_cases:
                case_id = str(
                    source_case.get("caseId", "")
                ).strip()

                case_title = str(
                    source_case.get("caseTitle", "")
                ).strip()

                source_citation = str(
                    source_case.get("citation", "")
                ).strip()

                if case_id:
                    source_case_ids.append(case_id)

                if case_title:
                    source_case_titles.append(case_title)

                if source_citation:
                    source_case_citations.append(
                        source_citation
                    )

            case_doc_id = str(
                draft.get("case_doc_id", "")
            )

            if case_doc_id.startswith("skeleton-args"):
                input_type = "synthetic"
            else:
                input_type = "real"

            citation_rows.append({
                "draft_id": draft.get("draft_id"),
                "skeleton_arguments_id": (
                    draft.get("skeleton_arguments_id")
                ),
                "case_doc_id": case_doc_id,
                "input_type": input_type,
                "model_used": draft.get("model_used"),
                "generated_at": draft.get("generated_at"),
                "citation_index": citation_index,
                "citation": citation_text,
                "citation_normalized": normalize_text(
                    citation_text
                ),
                "citation_type": classify_citation(
                    citation_text
                ),
                "pinpoint": citation_record.get(
                    "pinpoint",
                    ""
                ),
                "principle": citation_record.get(
                    "principle",
                    ""
                ),
                "application": citation_record.get(
                    "application",
                    ""
                ),
                "binding_authority": citation_record.get(
                    "bindingAuthority",
                    ""
                ),
                "linked_source_case_count": len(
                    source_case_ids
                ),
                "source_case_ids": " || ".join(
                    source_case_ids
                ),
                "source_case_titles": " || ".join(
                    source_case_titles
                ),
                "source_case_citations": " || ".join(
                    source_case_citations
                ),
            })

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    if citation_rows:
        with OUTPUT_CSV.open(
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=list(citation_rows[0].keys())
            )

            writer.writeheader()
            writer.writerows(citation_rows)

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            citation_rows,
            file,
            indent=2,
            ensure_ascii=False
        )

    citation_type_counts = Counter(
        row["citation_type"]
        for row in citation_rows
    )

    unique_citations = {
        row["citation_normalized"]
        for row in citation_rows
        if row["citation_normalized"]
    }

    linked_citations = sum(
        1
        for row in citation_rows
        if row["linked_source_case_count"] > 0
    )

    print()
    print("Judgment citation extraction completed")
    print("--------------------------------------")
    print(f"Judgments loaded: {len(drafts)}")
    print(f"Citation records extracted: {len(citation_rows)}")
    print(f"Unique normalized citations: {len(unique_citations)}")
    print(
        "Judgments without precedent citations: "
        f"{len(judgments_without_citations)}"
    )
    print(
        "Citations linked to a retrieved source case ID: "
        f"{linked_citations}"
    )

    print("\nCitation types:")

    for citation_type, count in sorted(
        citation_type_counts.items()
    ):
        print(f"- {citation_type}: {count}")

    print(f"\nCSV output: {OUTPUT_CSV}")
    print(f"JSON output: {OUTPUT_JSON}")

    if judgments_without_citations:
        print("\nJudgments without citations:")

        for draft_id in judgments_without_citations:
            print(f"- {draft_id}")


if __name__ == "__main__":
    main()