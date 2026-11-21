#!/usr/bin/env python3
"""
Generate publication-quality Time-Frequency Resource Allocation Grid (OFDMA Grid)
comparing Round Robin (RR), Proportional Fair (PF), and Best CQI (BCQI) in ns-3 LENA.
Bandwidth: 5 MHz (25 PRBs: 0..24), 10 UEs.
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.patches as mpatches

# Register Times New Roman if present
for font_file in [
    "/home/Avadik/.local/share/fonts/ttf-ms-fonts/Times.TTF",
    "/home/Avadik/.local/share/fonts/ttf-ms-fonts/Timesbd.TTF",
]:
    if os.path.exists(font_file):
        matplotlib.font_manager.fontManager.addfont(font_file)

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 11,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.titlesize": 13,
    "savefig.dpi": 300,
})

def parse_allocations(mac_file, num_prbs=25, max_subframes=40):
    """
    Parses DlMacStats.txt to reconstruct the 2D PRB allocation matrix [num_prbs x num_subframes].
    Returns grid, sorted unique subframes, and list of RNTIs.
    """
    with open(mac_file, "r") as f:
        lines = [line.strip().split("\t") for line in f if not line.startswith("%") and line.strip()]

    # Collect subframes
    subframe_records = {}
    for row in lines:
        f = int(row[3])
        sf = int(row[4])
        rnti = int(row[5])
        mcs = int(row[6])
        size = int(row[7])
        key = (f, sf)
        if key not in subframe_records:
            subframe_records[key] = []
        subframe_records[key].append((rnti, mcs, size))

    sorted_keys = sorted(subframe_records.keys())[:max_subframes]
    
    # 0 = unallocated (idle)
    # 1..10 = UE 1..10
    grid = np.zeros((num_prbs, len(sorted_keys)), dtype=int)

    # AMC lookup for PRB count
    # Size 185 at mcs 28 -> 2 PRBs
    # Size 2196 at mcs 28 -> 24 PRBs
    for t_idx, key in enumerate(sorted_keys):
        records = subframe_records[key]
        curr_prb = 0
        for rnti, mcs, size in records:
            # Map size to PRBs
            if size == 185:
                nprb = 2
            elif size == 2196:
                nprb = 24
            elif size == 2052:
                nprb = 22
            elif size == 1836:
                nprb = 20
            elif size == 1692:
                nprb = 18
            elif size == 549:
                nprb = 6
            elif size == 373:
                nprb = 4
            else:
                nprb = max(1, int(round((size / 2196.0) * 24)))
            
            end_prb = min(num_prbs, curr_prb + nprb)
            grid[curr_prb:end_prb, t_idx] = rnti
            curr_prb = end_prb
            if curr_prb >= num_prbs:
                break

    return grid, sorted_keys

def plot_resource_grids(output_path):
    scheds = [
        ("RR", "Round Robin (RR)", "/home/Avadik/Prog/ns-3.43/reports/WB/RR/DlMacStats.txt",
         "Равномерное статическое разделение PRB (2 PRB на UE)\n20% радиоресурса (PRB 20–24) не утилизировано"),
        ("PF", "Proportional Fair (PF)", "/home/Avadik/Prog/ns-3.43/reports/WB/PF/DlMacStats.txt",
         "Динамическое адаптивное квантование по 24 PRB (12 RBG)\nПоочерёдное выделение с учётом качества радиоканала"),
        ("BCQI", "Best CQI (Maximum Throughput)", "/home/Avadik/Prog/ns-3.43/reports/WB/BCQI/DlMacStats.txt",
         "Монополизация радиоканала терминалом с наивысшим SNR (UE 1)\n100% голодание (starvation) остальных 9 терминалов")
    ]

    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

    # 10 distinctive colors for 10 UEs + Gray for idle
    colors = [
        "#E2E8F0",  # 0: Idle / Unallocated (Light Slate Gray)
        "#E53E3E",  # 1: UE 1 (Red)
        "#3182CE",  # 2: UE 2 (Blue)
        "#38A169",  # 3: UE 3 (Green)
        "#DD6B20",  # 4: UE 4 (Orange)
        "#805AD5",  # 9: UE 5 (Purple)
        "#D69E2E",  # 10: UE 6 (Gold)
        "#319795",  # 11: UE 7 (Teal)
        "#ED64A6",  # 12: UE 8 (Pink)
        "#4FD1C5",  # 15: UE 9 (Cyan)
        "#4A5568",  # 16: UE 10 (Dark Slate)
    ]
    rnti_map = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 9: 5, 10: 6, 11: 7, 12: 8, 15: 9, 16: 10}

    cmap = ListedColormap(colors)
    bounds = list(range(len(colors) + 1))
    norm = BoundaryNorm(bounds, cmap.N)

    max_sf = 35

    for ax_idx, (code, title, file_path, subtitle) in enumerate(scheds):
        ax = axes[ax_idx]
        raw_grid, sorted_keys = parse_allocations(file_path, num_prbs=25, max_subframes=max_sf)
        
        # Remap RNTIs to consecutive indices 0..10
        mapped_grid = np.zeros_like(raw_grid)
        for rnti, idx in rnti_map.items():
            mapped_grid[raw_grid == rnti] = idx

        im = ax.imshow(
            mapped_grid,
            aspect="auto",
            origin="lower",
            cmap=cmap,
            norm=norm,
            interpolation="nearest"
        )

        ax.set_title(f"{title} — {subtitle}", fontsize=11, fontweight="bold", pad=8)
        ax.set_ylabel("Индекс PRB (0–24)", fontsize=10)
        ax.set_yticks([0, 5, 10, 15, 20, 24])
        ax.grid(True, which="both", color="white", linestyle="-", linewidth=0.6, alpha=0.6)

        # Highlight idle area in RR
        if code == "RR":
            ax.axhspan(19.5, 24.5, color="red", alpha=0.15, linestyle="--", linewidth=1.2)
            ax.text(max_sf / 2, 22, "НЕИСПОЛЬЗУЕМЫЕ PRB (ПРОСТОЙ 20%)", color="#C53030",
                    fontsize=9, fontweight="bold", ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8, edgecolor="#E53E3E"))

    axes[-1].set_xlabel("Номер субфрейма / TTI (квант 1 мс)", fontsize=11)
    axes[-1].set_xticks(range(0, max_sf, 5))
    axes[-1].set_xticklabels([f"TTI {i}" for i in range(0, max_sf, 5)])

    # Legend for UEs
    legend_patches = [
        mpatches.Patch(color=colors[0], label="Простой (Idle / Unallocated)", edgecolor="black", linewidth=0.5)
    ]
    ue_labels = ["UE 1", "UE 2", "UE 3", "UE 4", "UE 5", "UE 6", "UE 7", "UE 8", "UE 9", "UE 10"]
    for i, u_lbl in enumerate(ue_labels):
        legend_patches.append(mpatches.Patch(color=colors[i+1], label=u_lbl, edgecolor="black", linewidth=0.5))

    fig.legend(
        handles=legend_patches,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.99),
        ncol=6,
        fontsize=9,
        frameon=True,
        facecolor="#F7FAFC",
        edgecolor="#CBD5E0"
    )

    plt.tight_layout()
    fig.subplots_adjust(top=0.91, bottom=0.07, hspace=0.35)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[+] Saved resource grid figure to {output_path}")

if __name__ == "__main__":
    out_file = "/home/Avadik/Prog/Ns3-YADRO-reps/05_resource_grid_rr_pf_bcqi.png"
    plot_resource_grids(out_file)
