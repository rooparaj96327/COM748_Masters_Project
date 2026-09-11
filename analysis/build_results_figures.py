from collections import Counter
from pathlib import Path
import csv

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED = PROJECT_ROOT / "data" / "processed"
OUTPUT = (
    PROJECT_ROOT
    / "outputs"
    / "experiments"
    / "citation-analysis"
)

SUMMARY_FILE = PROCESSED / "citation_review_summary.csv"
BREAKDOWN_FILE = PROCESSED / "citation_correctness_breakdown.csv"
VERIFICATION_FILE = (
    PROCESSED / "citation_retrieval_verification_115.csv"
)


COLORS = {
    "navy": "#17365D",
    "blue": "#4472C4",
    "green": "#2E8B57",
    "amber": "#E6A23C",
    "red": "#C44E52",
    "grey": "#6B7280",
    "light_blue": "#7EA6E0",
}


def read_csv(path):
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def save_figure(figure, filename):
    png_path = OUTPUT / f"{filename}.png"
    pdf_path = OUTPUT / f"{filename}.pdf"

    figure.savefig(
        png_path,
        dpi=300,
        bbox_inches="tight",
        facecolor="white",
    )
    figure.savefig(
        pdf_path,
        bbox_inches="tight",
        facecolor="white",
    )

    plt.close(figure)

    print(f"Created: {png_path}")
    print(f"Created: {pdf_path}")


def add_bar_labels(axis, bars, total):
    for bar in bars:
        value = int(bar.get_height())
        percentage = (value / total * 100) if total else 0

        axis.text(
            bar.get_x() + bar.get_width() / 2,
            value + max(total * 0.015, 0.2),
            f"{value}\n({percentage:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )


def create_correctness_figure(breakdown_rows):
    status_lookup = {
        row["citation_status"].strip().lower(): row
        for row in breakdown_rows
    }

    labels = ["Correct", "Incomplete", "Incorrect"]
    statuses = ["yes", "incomplete", "no"]

    values = [
        int(status_lookup[status]["authority_groups"])
        for status in statuses
    ]

    total = sum(values)

    figure, axis = plt.subplots(figsize=(7.2, 4.6))

    bars = axis.bar(
        labels,
        values,
        color=[
            COLORS["green"],
            COLORS["amber"],
            COLORS["red"],
        ],
        width=0.62,
    )

    add_bar_labels(axis, bars, total)

    axis.set_title(
        "External Verification of Citation Accuracy",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    axis.set_ylabel("Authority groups")
    axis.set_ylim(0, max(values) * 1.25)
    axis.grid(axis="y", linestyle="--", alpha=0.25)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)

    figure.tight_layout()
    save_figure(figure, "figure_1_citation_correctness")


def create_input_type_figure(summary):
    real_mentions = int(summary["real_case_mentions"])
    synthetic_mentions = int(summary["synthetic_case_mentions"])

    labels = ["Real-case inputs", "Synthetic-case inputs"]
    values = [real_mentions, synthetic_mentions]
    total = sum(values)

    figure, axis = plt.subplots(figsize=(7.2, 4.6))

    bars = axis.bar(
        labels,
        values,
        color=[COLORS["navy"], COLORS["light_blue"]],
        width=0.58,
    )

    add_bar_labels(axis, bars, total)

    axis.set_title(
        "Citation Mentions by Input Type",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    axis.set_ylabel("Extracted citation mentions")
    axis.set_ylim(0, max(values) * 1.22)
    axis.grid(axis="y", linestyle="--", alpha=0.25)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)

    figure.tight_layout()
    save_figure(figure, "figure_2_mentions_by_input_type")


def create_retrieval_figure(verification_rows):
    status_counts = Counter(
        row["verification_status"].strip()
        for row in verification_rows
    )

    ordered_statuses = [
        (
            "retrieved_and_cited",
            "Retrieved and cited",
            COLORS["green"],
        ),
        (
            "in_corpus_not_retrieved",
            "In corpus, not retrieved",
            COLORS["blue"],
        ),
        (
            "not_found_in_corpus_registry",
            "Not found in corpus registry",
            COLORS["red"],
        ),
        (
            "retrieved_id_citation_mismatch",
            "Retrieved ID/citation mismatch",
            COLORS["amber"],
        ),
        (
            "retrieved_case_name_citation_conflict",
            "Case-name/citation conflict",
            "#8E5EA2",
        ),
        (
            "not_applicable_non_case_reference",
            "Non-case reference",
            COLORS["grey"],
        ),
    ]

    labels = [item[1] for item in ordered_statuses]
    values = [status_counts[item[0]] for item in ordered_statuses]
    colors = [item[2] for item in ordered_statuses]

    total = sum(values)

    figure, axis = plt.subplots(figsize=(8.6, 5.3))

    bars = axis.barh(
        labels,
        values,
        color=colors,
        height=0.62,
    )

    axis.invert_yaxis()

    for bar, value in zip(bars, values):
        percentage = (value / total * 100) if total else 0

        axis.text(
            value + max(total * 0.008, 0.3),
            bar.get_y() + bar.get_height() / 2,
            f"{value} ({percentage:.1f}%)",
            va="center",
            fontsize=10,
            fontweight="bold",
        )

    axis.set_title(
        "Citation-to-Retrieval Verification Outcomes",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    axis.set_xlabel("Citation records")
    axis.set_xlim(0, max(values) * 1.28)
    axis.grid(axis="x", linestyle="--", alpha=0.25)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)

    figure.tight_layout()
    save_figure(figure, "figure_3_retrieval_outcomes")

    return status_counts


def write_results_table(summary, breakdown_rows, status_counts):
    breakdown_lookup = {
        row["citation_status"].strip().lower(): row
        for row in breakdown_rows
    }

    total_authorities = int(summary["reviewed_authority_groups"])
    total_mentions = int(summary["citation_mentions"])

    results = [
        (
            "Correct authority-group citations",
            int(breakdown_lookup["yes"]["authority_groups"]),
            total_authorities,
        ),
        (
            "Incomplete authority-group citations",
            int(
                breakdown_lookup["incomplete"]["authority_groups"]
            ),
            total_authorities,
        ),
        (
            "Incorrect authority-group citations",
            int(breakdown_lookup["no"]["authority_groups"]),
            total_authorities,
        ),
        (
            "Real-input citation mentions",
            int(summary["real_case_mentions"]),
            total_mentions,
        ),
        (
            "Synthetic-input citation mentions",
            int(summary["synthetic_case_mentions"]),
            total_mentions,
        ),
        (
            "Retrieved and cited records",
            status_counts["retrieved_and_cited"],
            total_mentions,
        ),
        (
            "Corpus records not retrieved",
            status_counts["in_corpus_not_retrieved"],
            total_mentions,
        ),
        (
            "Records not found in corpus registry",
            status_counts["not_found_in_corpus_registry"],
            total_mentions,
        ),
        (
            "Retrieved ID/citation mismatches",
            status_counts["retrieved_id_citation_mismatch"],
            total_mentions,
        ),
    ]

    output_file = OUTPUT / "paper_results_metrics.csv"

    with output_file.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.writer(file)
        writer.writerow(
            ["metric", "count", "denominator", "percentage"]
        )

        for metric, count, denominator in results:
            percentage = (
                count / denominator * 100 if denominator else 0
            )
            writer.writerow(
                [
                    metric,
                    count,
                    denominator,
                    f"{percentage:.1f}",
                ]
            )

    print(f"Created: {output_file}")


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)

    summary_rows = read_csv(SUMMARY_FILE)
    breakdown_rows = read_csv(BREAKDOWN_FILE)
    verification_rows = read_csv(VERIFICATION_FILE)

    summary = {
        row["metric"]: row["value"]
        for row in summary_rows
    }

    create_correctness_figure(breakdown_rows)
    create_input_type_figure(summary)

    status_counts = create_retrieval_figure(
        verification_rows
    )

    write_results_table(
        summary,
        breakdown_rows,
        status_counts,
    )

    print("\nResults figure generation completed")
    print("-----------------------------------")
    print(f"Output directory: {OUTPUT}")


if __name__ == "__main__":
    main()