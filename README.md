# Сравнение планировщиков MAC в ns-3 (LTE / LENA)

Репозиторий с отчётами, графиками и скриптами по исследованию алгоритмов планирования MAC (**Round Robin**, **Proportional Fair**, **Best CQI**) в симуляторе **ns-3.43**.

---

## Структура репозитория

```
Ns3-YADRO-reps/
├── README.md                      # Навигация по репозиторию
├── .gitignore                     # Игнорируемые файлы
├── reports/                       # Все отчёты в markdown
│   ├── week-01.md                 # Отчёт за 1 неделю (базовое сравнение RR, PF, BCQI)
│   └── week-02.md                 # Отчёт за 2 неделю (радары, ресурсная сетка, per-UE)
├── figures/                       # Все графики к отчётам
│   ├── week-01/                   # Графика за 1 неделю (столбчатые диаграммы)
│   │   ├── 01_throughput_matrix.png
│   │   ├── 02_latency_matrix.png
│   │   ├── 03_fairness_jfi_matrix.png
│   │   ├── 04_prb_utilization_matrix.png
│   │   ├── 05_worst_ue_matrix.png
│   │   └── kpi_matrix_dashboard.png
│   └── week-02/                   # Графика за 2 неделю
│       ├── 01_radar_comparison_wb_sb.png      # Радары WB/SB (PF, RR, BCQI)
│       ├── 02_resource_grid_rr_pf_bcqi.png    # Ресурсная сетка 25 PRB x 35 TTI
│       ├── 03_per_ue_throughput_ns3.png       # Скорости по абонентам UE 1..10
│       └── 04_latency_and_fairness_ns3.png    # Задержка на лог-шкале и JFI
└── scripts/                       # Скрипты парсинга и генерации графиков
    ├── analyze_kpis.py            # Парсер FlowMonitor и DlMacStats по 3GPP TS 36.213
    ├── generate_ns3_pure_plots.py # Генератор графиков за 2 неделю
    └── generate_resource_grid.py  # Генератор ресурсной сетки PRB
```

---

## Отчёты

- **[`reports/week-01.md`](reports/week-01.md)** — Сравнение RR, PF и Best CQI в режимах Wideband и Subband (суммарный и средний Throughput, задержка, индекс Джейна, утилизация PRB, скорость худшего абонента).
- **[`reports/week-02.md`](reports/week-02.md)** — Многокритериальные радарные диаграммы (WB vs SB), физическая ресурсная сетка (Time-Frequency OFDMA Resource Grid), попользовательское распределение скоростей UE 1..10, задержки на лог-шкале и выводы.

---

## Графика к отчётам

### Неделя 1 ([`figures/week-01/`](figures/week-01/))
- [`01_throughput_matrix.png`](figures/week-01/01_throughput_matrix.png) — Суммарная и средняя скорость соты
- [`02_latency_matrix.png`](figures/week-01/02_latency_matrix.png) — Задержка доставки пакетов
- [`03_fairness_jfi_matrix.png`](figures/week-01/03_fairness_jfi_matrix.png) — Индекс справедливости Джейна
- [`04_prb_utilization_matrix.png`](figures/week-01/04_prb_utilization_matrix.png) — Утилизация PRB
- [`05_worst_ue_matrix.png`](figures/week-01/05_worst_ue_matrix.png) — Скорость худшего абонента
- [`kpi_matrix_dashboard.png`](figures/week-01/kpi_matrix_dashboard.png) — Сводный дашборд

### Неделя 2 ([`figures/week-02/`](figures/week-02/))
- [`01_radar_comparison_wb_sb.png`](figures/week-02/01_radar_comparison_wb_sb.png) — Радарные диаграммы для Wideband и Subband (PF, RR, BCQI)
- [`02_resource_grid_rr_pf_bcqi.png`](figures/week-02/02_resource_grid_rr_pf_bcqi.png) — Ресурсная сетка PRB (25 PRB $\times$ 35 TTI) для RR, PF и BCQI
- [`03_per_ue_throughput_ns3.png`](figures/week-02/03_per_ue_throughput_ns3.png) — Скорость каждого из 10 абонентов
- [`04_latency_and_fairness_ns3.png`](figures/week-02/04_latency_and_fairness_ns3.png) — Задержка пакетов (лог-шкала) и индекс справедливости
