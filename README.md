# Исследование и сравнительный анализ MAC-планировщиков в ns-3 (LTE / 5G LENA)

Репозиторий содержит аналитические отчёты, графические материалы и воспроизводимый инструментарий для моделирования и анализа алгоритмов диспетчеризации (**MAC Scheduling**) в среде симулятора **ns-3.43 (модуль LENA)** в рамках практики YADRO.

---

## Структура репозитория

```
Ns3-YADRO-reps/
├── README.md                      # Главная страница и сводная навигация
├── .gitignore                     # Исключения для git (кэши Python, OS, логи)
├── week-01/                       # Отчёт и графические материалы за 1-ю неделю
│   ├── week-01.md                 # Аналитический отчёт: базовое сравнение RR, PF, BCQI
│   ├── README.md -> week-01.md    # Симлинк для авто-рендеринга в веб-интерфейсе
│   └── figures/                   # Столбчатые диаграммы метрик 1-й недели
│       ├── 01_throughput_matrix.png
│       ├── 02_latency_matrix.png
│       ├── 03_fairness_jfi_matrix.png
│       ├── 04_prb_utilization_matrix.png
│       ├── 05_worst_ue_matrix.png
│       └── kpi_matrix_dashboard.png
├── week-02/                       # Отчёт и графические материалы за 2-ю неделю
│   ├── week-02.md                 # Аналитический отчёт: радары, ресурсная сетка OFDMA
│   ├── README.md -> week-02.md    # Симлинк для авто-рендеринга в веб-интерфейсе
│   └── figures/                   # Многомерные графики 2-й недели
│       ├── 01_radar_comparison_wb_sb.png
│       ├── 02_resource_grid_rr_pf_bcqi.png
│       ├── 03_per_ue_throughput_ns3.png
│       └── 04_latency_and_fairness_ns3.png
└── scripts/                       # Автономный инструментарий постобработки и генерации
    ├── analyze_kpis.py            # Расчёт метрик (Throughput, Delay, JFI, PRB по 3GPP TS 36.213)
    ├── generate_ns3_pure_plots.py # Построение радаров, ресурсной сетки, per-UE и задержек
    └── generate_resource_grid.py  # Генератор детальной 2D-сетки распределения PRB
```

---

## Отчёты по этапам исследования

| Этап | Документ | Исследуемые аспекты и алгоритмы |
| :--- | :--- | :--- |
| **Неделя 1** | **[`week-01/week-01.md`](week-01/week-01.md)** | Базовое сравнение планировщиков **Round Robin (RR)**, **Proportional Fair (PF)** и **Best CQI (BCQI)** в условиях плоского (Wideband) и селективного (Subband) каналов. Оценка суммарной и средней ёмкости соты, задержек, утилизации PRB и индекса Джейна (JFI). |
| **Неделя 2** | **[`week-02/week-02.md`](week-02/week-02.md)** | Многокритериальный анализ и радарное профилирование (5 ортогональных осей). **Физическая ресурсная сетка (Time-Frequency OFDMA Grid)**: визуализация 20% простоя PRB у RR и монополии в BCQI. Попользовательские скорости UE 1..10, логарифмический анализ задержек и инженерные рекомендации для RAN YADRO. |

---

## Навигация по графикам

### Материалы Недели 1 ([`week-01/figures/`](week-01/figures/))
- [`01_throughput_matrix.png`](week-01/figures/01_throughput_matrix.png) — Суммарная и средняя пропускная способность соты
- [`02_latency_matrix.png`](week-01/figures/02_latency_matrix.png) — Средняя задержка доставки пакетов (лог-шкала)
- [`03_fairness_jfi_matrix.png`](week-01/figures/03_fairness_jfi_matrix.png) — Индекс справедливости Джейна (JFI)
- [`04_prb_utilization_matrix.png`](week-01/figures/04_prb_utilization_matrix.png) — Процент утилизации радиоресурса PRB
- [`05_worst_ue_matrix.png`](week-01/figures/05_worst_ue_matrix.png) — Пропускная способность худшего абонента соты
- [`kpi_matrix_dashboard.png`](week-01/figures/kpi_matrix_dashboard.png) — Сводный дашборд ключевых метрик

### Материалы Недели 2 ([`week-02/figures/`](week-02/figures/))
- [`01_radar_comparison_wb_sb.png`](week-02/figures/01_radar_comparison_wb_sb.png) — **Двухпанельный радарный график (Wideband vs Subband)** по 5 осям (`DL_THROUGHPUT`, `DL_BLER`, `PRB_UTIL`, `MAC_DL_LATENCY`, `DL_SERVICE_GAP/MAX_TTI`)
- [`02_resource_grid_rr_pf_bcqi.png`](week-02/figures/02_resource_grid_rr_pf_bcqi.png) — **Частотно-временная ресурсная сетка OFDMA (25 PRB $\times$ 35 TTI)**: распределение ресурсов между 10 абонентами для RR, PF и BCQI
- [`03_per_ue_throughput_ns3.png`](week-02/figures/03_per_ue_throughput_ns3.png) — **Распределение скоростей по терминалам (UE 1..10)** в режимах WB и SB
- [`04_latency_and_fairness_ns3.png`](week-02/figures/04_latency_and_fairness_ns3.png) — **Сопоставление задержек (мс, лог) и справедливости Джейна (JFI)**
