# Отчёты по исследованию и оптимизации MAC-планировщиков (ns-3 / 5G LENA / srsRAN)

Репозиторий содержит аналитические отчёты, графики и воспроизводимые скрипты для сравнительного исследования алгоритмов диспетчеризации (MAC Scheduling) в сетях LTE и 5G NR в рамках практики YADRO.

---

## Структура отчётов

| Отчёт | Тема | Ключевые исследуемые аспекты |
| :--- | :--- | :--- |
| **[`week-01.md`](week-01.md)** | Сравнение базовых планировщиков (RR, PF, Best CQI) в ns-3.43 | Суммарная и средняя пропускная способность, задержка RLC/MAC, индекс справедливости Джейна (JFI), утилизация PRB по 3GPP TS 36.213, деградация худшего абонента. |
| **[`week-02.md`](week-02.md)** | Многокритериальный анализ, радарное профилирование (RR, PF, BCQI, ML) и ресурсная сетка PRB | Физическая ресурсная сетка (Time-Frequency grid по 25 PRB), радарные диаграммы (WB vs SB), empirical CDF по CQI-режимам (граница / центр соты), Парето-граница SE–JFI, TTI Service Gap, BLER и адаптация MCS. |

---

## Навигация по графическим материалам

### Неделя 1 (Базовые столбчатые диаграммы метрик)
- [`01_throughput_matrix.png`](01_throughput_matrix.png) — Суммарный и средний Throughput по сценариям
- [`02_latency_matrix.png`](02_latency_matrix.png) — Средняя задержка доставки пакетов (лог-шкала)
- [`03_fairness_jfi_matrix.png`](03_fairness_jfi_matrix.png) — Индекс справедливости Джейна
- [`04_prb_utilization_matrix.png`](04_prb_utilization_matrix.png) — Утилизация радиоресурса PRB
- [`05_worst_ue_matrix.png`](05_worst_ue_matrix.png) — Скорость худшего абонента
- [`kpi_matrix_dashboard.png`](kpi_matrix_dashboard.png) — Сводный дашборд всех пяти метрик

### Неделя 2 (Ресурсные сетки, многомерные радары, CDF и Парето-анализ)
- [`05_resource_grid_rr_pf_bcqi.png`](05_resource_grid_rr_pf_bcqi.png) — **Частотно-временная ресурсная сетка (OFDMA Grid)**: сопоставление аллокации PRB 0–24 по TTI 0–35 для Round Robin, Proportional Fair и Best CQI с визуализацией 20% простоя PRB в RR и монополизации в BCQI
- [`01_radar_comparison_wb_sb.png`](01_radar_comparison_wb_sb.png) — Радарное сравнение планировщиков (ML, PF, RR) по 5 осям: `DL_THROUGHPUT`, `DL_BLER`, `PRB_UTIL`, `MAC_DL_LATENCY`, `DL_SERVICE_GAP/MAX_TTI`
- [`01b_radar_comparison_bcqi.png`](01b_radar_comparison_bcqi.png) — **Радарное сравнение с включением Best CQI**: наглядная демонстрация всплеска задержки и разрывов TTI при коллапсе справедливости
- [`02_cqi_regime_throughput_cdf.png`](02_cqi_regime_throughput_cdf.png) — Эмпирическая функция распределения (CDF) скорости по диапазонам CQI (Low, Mid, High)
- [`03_se_vs_fairness_pareto.png`](03_se_vs_fairness_pareto.png) — Карта Парето: Спектральная эффективность (SE) vs Индекс справедливости (JFI) с началом в (0; 0)
- [`04_worst_case_throughput.png`](04_worst_case_throughput.png) — Анализ наихудшей пропускной способности (5-й перцентиль и граничные терминалы)
