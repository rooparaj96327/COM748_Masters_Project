from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, stdev
import csv
import math

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "judgment_citations_59.csv"
)

OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "outputs"
    / "experiments"
    / "citation-analysis"
)


def load_citations():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"File not found: {INPUT_FILE}")

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


def calculate_group_statistics(rows):
    citation_counts = defaultdict(Counter)

    for row in rows:
        input_type = row["input_type"].strip().lower()
        draft_id = row["draft_id"].strip()

        if input_type in {"real", "synthetic"} and draft_id:
            citation_counts[input_type][draft_id] += 1

    statistics = {}

    for input_type in ["real", "synthetic"]:
        counts = list(citation_counts[input_type].values())

        if not counts:
            raise ValueError(
                f"No citation records found for {input_type}"
            )

        group_mean = mean(counts)
        group_sd = stdev(counts) if len(counts) > 1 else 0
        standard_error = group_sd / math.sqrt(len(counts))
        confidence_interval = 1.96 * standard_error

        statistics[input_type] = {
            "judgments": len(counts),
            "citation_mentions": sum(counts),
            "mean": group_mean,
            "standard_deviation": group_sd,
            "confidence_interval_95": confidence_interval,
        }

    return statistics


def create_figure(statistics):
    labels = ["Real-case inputs", "Synthetic-case inputs"]
    input_types = ["real", "synthetic"]

    means = [
        statistics[input_type]["mean"]
        for input_type in input_types
    ]

    confidence_intervals = [
        statistics[input_type]["confidence_interval_95"]
        for input_type in input_types
    ]

    colors = ["#17365D", "#7EA6E0"]

    figure, axis = plt.subplots(figsize=(7.2, 4.8))

    bars = axis.bar(
        labels,
        means,
        yerr=confidence_intervals,
        capsize=7,
        color=colors,
        width=0.58,
        error_kw={
            "elinewidth": 1.5,
            "capthick": 1.5,
            "ecolor": "#333333",
        },
    )

    for bar, input_type in zip(bars, input_types):
        values = statistics[input_type]

        label = (
            f"{values['mean']:.2f}\n"
            f"n={values['judgments']} judgments\n"
            f"{values['citation_mentions']} mentions"
        )

        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height()
            + values["confidence_interval_95"]
            + 0.08,
            label,
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    maximum = max(
        mean_value + interval
        for mean_value, interval in zip(
            means,
            confidence_intervals,
        )
    )

    axis.set_title(
        "Mean Citation Mentions per Generated Judgment",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    axis.set_ylabel("Mean citation mentions per judgment")
    axis.set_ylim(0, maximum + 0.8)
    axis.grid(axis="y", linestyle="--", alpha=0.25)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)

    axis.text(
        0.99,
        0.02,
        "Error bars show 95% confidence intervals",
        transform=axis.transAxes,
        ha="right",
        va="bottom",
        fontsize=9,
        color="#555555",
    )

    figure.tight_layout()

    png_file = (
        OUTPUT_DIRECTORY
        / "figure_2_citations_per_judgment.png"
    )
    pdf_file = (
        OUTPUT_DIRECTORY
        / "figure_2_citations_per_judgment.pdf"
    )

    figure.savefig(
        png_file,
        dpi=300,
        bbox_inches="tight",
        facecolor="white",
    )
    figure.savefig(
        pdf_file,
        bbox_inches="tight",
        facecolor="white",
    )

    plt.close(figure)

    print(f"Created: {png_file}")
    print(f"Created: {pdf_file}")


def write_metrics(statistics):
    output_file = (
        OUTPUT_DIRECTORY
        / "input_type_normalized_metrics.csv"
    )

    with output_file.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.writer(file)

        writer.writerow(
            [
                "input_type",
                "judgments",
                "citation_mentions",
                "mean_citations_per_judgment",
                "standard_deviation",
                "confidence_interval_95",
            ]
        )

        for input_type in ["real", "synthetic"]:
            values = statistics[input_type]

            writer.writerow(
                [
                    input_type,
                    values["judgments"],
                    values["citation_mentions"],
                    f"{values['mean']:.4f}",
                    f"{values['standard_deviation']:.4f}",
                    f"{values['confidence_interval_95']:.4f}",
                ]
            )

    print(f"Created: {output_file}")


def main():
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    rows = load_citations()
    statistics = calculate_group_statistics(rows)

    create_figure(statistics)
    write_metrics(statistics)

    print("\nNormalized comparison completed")
    print("--------------------------------")

    for input_type in ["real", "synthetic"]:
        values = statistics[input_type]

        print(
            f"{input_type}: "
            f"{values['citation_mentions']} mentions / "
            f"{values['judgments']} judgments = "
            f"{values['mean']:.4f}"
        )


if __name__ == "__main__":
    main()