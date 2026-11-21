# Исследование и сравнительный анализ MAC-планировщиков в ns-3 (LTE / 5G LENA)

Репозиторий содержит аналитические отчёты, графические материалы и воспроизводимый инструментарий для моделирования и анализа алгоритмов диспетчеризации (**MAC Scheduling**) в среде симулятора **ns-3.43 (модуль LENA)** в рамках практики YADRO.

---

## Структура репозитория

```
Ns3-YADRO-reps/
├── README.md                      # Главная страница и сводная навигация
├── .gitignore                     # Исключения для git (кэши Python, OS, логи)
├── reports/                       # Все аналитические отчёты (Markdown в одном месте)
│   ├── week-01.md                 # Отчёт 1: базовое исследование RR, PF, BCQI
│   └── week-02.md                 # Отчёт 2: радары WB/SB, ресурсная сетка OFDMA, per-UE
├── figures/                       # Все графические материалы (вынесены отдельно)
│   ├── week-01/                   # Графика 1-й недели
│   │   ├── 01_throughput_matrix.png
│   │   ├── 02_latency_matrix.png
│   │   ├── 03_fairness_jfi_matrix.png
│   │   ├── 04_prb_utilization_matrix.png
│   │   ├── 05_worst_ue_matrix.png
│   │   └── kpi_matrix_dashboard.png
│   └── week-02/                   # Графика 2-й недели
│       ├── 01_radar_comparison_wb_sb.png      # Радары WB/SB (PF, RR, BCQI)
│       ├── 02_resource_grid_rr_pf_bcqi.png    # Частотно-временная сетка OFDMA
│       ├── 03_per_ue_throughput_ns3.png       # Скорости абонентов UE 1..10
│       └── 04_latency_and_fairness_ns3.png    # Задержка (лог-шкала) и JFI
└── scripts/                       # Автономный инструментарий для ns-3
    ├── analyze_kpis.py            # Парсер FlowMonitor и DlMacStats по 3GPP TS 36.213
    ├── generate_ns3_pure_plots.py # Генератор всех графиков 2-й недели
    └── generate_resource_grid.py  # Генератор детальной ресурсной сетки PRB
```

---

## Аналитические отчёты ([`reports/`](reports/))

| Отчёт | Тема | Ключевые исследуемые аспекты |
| :--- | :--- | :--- |
| **[`reports/week-01.md`](reports/week-01.md)** | Сравнение базовых планировщиков (RR, PF, Best CQI) в ns-3.43 | Суммарная и средняя пропускная способность, задержка RLC/MAC, индекс справедливости Джейна (JFI), утилизация PRB по 3GPP TS 36.213, деградация худшего абонента. |
| **[`reports/week-02.md`](reports/week-02.md)** | Многокритериальный анализ, радарное профилирование и ресурсная сетка PRB | Двухпанельные радары (Wideband vs Subband), физическая ресурсная сетка PRB во времени и частоте (OFDMA Resource Grid 25 PRB $\times$ 35 TTI), попользовательские скорости UE 1..10, динамика задержек на лог-шкале и рекомендации для RAN YADRO. |

---

## Навигация по графикам ([`figures/`](figures/))

### Материалы Недели 1 ([`figures/week-01/`](figures/week-01/))
- [`01_throughput_matrix.png`](figures/week-01/01_throughput_matrix.png) — Суммарная и средняя пропускная способность соты
- [`02_latency_matrix.png`](figures/week-01/02_latency_matrix.png) — Средняя задержка доставки пакетов (лог-шкала)
- [`03_fairness_jfi_matrix.png`](figures/week-01/03_fairness_jfi_matrix.png) — Индекс справедливости Джейна (JFI)
- [`04_prb_utilization_matrix.png`](figures/week-01/04_prb_utilization_matrix.png) — Процент утилизации радиоресурса PRB
- [`05_worst_ue_matrix.png`](figures/week-01/05_worst_ue_matrix.png) — Пропускная способность худшего абонента соты
- [`kpi_matrix_dashboard.png`](figures/week-01/kpi_matrix_dashboard.png) — Сводный дашборд ключевых метрик

### Материалы Недели 2 ([`figures/week-02/`](figures/week-02/))
- [`01_radar_comparison_wb_sb.png`](figures/week-02/01_radar_comparison_wb_sb.png) — **Двухпанельный радарный график (Wideband vs Subband)** по 5 осям (`DL_THROUGHPUT`, `DL_BLER`, `PRB_UTIL`, `MAC_DL_LATENCY`, `DL_SERVICE_GAP/MAX_TTI`)
- [`02_resource_grid_rr_pf_bcqi.png`](figures/week-02/02_resource_grid_rr_pf_bcqi.png) — **Частотно-временная ресурсная сетка OFDMA (25 PRB $\times$ 35 TTI)**: распределение ресурсов между 10 абонентами для RR, PF и BCQI
- [`03_per_ue_throughput_ns3.png`](figures/week-02/03_per_ue_throughput_ns3.png) — **Распределение скоростей по терминалам (UE 1..10)** в режимах WB и SB
- [`04_latency_and_fairness_ns3.png`](figures/week-02/04_latency_and_fairness_ns3.png) — **Сопоставление задержек (мс, лог) и справедливости Джейна (JFI)**
