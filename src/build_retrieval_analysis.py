import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DRAFTS_FILENAME = "draft_decisions_59_2026-08-14.json"
SEARCHES_FILENAME = "semantic_searches_66_2026-08-14.json"

OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "processed"
OUTPUT_CSV = OUTPUT_DIRECTORY / "retrieval_linkage_59.csv"
OUTPUT_JSON = OUTPUT_DIRECTORY / "retrieval_linkage_59.json"


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


def parse_datetime(value):
    cleaned = str(value).strip()
    cleaned = cleaned.replace("T", " ")
    cleaned = cleaned.rstrip("Z")

    if "." in cleaned:
        main_part, fractional_part = cleaned.split(".", 1)

        fractional_digits = "".join(
            character
            for character in fractional_part
            if character.isdigit()
        )

        fractional_digits = fractional_digits[:6].ljust(6, "0")
        cleaned = f"{main_part}.{fractional_digits}"

        return datetime.strptime(
            cleaned,
            "%Y-%m-%d %H:%M:%S.%f"
        )

    return datetime.strptime(
        cleaned,
        "%Y-%m-%d %H:%M:%S"
    )


def select_search_for_draft(draft, candidate_searches):
    draft_time = parse_datetime(draft["generated_at"])

    searches_with_times = [
        (
            search,
            parse_datetime(search["searched_at"])
        )
        for search in candidate_searches
    ]

    searches_before_draft = [
        (search, search_time)
        for search, search_time in searches_with_times
        if search_time <= draft_time
    ]

    if searches_before_draft:
        selected_search, selected_time = max(
            searches_before_draft,
            key=lambda item: item[1]
        )
        match_method = "latest_search_before_draft"
    else:
        selected_search, selected_time = min(
            searches_with_times,
            key=lambda item: abs(
                (draft_time - item[1]).total_seconds()
            )
        )
        match_method = "nearest_search_no_prior_match"

    time_gap_seconds = (
        draft_time - selected_time
    ).total_seconds()

    return selected_search, match_method, time_gap_seconds


def main():
    drafts_path = find_file(DRAFTS_FILENAME)
    searches_path = find_file(SEARCHES_FILENAME)

    drafts = load_json(drafts_path)
    searches = load_json(searches_path)

    searches_by_skeleton_id = defaultdict(list)

    for search in searches:
        skeleton_id = search.get("skeleton_arguments_id")

        if skeleton_id:
            searches_by_skeleton_id[skeleton_id].append(search)

    csv_rows = []
    json_rows = []
    unmatched_drafts = []

    for draft in drafts:
        skeleton_id = draft.get("skeleton_arguments_id")
        candidate_searches = searches_by_skeleton_id.get(
            skeleton_id,
            []
        )

        if not candidate_searches:
            unmatched_drafts.append(draft.get("draft_id"))
            continue

        (
            selected_search,
            match_method,
            time_gap_seconds
        ) = select_search_for_draft(
            draft,
            candidate_searches
        )

        similar_cases = parse_json_field(
            selected_search.get("similar_cases"),
            []
        )

        search_stats = parse_json_field(
            selected_search.get("search_stats"),
            {}
        )

        retrieved_case_ids = []
        retrieved_titles = []
        similarity_scores = []

        for retrieved_case in similar_cases:
            retrieved_case_ids.append(
                str(retrieved_case.get("id", ""))
            )

            retrieved_titles.append(
                str(retrieved_case.get("title", ""))
            )

            score = retrieved_case.get("similarity_score")

            if score is not None:
                similarity_scores.append(str(score))

        case_doc_id = str(
            draft.get("case_doc_id", "")
        )

        if case_doc_id.startswith("skeleton-args"):
            input_type = "synthetic"
        else:
            input_type = "real"

        csv_row = {
            "draft_id": draft.get("draft_id"),
            "skeleton_arguments_id": skeleton_id,
            "case_doc_id": case_doc_id,
            "input_type": input_type,
            "model_used": draft.get("model_used"),
            "generated_at": draft.get("generated_at"),
            "search_id": selected_search.get("search_id"),
            "searched_at": selected_search.get("searched_at"),
            "match_method": match_method,
            "search_to_draft_seconds": round(
                time_gap_seconds,
                3
            ),
            "search_type": selected_search.get("search_type"),
            "reported_total_results": (
                selected_search.get("total_results")
            ),
            "retrieved_cases_in_export": len(similar_cases),
            "average_similarity": (
                search_stats.get("avg_similarity")
            ),
            "top_retrieved_case": (
                retrieved_titles[0]
                if retrieved_titles
                else ""
            ),
            "top_similarity_score": (
                similarity_scores[0]
                if similarity_scores
                else ""
            ),
            "retrieved_case_ids": " || ".join(
                retrieved_case_ids
            ),
            "retrieved_case_titles": " || ".join(
                retrieved_titles
            ),
            "similarity_scores": " || ".join(
                similarity_scores
            ),
        }

        csv_rows.append(csv_row)

        json_rows.append({
            **csv_row,
            "retrieved_cases": similar_cases,
        })

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    if csv_rows:
        with OUTPUT_CSV.open(
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=list(csv_rows[0].keys())
            )
            writer.writeheader()
            writer.writerows(csv_rows)

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            json_rows,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("Retrieval linkage completed")
    print("---------------------------")
    print(f"Draft judgments loaded: {len(drafts)}")
    print(f"Semantic searches loaded: {len(searches)}")
    print(
        f"Drafts successfully matched: {len(csv_rows)}"
    )
    print(f"Unmatched drafts: {len(unmatched_drafts)}")
    print(f"CSV output: {OUTPUT_CSV}")
    print(f"JSON output: {OUTPUT_JSON}")

    if unmatched_drafts:
        print("\nUnmatched draft IDs:")

        for draft_id in unmatched_drafts:
            print(f"- {draft_id}")


if __name__ == "__main__":
    main()