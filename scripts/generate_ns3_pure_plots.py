#!/usr/bin/env python3
"""
Generate publication-quality plots strictly for NS-3 LENA comparing:
  - Round Robin (RR)
  - Proportional Fair (PF)
  - Best CQI (BCQI / MT)
in Wideband (WB) and Subband (SB) modes.

Plots:
1. 01_radar_comparison_wb_sb.png: Dual-panel radar chart (a: WB, b: SB) for PF, RR, BCQI.
2. 02_resource_grid_rr_pf_bcqi.png: 2D Time-Frequency OFDMA Resource Grid.
3. 03_per_ue_throughput_ns3.png: Per-UE throughput bar chart across 10 UEs.
4. 04_latency_and_fairness_ns3.png: Latency (log scale) & Jain's Fairness Index comparison.
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.patches as mpatches

# Register Times New Roman fonts if available
for font_file in [
    "/home/Avadik/.local/share/fonts/ttf-ms-fonts/Times.TTF",
    "/home/Avadik/.local/share/fonts/ttf-ms-fonts/Timesbd.TTF",
]:
    if os.path.exists(font_file):
        fm.fontManager.addfont(font_file)

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 12,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 11,
    "savefig.dpi": 300,
})

REPS_DIR = "/home/Avadik/Prog/Ns3-YADRO-reps"
os.makedirs(REPS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. RADAR COMPARISON CHART: PF vs RR vs BCQI (Wideband vs Subband)
# ---------------------------------------------------------------------------
def build_radar_chart():
    RADAR_METRIC_NAMES = [
        "DL_THROUGHPUT",
        "DL_BLER",
        "PRB_UTIL",
        "MAC_DL_LATENCY",
        "DL_SERVICE_GAP/MAX_TTI",
    ]

    # Metrics from ns-3 simulation matrix:
    # WB:
    # PF:   AggTP = 17.41 Mbps, BLER = 4.36%, PRB = 96.0%, Latency = 50.6 ms (50620 us), MaxGap = 10 TTI
    # RR:   AggTP = 14.55 Mbps, BLER = 4.13%, PRB = 80.0%, Latency = 60.3 ms (60330 us), MaxGap = 1 TTI
    # BCQI: AggTP =  8.53 Mbps, BLER = 7.80%, PRB = 96.0%, Latency = 2002.0 ms (2002000 us -> norm scale max), MaxGap = 25 TTI
    
    # SB:
    # PF:   AggTP = 17.33 Mbps, BLER = 4.63%, PRB = 96.0%, Latency = 50.9 ms (50910 us), MaxGap = 12 TTI
    # RR:   AggTP = 14.44 Mbps, BLER = 3.75%, PRB = 80.0%, Latency = 60.9 ms (60870 us), MaxGap = 1 TTI
    # BCQI: AggTP =  8.90 Mbps, BLER = 8.90%, PRB = 96.0%, Latency = 1780.0 ms (1780000 us), MaxGap = 28 TTI

    wb_data = {
        "PF":   [17.41, 4.36, 0.96, 50.6, 10.0],
        "RR":   [14.55, 4.13, 0.80, 60.3, 1.0],
        "BCQI": [8.53,  7.80, 0.96, 2002.0, 25.0],
    }
    wb_max = [18.0, 8.0, 1.00, 2002.0, 25.0]

    sb_data = {
        "PF":   [17.33, 4.63, 0.96, 50.9, 12.0],
        "RR":   [14.44, 3.75, 0.80, 60.9, 1.0],
        "BCQI": [8.90,  8.90, 0.96, 1780.0, 28.0],
    }
    sb_max = [18.0, 9.0, 1.00, 1780.0, 28.0]

    styles = {
        "WB": {
            "PF":   {"color": "#1e88e5", "marker": "o", "linestyle": "-", "label": "PF (WB)"},
            "RR":   {"color": "#fb8c00", "marker": "s", "linestyle": "-", "label": "RR (WB)"},
            "BCQI": {"color": "#e53935", "marker": "^", "linestyle": "-", "label": "BCQI (WB)"},
        },
        "SB": {
            "PF":   {"color": "#0d47a1", "marker": "o", "linestyle": "--", "label": "PF (SB)"},
            "RR":   {"color": "#d84315", "marker": "s", "linestyle": "--", "label": "RR (SB)"},
            "BCQI": {"color": "#b71c1c", "marker": "^", "linestyle": "--", "label": "BCQI (SB)"},
        }
    }

    fig = plt.figure(figsize=(16, 8.5))
    ax_a = fig.add_subplot(1, 2, 1, polar=True)
    ax_b = fig.add_subplot(1, 2, 2, polar=True)

    N = len(RADAR_METRIC_NAMES)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    def render_panel(ax, mode_data, mode_key, panel_label, max_vals):
        def format_axis(idx: int, val: float) -> str:
            name = RADAR_METRIC_NAMES[idx]
            if name == "DL_THROUGHPUT":
                return f"{name}\n[max: {val:.1f} Mbps]"
            if name == "DL_BLER":
                return f"{name}\n[max: {val:.1f}%]"
            if name == "PRB_UTIL":
                return f"{name}\n[max: {val:.2f}]"
            if name == "MAC_DL_LATENCY":
                return f"{name}\n[max: {val:.0f} ms]"
            if name == "DL_SERVICE_GAP/MAX_TTI":
                return f"{name}\n[max: {val:.0f} TTI]"
            return f"{name}\n[max: {val:.1f}]"

        spoke_labels = [format_axis(i, v) for i, v in enumerate(max_vals)]

        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)

        ax.set_ylim(0, 1.20)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(["20%", "40%", "60%", "80%", "100%"], color="#777777", size=9.5)

        ax.set_thetagrids(np.degrees(angles[:-1]), spoke_labels, fontsize=11, fontfamily="Times New Roman")
        ax.tick_params(axis='x', pad=14)

        for sched_val in ["PF", "RR", "BCQI"]:
            raw_vals = mode_data[sched_val]
            st = styles[mode_key][sched_val]
            norm_vals = [raw_vals[j] / max_vals[j] if max_vals[j] > 0 else 0.0 for j in range(N)]
            norm_vals += norm_vals[:1]

            ax.plot(
                angles,
                norm_vals,
                color=st["color"],
                marker=st["marker"],
                markersize=6,
                linestyle=st["linestyle"],
                linewidth=2.2,
                label=st["label"],
                alpha=0.9,
            )
            ax.fill(angles, norm_vals, color=st["color"], alpha=0.08)

        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.12), fontsize=11, framealpha=0.85)
        ax.text(-0.25, 1.15, panel_label, transform=ax.transAxes, fontsize=18, fontweight="bold", va="top")

    render_panel(ax_a, wb_data, "WB", "а)", wb_max)
    render_panel(ax_b, sb_data, "SB", "б)", sb_max)

    plt.tight_layout()
    fig.subplots_adjust(wspace=0.36, top=0.90, bottom=0.10)
    out_file = os.path.join(REPS_DIR, "01_radar_comparison_wb_sb.png")
    fig.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Saved radar chart to {out_file}")

# ---------------------------------------------------------------------------
# 2. TIME-FREQUENCY OFDMA RESOURCE GRID
# ---------------------------------------------------------------------------
def build_resource_grid():
    def parse_allocations(mac_file, num_prbs=25, max_subframes=35):
        with open(mac_file, "r") as f:
            lines = [line.strip().split("\t") for line in f if not line.startswith("%") and line.strip()]

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
        grid = np.zeros((num_prbs, len(sorted_keys)), dtype=int)

        for t_idx, key in enumerate(sorted_keys):
            records = subframe_records[key]
            curr_prb = 0
            for rnti, mcs, size in records:
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

    scheds = [
        ("RR", "Round Robin (RR)", "/home/Avadik/Prog/ns-3.43/reports/WB/RR/DlMacStats.txt",
         "Равномерное статическое разделение PRB (2 PRB на UE)\n20% радиоресурса (PRB 20–24) не утилизировано"),
        ("PF", "Proportional Fair (PF)", "/home/Avadik/Prog/ns-3.43/reports/WB/PF/DlMacStats.txt",
         "Динамическое адаптивное квантование по 24 PRB (12 RBG)\nПоочерёдное выделение с учётом качества радиоканала"),
        ("BCQI", "Best CQI (Maximum Throughput)", "/home/Avadik/Prog/ns-3.43/reports/WB/BCQI/DlMacStats.txt",
         "Монополизация радиоканала терминалом с наивысшим SNR (UE 1)\n100% голодание (starvation) остальных 9 терминалов")
    ]

    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

    colors = [
        "#E2E8F0",  # 0: Idle / Unallocated
        "#E53E3E",  # 1: UE 1
        "#3182CE",  # 2: UE 2
        "#38A169",  # 3: UE 3
        "#DD6B20",  # 4: UE 4
        "#805AD5",  # 9: UE 5
        "#D69E2E",  # 10: UE 6
        "#319795",  # 11: UE 7
        "#ED64A6",  # 12: UE 8
        "#4FD1C5",  # 15: UE 9
        "#4A5568",  # 16: UE 10
    ]
    rnti_map = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 9: 5, 10: 6, 11: 7, 12: 8, 15: 9, 16: 10}

    cmap = ListedColormap(colors)
    bounds = list(range(len(colors) + 1))
    norm = BoundaryNorm(bounds, cmap.N)

    max_sf = 35

    for ax_idx, (code, title, file_path, subtitle) in enumerate(scheds):
        ax = axes[ax_idx]
        raw_grid, sorted_keys = parse_allocations(file_path, num_prbs=25, max_subframes=max_sf)
        
        mapped_grid = np.zeros_like(raw_grid)
        for rnti, idx in rnti_map.items():
            mapped_grid[raw_grid == rnti] = idx

        ax.imshow(
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

        if code == "RR":
            ax.axhspan(19.5, 24.5, color="red", alpha=0.15, linestyle="--", linewidth=1.2)
            ax.text(max_sf / 2, 22, "НЕИСПОЛЬЗУЕМЫЕ PRB (ПРОСТОЙ 20%)", color="#C53030",
                    fontsize=9, fontweight="bold", ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8, edgecolor="#E53E3E"))

    axes[-1].set_xlabel("Номер субфрейма / TTI (квант 1 мс)", fontsize=11)
    axes[-1].set_xticks(range(0, max_sf, 5))
    axes[-1].set_xticklabels([f"TTI {i}" for i in range(0, max_sf, 5)])

    legend_patches = [
        mpatches.Patch(facecolor=colors[0], label="Простой (Idle / Unallocated)", edgecolor="black", linewidth=0.5)
    ]
    ue_labels = ["UE 1", "UE 2", "UE 3", "UE 4", "UE 5", "UE 6", "UE 7", "UE 8", "UE 9", "UE 10"]
    for i, u_lbl in enumerate(ue_labels):
        legend_patches.append(mpatches.Patch(facecolor=colors[i+1], label=u_lbl, edgecolor="black", linewidth=0.5))

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
    out_file = os.path.join(REPS_DIR, "02_resource_grid_rr_pf_bcqi.png")
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[+] Saved resource grid to {out_file}")

# ---------------------------------------------------------------------------
# 3. PER-UE THROUGHPUT DISTRIBUTION (10 UEs)
# ---------------------------------------------------------------------------
def build_per_ue_throughput_plot():
    # Real simulation per-UE data from flowmon-results.xml
    wb_rr = [1.455] * 10
    wb_pf = [1.745, 1.748, 1.739, 1.746, 1.747, 1.742, 1.740, 1.744, 1.751, 1.748]
    wb_bcqi = [0.034, 0.034, 0.034, 0.034, 0.034, 0.034, 8.400, 0.034, 0.034, 0.034]

    sb_rr = [1.448, 1.450, 1.447, 1.452, 1.446, 1.441, 1.421, 1.444, 1.451, 1.445]
    sb_pf = [1.738, 1.741, 1.736, 1.732, 1.739, 1.731, 1.727, 1.738, 1.742, 1.735]
    sb_bcqi = [0.034, 0.034, 0.034, 0.041, 0.034, 0.034, 8.400, 0.034, 0.034, 0.412]

    ues = np.arange(1, 11)
    w = 0.26

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.2), sharey=True)

    # Wideband
    ax1.bar(ues - w, wb_rr, w, label="Round Robin (RR)", color="#fb8c00", edgecolor="black", alpha=0.85)
    ax1.bar(ues, wb_pf, w, label="Proportional Fair (PF)", color="#1e88e5", edgecolor="black", alpha=0.85)
    ax1.bar(ues + w, wb_bcqi, w, label="Best CQI (BCQI)", color="#e53935", edgecolor="black", alpha=0.85)
    ax1.set_title("а) Wideband (WB) — Пропускная способность по абонентам", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Номер абонента (UE ID)", fontsize=10)
    ax1.set_ylabel("Throughput (Мбит/с)", fontsize=10)
    ax1.set_xticks(ues)
    ax1.grid(True, linestyle="--", alpha=0.4)
    ax1.legend(loc="upper left")
    ax1.annotate("Монополия UE 7\n(8.40 Мбит/с)", xy=(7 + w, 8.4), xytext=(7 + w - 1.2, 7.2),
                 arrowprops=dict(facecolor="black", shrink=0.05, width=1, headwidth=6),
                 fontsize=8.5, fontweight="bold", bbox=dict(boxstyle="round,pad=0.2", facecolor="#FFEBEE", edgecolor="#E53935"))

    # Subband
    ax2.bar(ues - w, sb_rr, w, label="Round Robin (RR)", color="#d84315", edgecolor="black", alpha=0.85)
    ax2.bar(ues, sb_pf, w, label="Proportional Fair (PF)", color="#0d47a1", edgecolor="black", alpha=0.85)
    ax2.bar(ues + w, sb_bcqi, w, label="Best CQI (BCQI)", color="#b71c1c", edgecolor="black", alpha=0.85)
    ax2.set_title("б) Subband (SB) — Пропускная способность по абонентам", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Номер абонента (UE ID)", fontsize=10)
    ax2.set_xticks(ues)
    ax2.grid(True, linestyle="--", alpha=0.4)
    ax2.legend(loc="upper left")
    ax2.annotate("Монополия UE 7\n(8.40 Мбит/с)", xy=(7 + w, 8.4), xytext=(7 + w - 1.2, 7.2),
                 arrowprops=dict(facecolor="black", shrink=0.05, width=1, headwidth=6),
                 fontsize=8.5, fontweight="bold", bbox=dict(boxstyle="round,pad=0.2", facecolor="#FFEBEE", edgecolor="#E53935"))

    plt.tight_layout()
    out_file = os.path.join(REPS_DIR, "03_per_ue_throughput_ns3.png")
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[+] Saved per-UE throughput to {out_file}")

# ---------------------------------------------------------------------------
# 4. LATENCY & FAIRNESS COMPARISON (CDF & JFI)
# ---------------------------------------------------------------------------
def build_latency_and_fairness_plot():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Left: Packet latency on log scale
    scheds = ["RR", "PF", "BCQI"]
    labels = ["Round Robin", "Proportional Fair", "Best CQI"]
    x = np.arange(len(scheds))
    w = 0.35

    wb_lat = [60.33, 50.62, 2002.0]
    sb_lat = [60.87, 50.91, 1780.0]

    b1 = ax1.bar(x - w/2, wb_lat, w, label="Wideband (WB)", color="#1e88e5", edgecolor="black", alpha=0.85)
    b2 = ax1.bar(x + w/2, sb_lat, w, label="Subband (SB)", color="#d84315", edgecolor="black", alpha=0.85)
    ax1.set_yscale("log")
    ax1.set_ylim(10, 5000)
    ax1.set_ylabel("Средняя задержка пакетов (мс, лог-шкала)", fontsize=10)
    ax1.set_title("а) Задержка доставки пакетов (мс, лог)", fontsize=11, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=10)
    ax1.grid(True, linestyle="--", alpha=0.4)
    ax1.legend(loc="upper left")

    for b in list(b1) + list(b2):
        h = b.get_height()
        ax1.text(b.get_x() + b.get_width()/2., h * 1.25, f"{h:.0f} мс", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    # Right: Jain's Fairness Index
    wb_jfi = [1.0000, 1.0000, 0.1074]
    sb_jfi = [1.0000, 1.0000, 0.1166]

    b3 = ax2.bar(x - w/2, wb_jfi, w, label="Wideband (WB)", color="#1e88e5", edgecolor="black", alpha=0.85)
    b4 = ax2.bar(x + w/2, sb_jfi, w, label="Subband (SB)", color="#d84315", edgecolor="black", alpha=0.85)
    ax2.set_ylim(0, 1.25)
    ax2.set_ylabel("Индекс справедливости Джейна (JFI)", fontsize=10)
    ax2.set_title("б) Индекс справедливости Джейна (JFI)", fontsize=11, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=10)
    ax2.grid(True, linestyle="--", alpha=0.4)
    ax2.legend(loc="upper right")

    for b in list(b3) + list(b4):
        h = b.get_height()
        ax2.text(b.get_x() + b.get_width()/2., h + 0.03, f"{h:.3f}", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    plt.tight_layout()
    out_file = os.path.join(REPS_DIR, "04_latency_and_fairness_ns3.png")
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[+] Saved latency & fairness plot to {out_file}")

if __name__ == "__main__":
    build_radar_chart()
    build_resource_grid()
    build_per_ue_throughput_plot()
    build_latency_and_fairness_plot()
    print("[+] All pure NS-3 plots successfully generated!")
