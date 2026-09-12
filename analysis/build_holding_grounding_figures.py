#!/usr/bin/env python3
"""Generate holding-accuracy and reasoning-grounding figures from annotations."""

import csv
import os
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
PREDICTIONS = ROOT / "outputs" / "verifier_predictions_v1.csv"
OUTPUT_DIR = ROOT / "outputs" / "experiments" / "annotation-analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NAVY = "#17365D"
BLUE = "#4472C4"
GREEN = "#2E8B57"
AMBER = "#E6A23C"
RED = "#C44E52"
GREY = "#6B7280"
LIGHT_BLUE = "#7EA6E0"
PURPLE = "#7B68AE"

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 13,
    "axes.titlesize": 16,
    "axes.titleweight": "bold",
    "axes.labelsize": 14,
    "figure.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.15,
})


def load_validation_rows():
    rows = []
    with open(PREDICTIONS, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["in_validation_sample"] == "yes":
                rows.append(r)
    return rows


def figure_holding_accuracy(rows):
    labels_order = ["yes", "partial", "no", "n/a"]
    display = ["Accurate", "Partial", "Inaccurate", "N/A"]
    colors = [GREEN, AMBER, RED, GREY]

    counts = Counter(r["adjudicated_holding_accuracy"] for r in rows)
    values = [counts.get(l, 0) for l in labels_order]
    total = sum(values)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars = ax.bar(display, values, color=colors, edgecolor="white", linewidth=0.8, width=0.6)

    for bar, v in zip(bars, values):
        pct = v / total * 100 if total else 0
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8,
                f"{v}\n({pct:.1f}%)", ha="center", va="bottom", fontsize=12, fontweight="bold")

    ax.set_title("Holding Accuracy: Human-Adjudicated Labels", pad=15)
    ax.set_ylabel("Citation occurrences")
    ax.set_ylim(0, max(values) * 1.25)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for fmt in ("png", "pdf"):
        fig.savefig(OUTPUT_DIR / f"figure_4_holding_accuracy.{fmt}")
    plt.close(fig)
    print(f"  Figure 4: holding accuracy ({total} occurrences)")


def figure_grounding(rows):
    labels_order = ["yes", "partial", "no"]
    display = ["Grounded", "Partial", "Ungrounded"]
    colors = [GREEN, AMBER, RED]

    counts = Counter(r["adjudicated_reasoning_grounding"] for r in rows
                     if r["adjudicated_reasoning_grounding"] in labels_order)
    values = [counts.get(l, 0) for l in labels_order]
    total = sum(values)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars = ax.bar(display, values, color=colors, edgecolor="white", linewidth=0.8, width=0.6)

    for bar, v in zip(bars, values):
        pct = v / total * 100 if total else 0
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
                f"{v}\n({pct:.1f}%)", ha="center", va="bottom", fontsize=12, fontweight="bold")

    ax.set_title("Reasoning Grounding: Human-Adjudicated Labels", pad=15)
    ax.set_ylabel("Citation occurrences")
    ax.set_ylim(0, max(values) * 1.25)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for fmt in ("png", "pdf"):
        fig.savefig(OUTPUT_DIR / f"figure_5_reasoning_grounding.{fmt}")
    plt.close(fig)
    print(f"  Figure 5: reasoning grounding ({total} occurrences)")


def figure_grounding_gap(rows):
    all_rows_path = ROOT / "outputs" / "verifier_predictions_v1.csv"
    all_rows = []
    with open(all_rows_path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            all_rows.append(r)

    real_cites = [r for r in all_rows if r["input_type"] == "real"
                  and r["citation_kind"] not in ("legislation", "rule")]
    synth_cites = [r for r in all_rows if r["input_type"] == "synthetic"
                   and r["citation_kind"] not in ("legislation", "rule")]

    real_absent = sum(1 for r in real_cites
                      if r["predicted_citation_status"] == "not_found_in_corpus_registry")
    synth_absent = sum(1 for r in synth_cites
                       if r["predicted_citation_status"] == "not_found_in_corpus_registry")

    real_val = [r for r in rows if r["input_type"] == "real"]
    synth_val = [r for r in rows if r["input_type"] == "synthetic"]
    real_ungrounded = sum(1 for r in real_val if r["adjudicated_reasoning_grounding"] == "no")
    synth_ungrounded = sum(1 for r in synth_val if r["adjudicated_reasoning_grounding"] == "no")

    real_absent_pct = real_absent / len(real_cites) * 100 if real_cites else 0
    synth_absent_pct = synth_absent / len(synth_cites) * 100 if synth_cites else 0
    real_ungr_pct = real_ungrounded / len(real_val) * 100 if real_val else 0
    synth_ungr_pct = synth_ungrounded / len(synth_val) * 100 if synth_val else 0

    categories = ["Layer 1\ncitations not\nin corpus", "Layer 3\nreasoning\nungrounded"]
    real_vals = [real_absent_pct, real_ungr_pct]
    synth_vals = [synth_absent_pct, synth_ungr_pct]

    x = np.arange(len(categories))
    width = 0.3

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width / 2, real_vals, width, label="Real cases", color=NAVY)
    bars2 = ax.bar(x + width / 2, synth_vals, width, label="Synthetic cases", color=LIGHT_BLUE)

    for bars in (bars1, bars2):
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 1,
                    f"{h:.0f}%", ha="center", va="bottom", fontsize=12, fontweight="bold")

    ax.set_ylabel("Percentage of items")
    ax.set_title("Corpus absence and reasoning grounding defect rates by input type", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 100)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for fmt in ("png", "pdf"):
        fig.savefig(OUTPUT_DIR / f"figure_6_grounding_gap.{fmt}")
    plt.close(fig)
    print(f"  Figure 6: grounding gap (real vs synthetic)")


def figure_verifier_citation_confusion(rows):
    statuses = [
        "retrieved_and_cited",
        "in_corpus_not_retrieved",
        "not_found_in_corpus_registry",
        "retrieved_id_citation_mismatch",
        "not_applicable_non_case_reference",
    ]
    short = ["Retr.\n& cited", "In corpus\nnot retr.", "Not in\ncorpus", "ID/cit.\nmismatch", "Non-case\nref."]

    pred_key = "predicted_citation_status"
    truth_key = "citation_verification_status"

    n = len(statuses)
    matrix = np.zeros((n, n), dtype=int)
    for r in rows:
        p = r[pred_key]
        t = r[truth_key]
        if p in statuses and t in statuses:
            pi = statuses.index(p)
            ti = statuses.index(t)
            matrix[pi, ti] += 1

    fig, ax = plt.subplots(figsize=(9, 7))
    im = ax.imshow(matrix, cmap="Blues", aspect="auto")

    ax.set_xticks(range(n))
    ax.set_xticklabels(short, fontsize=9)
    ax.set_yticks(range(n))
    ax.set_yticklabels(short, fontsize=9)
    ax.set_xlabel("Ground truth (manual verification)", fontsize=12)
    ax.set_ylabel("Verifier prediction", fontsize=12)
    ax.set_title("Citation-Status Verifier: Confusion Matrix\n(κ = 0.80, accuracy = 87.8%)", pad=15)

    for i in range(n):
        for j in range(n):
            v = matrix[i, j]
            if v > 0:
                color = "white" if v > matrix.max() * 0.5 else "black"
                ax.text(j, i, str(v), ha="center", va="center", fontsize=11,
                        fontweight="bold", color=color)

    fig.colorbar(im, ax=ax, shrink=0.8, label="Count")

    for fmt in ("png", "pdf"):
        fig.savefig(OUTPUT_DIR / f"figure_7_citation_confusion_matrix.{fmt}")
    plt.close(fig)
    print(f"  Figure 7: citation verifier confusion matrix")


def write_annotation_metrics(rows):
    total = len(rows)
    holding = Counter(r["adjudicated_holding_accuracy"] for r in rows)
    grounding = Counter(r["adjudicated_reasoning_grounding"] for r in rows)

    real = [r for r in rows if r["input_type"] == "real"]
    synth = [r for r in rows if r["input_type"] == "synthetic"]

    with open(OUTPUT_DIR / "annotation_summary_metrics.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "count", "denominator", "percentage"])
        for label in ["yes", "partial", "no", "n/a"]:
            c = holding.get(label, 0)
            w.writerow([f"holding_{label}", c, total, round(c / total * 100, 1)])
        for label in ["yes", "partial", "no"]:
            c = grounding.get(label, 0)
            w.writerow([f"grounding_{label}", c, total, round(c / total * 100, 1)])
        w.writerow(["validation_sample_total", total, total, 100.0])
        w.writerow(["real_in_sample", len(real), total, round(len(real) / total * 100, 1)])
        w.writerow(["synthetic_in_sample", len(synth), total, round(len(synth) / total * 100, 1)])

    print(f"  Metrics: annotation_summary_metrics.csv")


if __name__ == "__main__":
    print("Loading validation data...")
    rows = load_validation_rows()
    print(f"  {len(rows)} validation-sample rows loaded\n")

    print("Generating figures:")
    figure_holding_accuracy(rows)
    figure_grounding(rows)
    figure_grounding_gap(rows)
    figure_verifier_citation_confusion(rows)
    write_annotation_metrics(rows)
    print(f"\nAll outputs written to {OUTPUT_DIR}")