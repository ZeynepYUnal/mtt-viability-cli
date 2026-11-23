#!/usr/bin/env python3
import sys
import csv
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def four_pl(x, bottom, top, ic50, hill_slope):
    return bottom + (top - bottom) / (1.0 + (x / ic50) ** hill_slope)

def main():
    summary_file = sys.argv[1] if len(sys.argv) > 1 else "results/viability_summary.tsv"
    output_plot = sys.argv[2] if len(sys.argv) > 2 else "results/dose_response_curve.png"

    doses, means, sds = [], [], []
    with open(summary_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            dose = float(row["Dose_uM"])
            if dose > 0:
                doses.append(dose)
                means.append(float(row["Mean_Viability_Pct"]))
                sds.append(float(row["SD"]))

    doses = np.array(doses)
    means = np.array(means)
    sds = np.array(sds)

    p0 = [0.0, 100.0, float(np.median(doses)), 1.5]
    bounds = ([0.0, 70.0, min(doses) * 0.01, 0.1], [30.0, 120.0, max(doses) * 100.0, 10.0])

    popt, _ = curve_fit(four_pl, doses, means, p0=p0, bounds=bounds, maxfev=10000)
    bottom, top, ic50, hill_slope = popt

    residuals = means - four_pl(doses, *popt)
    r_squared = 1.0 - (np.sum(residuals ** 2) / np.sum((means - np.mean(means)) ** 2))

    print(f"4PL Curve Fit Results -> IC50: {ic50:.2f} uM | Hill Slope: {hill_slope:.2f} | R^2: {r_squared:.4f}")

    # Plot dose-response curve
    fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
    x_smooth = np.logspace(np.log10(min(doses) * 0.5), np.log10(max(doses) * 1.5), 250)
    y_smooth = four_pl(x_smooth, *popt)

    ax.plot(x_smooth, y_smooth, color="#1f77b4", linewidth=2.2, label="4PL Fit")
    ax.errorbar(doses, means, yerr=sds, fmt="o", color="#0d3b66", ecolor="#0d3b66",
                elinewidth=1.4, capsize=4, markersize=6, label="Mean ± SD (n=3)")

    # IC50 reference lines
    ax.axhline(50, color="#888888", linestyle="--", linewidth=1)
    ax.axvline(ic50, color="#d62728", linestyle="--", linewidth=1.2)
    ax.scatter([ic50], [50], color="#d62728", zorder=5, s=45)

    ax.text(
        0.05, 0.15,
        f"IC50 = {ic50:.2f} µM\nR² = {r_squared:.4f}",
        transform=ax.transAxes,
        fontsize=10.5,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f9fa", edgecolor="#cccccc")
    )

    ax.set_xscale("log")
    ax.set_ylim(-5, 115)
    ax.set_xlabel("Concentration (µM, log scale)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Cell Viability (% of Control)", fontsize=11, fontweight="bold")
    ax.set_title("MTT Dose-Response Curve (4PL Regression)", fontsize=12.5, fontweight="bold", pad=12)
    ax.grid(True, which="both", linestyle=":", alpha=0.5)
    ax.legend(frameon=True, loc="upper right")

    plt.tight_layout()
    plt.savefig(output_plot)
    print(f"Dose-response plot saved to: {output_plot}")

if __name__ == "__main__":
    main()
