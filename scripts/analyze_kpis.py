#!/usr/bin/env python3
"""
3GPP / LTE KPI Matrix Analyzer for ns-3.43 (LENA)
Generates:
  - Clean bar charts (столбчатые диаграммы) for all target metrics
Target Metrics:
  1. Throughput (Aggregate & Mean per UE bar charts)
  2. Latency (Average delay per UE bar chart, log scale)
  3. Jain's Fairness Index (JFI bar chart)
  4. PRB Utilization (PRB bar chart)
  5. Worst UE Throughput (Worst UE bar chart)
"""

import os
import sys
import re
import shutil
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt

MCS_TO_ITBS_DL = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 10, 11, 12, 13,
    14, 15, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26
]

def load_amc_table():
    amc_path = "/home/Avadik/Prog/ns-3.43/src/lte/model/lte-amc.cc"
    if not os.path.exists(amc_path):
        return {}
    with open(amc_path, "r") as f:
        content = f.read()
    m = re.search(r'TransportBlockSizeTable\[110\]\[27\]\s*=\s*\{([\s\S]+?)\};', content)
    if not m:
        return {}
    tbs_table = [[int(x.strip()) for x in row.split(',') if x.strip()] for row in re.findall(r'\{([^}]+)\}', m.group(1))]

    lookup = {}
    for nprb in range(1, 111):
        for mcs in range(0, 29):
            itbs = MCS_TO_ITBS_DL[mcs]
            tbs_bytes = tbs_table[nprb - 1][itbs] // 8
            lookup[(mcs, tbs_bytes)] = nprb
    return lookup

AMC_LOOKUP = load_amc_table()

def parse_flowmon(xml_path):
    if not os.path.exists(xml_path):
        return None
    tree = ET.parse(xml_path)
    root = tree.getroot()

    ipv4_classifier = {}
    for flow_elem in root.findall(".//Ipv4FlowClassifier/Flow"):
        fid = int(flow_elem.get("flowId"))
        src = flow_elem.get("sourceAddress")
        dst = flow_elem.get("destinationAddress")
        ipv4_classifier[fid] = (src, dst)

    ue_stats = []
    total_rx_bytes = 0
    min_time_first_tx = float("inf")
    max_time_last_rx = 0.0

    for flow_elem in root.findall(".//FlowStats/Flow"):
        fid = int(flow_elem.get("flowId"))
        src, dst = ipv4_classifier.get(fid, ("", ""))

        if src.startswith("1.0.0.") and dst.startswith("7.0.0."):
            rx_bytes = int(flow_elem.get("rxBytes", 0))
            rx_packets = int(flow_elem.get("rxPackets", 0))
            time_first_tx = float(flow_elem.get("timeFirstTxPacket", "0").replace("ns", "")) * 1e-9
            time_last_rx = float(flow_elem.get("timeLastRxPacket", "0").replace("ns", "")) * 1e-9
            delay_sum = float(flow_elem.get("delaySum", "0").replace("ns", "")) * 1e-9

            duration = time_last_rx - time_first_tx if time_last_rx > time_first_tx else 0.0
            throughput_mbps = (rx_bytes * 8.0) / (duration * 1e6) if duration > 0 else 0.0
            mean_delay_ms = (delay_sum / rx_packets * 1000.0) if rx_packets > 0 else 0.0

            total_rx_bytes += rx_bytes
            min_time_first_tx = min(min_time_first_tx, time_first_tx)
            max_time_last_rx = max(max_time_last_rx, time_last_rx)

            ue_stats.append({
                "flowId": fid,
                "dst": dst,
                "throughput_mbps": throughput_mbps,
                "delay_ms": mean_delay_ms,
                "rx_bytes": rx_bytes
            })

    total_duration = max_time_last_rx - min_time_first_tx if max_time_last_rx > min_time_first_tx else 1.0
    agg_throughput = (total_rx_bytes * 8.0) / (total_duration * 1e6)

    return {
        "flows": ue_stats,
        "agg_throughput": agg_throughput,
        "duration": total_duration
    }

def parse_prb_utilization(mac_path, system_prb=25):
    if not os.path.exists(mac_path):
        return 0.0, {}

    subframe_prb = {}
    with open(mac_path, "r") as f:
        for line in f:
            if line.startswith("%") or not line.strip():
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 8:
                frame = int(parts[3])
                sframe = int(parts[4])
                mcs = int(parts[6])
                size = int(parts[7])
                nprb = AMC_LOOKUP.get((mcs, size), 2)
                key = (frame, sframe)
                subframe_prb[key] = subframe_prb.get(key, 0) + nprb

    total_used = sum(subframe_prb.values())
    total_avail = len(subframe_prb) * system_prb
    return ((total_used / total_avail * 100.0) if total_avail > 0 else 0.0), subframe_prb

def evaluate_scenario(report_dir):
    flow_file = os.path.join(report_dir, "flowmon-results.xml")
    mac_file = os.path.join(report_dir, "DlMacStats.txt")

    flow_data = parse_flowmon(flow_file)
    if not flow_data or not flow_data["flows"]:
        return None

    throughputs = [f["throughput_mbps"] for f in flow_data["flows"]]
    delays = [f["delay_ms"] for f in flow_data["flows"]]

    agg_th = flow_data["agg_throughput"]
    mean_th = np.mean(throughputs)
    mean_delay = np.mean(delays)

    sum_x = sum(throughputs)
    sum_sq = sum(t ** 2 for t in throughputs)
    n = len(throughputs)
    jfi = (sum_x ** 2) / (n * sum_sq) if sum_sq > 0 else 0.0

    prb_util, _ = parse_prb_utilization(mac_file)
    worst_ue_th = min(throughputs)

    return {
        "dir": report_dir,
        "num_ues": n,
        "agg_throughput": agg_th,
        "mean_throughput": mean_th,
        "mean_delay": mean_delay,
        "jfi": jfi,
        "prb_util": prb_util,
        "worst_ue_th": worst_ue_th
    }

def generate_matrix_plots(matrix_data, output_dir="reports"):
    os.makedirs(output_dir, exist_ok=True)
    scheds = ["RR", "PF", "BCQI"]
    labels = ["Round Robin", "Proportional Fair", "Best CQI"]
    c_wb = "#3182CE"  # Steel Blue
    c_sb = "#DD6B20"  # Dark Amber / Orange

    x = np.arange(len(scheds))
    w = 0.35

    # -------------------------------------------------------------
    # МЕТРИКА 1: THROUGHPUT
    # Левый: Суммарный Throughput соты (столбцы)
    # Правый: Средний Throughput на абонента (столбцы)
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    wb_agg = [matrix_data[f"WB_{s}"]["agg_throughput"] for s in scheds]
    sb_agg = [matrix_data[f"SB_{s}"]["agg_throughput"] for s in scheds]
    b1 = ax1.bar(x - w/2, wb_agg, w, label="Wideband (WB)", color=c_wb, edgecolor="black", alpha=0.85)
    b2 = ax1.bar(x + w/2, sb_agg, w, label="Subband (SB)", color=c_sb, edgecolor="black", alpha=0.85)
    ax1.set_ylabel("Суммарный Throughput (Мбит/с)", fontsize=10)
    ax1.set_title("Суммарная емкость соты", fontsize=11, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=10)
    ax1.legend(loc="upper left")
    ax1.grid(True, linestyle="--", alpha=0.4)
    for b in list(b1) + list(b2):
        h = b.get_height()
        ax1.text(b.get_x() + b.get_width()/2., h + 0.25, f"{h:.2f}", ha='center', va='bottom', fontsize=8.5, fontweight='bold')

    wb_mean = [matrix_data[f"WB_{s}"]["mean_throughput"] for s in scheds]
    sb_mean = [matrix_data[f"SB_{s}"]["mean_throughput"] for s in scheds]
    b3 = ax2.bar(x - w/2, wb_mean, w, label="Wideband (WB)", color=c_wb, edgecolor="black", alpha=0.85)
    b4 = ax2.bar(x + w/2, sb_mean, w, label="Subband (SB)", color=c_sb, edgecolor="black", alpha=0.85)
    ax2.set_ylabel("Средний Throughput на UE (Мбит/с)", fontsize=10)
    ax2.set_title("Средняя скорость на абонента", fontsize=11, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=10)
    ax2.legend(loc="upper left")
    ax2.grid(True, linestyle="--", alpha=0.4)
    for b in list(b3) + list(b4):
        h = b.get_height()
        ax2.text(b.get_x() + b.get_width()/2., h + 0.03, f"{h:.2f}", ha='center', va='bottom', fontsize=8.5, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "01_throughput_matrix.png"), dpi=150)
    plt.savefig(os.path.join(output_dir, "01_throughput.png"), dpi=150)
    plt.close()

    # -------------------------------------------------------------
    # МЕТРИКА 2: LATENCY
    # Средняя задержка пакетов (столбцы на лог-шкале)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    wb_lat = [matrix_data[f"WB_{s}"]["mean_delay"] for s in scheds]
    sb_lat = [matrix_data[f"SB_{s}"]["mean_delay"] for s in scheds]

    b1 = ax.bar(x - w/2, wb_lat, w, label="Wideband (WB)", color=c_wb, edgecolor="black", alpha=0.85)
    b2 = ax.bar(x + w/2, sb_lat, w, label="Subband (SB)", color=c_sb, edgecolor="black", alpha=0.85)
    ax.set_yscale("log")
    ax.set_ylim(5, 5000)
    ax.set_ylabel("Средняя задержка (мс, лог-шкала)", fontsize=10)
    ax.set_title("Средняя задержка доставки пакетов (столбцы)", fontsize=11, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    for b in list(b1) + list(b2):
        h = b.get_height()
        ax.text(b.get_x() + b.get_width()/2., h * 1.2, f"{h:.1f}", ha='center', va='bottom', fontsize=8.5, fontweight='bold')
    ax.legend(loc="upper left")
    ax.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "02_latency_matrix.png"), dpi=150)
    plt.savefig(os.path.join(output_dir, "02_latency.png"), dpi=150)
    plt.close()

    # -------------------------------------------------------------
    # МЕТРИКА 3: JAIN'S FAIRNESS INDEX (JFI)
    # Столбцы справедливости
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 4.5))
    wb_jfi = [matrix_data[f"WB_{s}"]["jfi"] for s in scheds]
    sb_jfi = [matrix_data[f"SB_{s}"]["jfi"] for s in scheds]
    b1 = ax.bar(x - w/2, wb_jfi, w, label="Wideband (WB)", color=c_wb, edgecolor="black", alpha=0.85)
    b2 = ax.bar(x + w/2, sb_jfi, w, label="Subband (SB)", color=c_sb, edgecolor="black", alpha=0.85)
    ax.set_ylim(0, 1.25)
    ax.set_ylabel("Jain's Fairness Index", fontsize=10)
    ax.set_title("Индекс справедливости Джейна (столбцы)", fontsize=11, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    for b in list(b1) + list(b2):
        h = b.get_height()
        ax.text(b.get_x() + b.get_width()/2., h + 0.03, f"{h:.3f}", ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.legend(loc="upper right")
    ax.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "03_fairness_jfi_matrix.png"), dpi=150)
    plt.savefig(os.path.join(output_dir, "03_fairness_jfi.png"), dpi=150)
    plt.close()

    # -------------------------------------------------------------
    # МЕТРИКА 4: PRB UTILIZATION
    # Столбцы утилизации
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 4.5))
    wb_prb = [matrix_data[f"WB_{s}"]["prb_util"] for s in scheds]
    sb_prb = [matrix_data[f"SB_{s}"]["prb_util"] for s in scheds]
    b1 = ax.bar(x - w/2, wb_prb, w, label="Wideband (WB)", color=c_wb, edgecolor="black", alpha=0.85)
    b2 = ax.bar(x + w/2, sb_prb, w, label="Subband (SB)", color=c_sb, edgecolor="black", alpha=0.85)
    ax.set_ylim(0, 115)
    ax.set_ylabel("Утилизация PRB (%)", fontsize=10)
    ax.set_title("Утилизация радиоресурса PRB (столбцы)", fontsize=11, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    for b in list(b1) + list(b2):
        h = b.get_height()
        ax.text(b.get_x() + b.get_width()/2., h + 1.5, f"{h:.1f}%", ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.legend(loc="upper left")
    ax.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "04_prb_utilization_matrix.png"), dpi=150)
    plt.savefig(os.path.join(output_dir, "04_prb_utilization.png"), dpi=150)
    plt.close()

    # -------------------------------------------------------------
    # МЕТРИКА 5: WORST UE THROUGHPUT
    # Столбцы худшего абонента
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 4.5))
    wb_w = [matrix_data[f"WB_{s}"]["worst_ue_th"] for s in scheds]
    sb_w = [matrix_data[f"SB_{s}"]["worst_ue_th"] for s in scheds]
    b1 = ax.bar(x - w/2, wb_w, w, label="Wideband (WB)", color=c_wb, edgecolor="black", alpha=0.85)
    b2 = ax.bar(x + w/2, sb_w, w, label="Subband (SB)", color=c_sb, edgecolor="black", alpha=0.85)
    ax.set_ylabel("Throughput худшего UE (Мбит/с)", fontsize=10)
    ax.set_title("Пропускная способность худшего абонента (столбцы)", fontsize=11, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    for b in list(b1) + list(b2):
        h = b.get_height()
        ax.text(b.get_x() + b.get_width()/2., h + 0.04, f"{h:.3f}", ha='center', va='bottom', fontsize=8.5, fontweight='bold')
    ax.legend(loc="upper left")
    ax.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "05_worst_ue_matrix.png"), dpi=150)
    plt.savefig(os.path.join(output_dir, "05_worst_ue_throughput.png"), dpi=150)
    plt.close()

    # -------------------------------------------------------------
    # СВОДНЫЙ ДАШБОРД (2x3) — ВСЕ 6 ГРАФИКОВ СТОЛБЦЫ
    # -------------------------------------------------------------
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))

    # 1. Средний Throughput на абонента (столбцы)
    b1 = axes[0, 0].bar(x - w/2, wb_mean, w, label="WB", color=c_wb, edgecolor="black", alpha=0.85)
    b2 = axes[0, 0].bar(x + w/2, sb_mean, w, label="SB", color=c_sb, edgecolor="black", alpha=0.85)
    axes[0, 0].set_ylabel("Throughput на UE (Мбит/с)", fontsize=9.5)
    axes[0, 0].set_title("1. Средняя скорость на абонента (столбцы)", fontsize=11, fontweight="bold")
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(scheds, fontsize=10)
    for b in list(b1) + list(b2):
        h = b.get_height()
        axes[0, 0].text(b.get_x() + b.get_width()/2., h + 0.03, f"{h:.2f}", ha='center', va='bottom', fontsize=8, fontweight='bold')
    axes[0, 0].legend(loc="upper left", fontsize=8.5)
    axes[0, 0].grid(True, linestyle="--", alpha=0.4)

    # 2. Суммарный Throughput (столбцы)
    b1 = axes[0, 1].bar(x - w/2, wb_agg, w, label="WB", color=c_wb, edgecolor="black", alpha=0.85)
    b2 = axes[0, 1].bar(x + w/2, sb_agg, w, label="SB", color=c_sb, edgecolor="black", alpha=0.85)
    axes[0, 1].set_ylabel("Throughput соты (Мбит/с)", fontsize=9.5)
    axes[0, 1].set_title("2. Суммарная емкость соты (столбцы)", fontsize=11, fontweight="bold")
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(scheds, fontsize=10)
    for b in list(b1) + list(b2):
        h = b.get_height()
        axes[0, 1].text(b.get_x() + b.get_width()/2., h + 0.25, f"{h:.1f}", ha='center', va='bottom', fontsize=8, fontweight='bold')
    axes[0, 1].legend(loc="upper left", fontsize=8.5)
    axes[0, 1].grid(True, linestyle="--", alpha=0.4)

    # 3. Средняя задержка пакетов (столбцы на лог-шкале)
    b1 = axes[0, 2].bar(x - w/2, wb_lat, w, label="WB", color=c_wb, edgecolor="black", alpha=0.85)
    b2 = axes[0, 2].bar(x + w/2, sb_lat, w, label="SB", color=c_sb, edgecolor="black", alpha=0.85)
    axes[0, 2].set_yscale("log")
    axes[0, 2].set_ylim(5, 5000)
    axes[0, 2].set_ylabel("Задержка (мс, лог)", fontsize=9.5)
    axes[0, 2].set_title("3. Средняя задержка пакетов (столбцы, лог)", fontsize=11, fontweight="bold")
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(scheds, fontsize=10)
    for b in list(b1) + list(b2):
        h = b.get_height()
        axes[0, 2].text(b.get_x() + b.get_width()/2., h * 1.25, f"{h:.0f}", ha='center', va='bottom', fontsize=8, fontweight='bold')
    axes[0, 2].legend(loc="upper left", fontsize=8.5)
    axes[0, 2].grid(True, linestyle="--", alpha=0.4)

    # 4. Индекс справедливости Джейна (столбцы)
    b1 = axes[1, 0].bar(x - w/2, wb_jfi, w, label="WB", color=c_wb, edgecolor="black", alpha=0.85)
    b2 = axes[1, 0].bar(x + w/2, sb_jfi, w, label="SB", color=c_sb, edgecolor="black", alpha=0.85)
    axes[1, 0].set_ylim(0, 1.25)
    axes[1, 0].set_ylabel("Jain's Fairness Index", fontsize=9.5)
    axes[1, 0].set_title("4. Индекс справедливости Джейна (столбцы)", fontsize=11, fontweight="bold")
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(scheds, fontsize=10)
    for b in list(b1) + list(b2):
        h = b.get_height()
        axes[1, 0].text(b.get_x() + b.get_width()/2., h + 0.03, f"{h:.2f}", ha='center', va='bottom', fontsize=8, fontweight='bold')
    axes[1, 0].legend(loc="upper right", fontsize=8.5)
    axes[1, 0].grid(True, linestyle="--", alpha=0.4)

    # 5. Утилизация PRB (столбцы)
    b1 = axes[1, 1].bar(x - w/2, wb_prb, w, label="WB", color=c_wb, edgecolor="black", alpha=0.85)
    b2 = axes[1, 1].bar(x + w/2, sb_prb, w, label="SB", color=c_sb, edgecolor="black", alpha=0.85)
    axes[1, 1].set_ylim(0, 115)
    axes[1, 1].set_ylabel("Утилизация (%)", fontsize=9.5)
    axes[1, 1].set_title("5. Утилизация PRB (столбцы)", fontsize=11, fontweight="bold")
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(scheds, fontsize=10)
    for b in list(b1) + list(b2):
        h = b.get_height()
        axes[1, 1].text(b.get_x() + b.get_width()/2., h + 2.0, f"{h:.0f}%", ha='center', va='bottom', fontsize=8, fontweight='bold')
    axes[1, 1].legend(loc="upper left", fontsize=8.5)
    axes[1, 1].grid(True, linestyle="--", alpha=0.4)

    # 6. Throughput худшего абонента (столбцы)
    b1 = axes[1, 2].bar(x - w/2, wb_w, w, label="WB", color=c_wb, edgecolor="black", alpha=0.85)
    b2 = axes[1, 2].bar(x + w/2, sb_w, w, label="SB", color=c_sb, edgecolor="black", alpha=0.85)
    axes[1, 2].set_ylabel("Throughput худшего UE (Мбит/с)", fontsize=9.5)
    axes[1, 2].set_title("6. Скорость худшего абонента (столбцы)", fontsize=11, fontweight="bold")
    axes[1, 2].set_xticks(x)
    axes[1, 2].set_xticklabels(scheds, fontsize=10)
    for b in list(b1) + list(b2):
        h = b.get_height()
        axes[1, 2].text(b.get_x() + b.get_width()/2., h + 0.04, f"{h:.2f}", ha='center', va='bottom', fontsize=8, fontweight='bold')
    axes[1, 2].legend(loc="upper left", fontsize=8.5)
    axes[1, 2].grid(True, linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "kpi_matrix_dashboard.png"), dpi=150)
    plt.savefig(os.path.join(output_dir, "kpi_dashboard.png"), dpi=150)
    plt.savefig(os.path.join(output_dir, "kpi_comparison.png"), dpi=150)
    plt.close()
    print(f"[*] All plots generated in {output_dir}/")

    # Mirror to report repo if exists
    rep_repo_dir = "/home/Avadik/Prog/Ns3-YADRO-reps"
    if os.path.exists(rep_repo_dir):
        for f in os.listdir(output_dir):
            if f.endswith(".png"):
                src_p = os.path.join(output_dir, f)
                dst_p = os.path.join(rep_repo_dir, f)
                shutil.copy2(src_p, dst_p)
        print(f"[*] Mirrored plots to {rep_repo_dir}/")

if __name__ == "__main__":
    modes = ["WB", "SB"]
    scheds = ["RR", "PF", "BCQI"]
    matrix_data = {}

    print("\n" + "=" * 92)
    print("      LTE MAC SCHEDULER MATRIX: RR vs PF vs BCQI (Wideband vs Subband)")
    print("=" * 92)
    print(f"| {'Case':<10} | {'Agg Th (Mbps)':<14} | {'Mean Th':<10} | {'Delay (ms)':<10} | {'JFI':<8} | {'PRB Util':<10} | {'Worst UE':<10} |")
    print("|" + "-" * 90 + "|")

    for m in modes:
        for s in scheds:
            d = f"/home/Avadik/Prog/ns-3.43/reports/{m}/{s}"
            res = evaluate_scenario(d)
            if res:
                matrix_data[f"{m}_{s}"] = res
                name = f"{m}_{s}"
                print(f"| {name:<10} | {res['agg_throughput']:>12.3f}   | {res['mean_throughput']:>8.3f} | {res['mean_delay']:>8.2f} | {res['jfi']:>6.4f} | {res['prb_util']:>8.1f}% | {res['worst_ue_th']:>8.3f} |")

    print("=" * 92 + "\n")
    generate_matrix_plots(matrix_data, output_dir="reports")
