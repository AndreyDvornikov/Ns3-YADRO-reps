# Отчёты по исследованию и оптимизации MAC-планировщиков в ns-3 (LTE / 5G LENA)

Репозиторий содержит аналитические отчёты, графики и воспроизводимые скрипты для сравнительного исследования алгоритмов диспетчеризации (MAC Scheduling) в симуляторе **ns-3.43 (модуль LENA)** в рамках практики YADRO.

---

## Структура отчётов

| Отчёт | Тема | Ключевые исследуемые аспекты |
| :--- | :--- | :--- |
| **[`week-01.md`](week-01.md)** | Сравнение базовых планировщиков (RR, PF, Best CQI) в ns-3.43 | Суммарная и средняя пропускная способность, задержка RLC/MAC, индекс справедливости Джейна (JFI), утилизация PRB по 3GPP TS 36.213, деградация худшего абонента. |
| **[`week-02.md`](week-02.md)** | Многокритериальный анализ, радарное профилирование (PF, RR, BCQI) и ресурсная сетка PRB в ns-3 | Двухпанельные радарные диаграммы (Wideband vs Subband), физическая ресурсная сетка PRB во времени и частоте (OFDMA Resource Grid 25 PRB $\times$ 35 TTI), попользовательское распределение скоростей UE 1..10, динамика задержек на лог-шкале и справедливость Джейна. |

---

## Навигация по графическим материалам

### Неделя 1 (Базовые столбчатые диаграммы метрик)
- [`01_throughput_matrix.png`](01_throughput_matrix.png) — Суммарный и средний Throughput по сценариям
- [`02_latency_matrix.png`](02_latency_matrix.png) — Средняя задержка доставки пакетов (лог-шкала)
- [`03_fairness_jfi_matrix.png`](03_fairness_jfi_matrix.png) — Индекс справедливости Джейна
- [`04_prb_utilization_matrix.png`](04_prb_utilization_matrix.png) — Утилизация радиоресурса PRB
- [`05_worst_ue_matrix.png`](05_worst_ue_matrix.png) — Скорость худшего абонента
- [`kpi_matrix_dashboard.png`](kpi_matrix_dashboard.png) — Сводный дашборд всех пяти метрик

### Неделя 2 (Радарные профили, физическая ресурсная сетка и per-UE анализ в ns-3)
- [`01_radar_comparison_wb_sb.png`](01_radar_comparison_wb_sb.png) — **Радарное сравнение планировщиков (PF, RR, BCQI)** в режимах Wideband (слева) и Subband (справа) по 5 осям: `DL_THROUGHPUT`, `DL_BLER`, `PRB_UTIL`, `MAC_DL_LATENCY`, `DL_SERVICE_GAP/MAX_TTI`
- [`02_resource_grid_rr_pf_bcqi.png`](02_resource_grid_rr_pf_bcqi.png) — **Частотно-временная ресурсная сетка (OFDMA Resource Grid)**: физическая раскладка PRB 0–24 по TTI 0–34 для Round Robin (с фиксацией 20% простоя), Proportional Fair и Best CQI (с фиксацией монополии UE 1)
- [`03_per_ue_throughput_ns3.png`](03_per_ue_throughput_ns3.png) — **Распределение скоростей по абонентам UE 1..10**: сопоставление пользовательской пропускной способности в WB и SB
- [`04_latency_and_fairness_ns3.png`](04_latency_and_fairness_ns3.png) — **Задержка доставки пакетов (лог-шкала) и индекс справедливости Джейна (JFI)**
