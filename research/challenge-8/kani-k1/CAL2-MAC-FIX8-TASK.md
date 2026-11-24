# CAL2 Darwin · FIX8: окно setup и состав macOS

Run 45331131850 (macos, M1 7 GiB): учёт Darwin исправен; overlay kani list 1315 с, пик 3,27 GB; base kani list остановлен 45-минутным дедлайном setup на 1025 с. Засчитано 0. Артефакт /root/ch8-artifacts/run-45331131850.

Решение планера (pane 8, 2026-11-24): один macOS job, оба нативных kani list, 65 мин на setup в supervisor и workflow. Состав по порядку:
1. NET-U8-N08, 2. NET-U8-N09, 3. batch-auto и 4. batch-jobs1 (пара N8/N9, прежнее правило допуска), затем 5. NET-N25, 6. NET-U64-N13, 7. MERGE-N32 (Below), 8. GEN-N16-SMALL.
Итого около 55 мин одиночных слотов и 20 мин batch, 163 из 225 мин с аттестацией, финализацией и резервом.

Поверх control 52b3048ca1. Менять только: Darwin-дедлайн setup (45 → 65 мин) в supervisor/run и workflow, Darwin roster и порядок слотов (окна каждого слота прежние), расчёт latest start и бюджетов под новый состав, тесты roster/часов. Исключённые корни (S13-N13, S13-N17, S13-N32-R, NET-U64-N32, GEN-N16-WIDE) получают именные NOT_RUN с причиной EXCLUDED_BY_PLAN в receipts. Сценарий партиций на macOS считает только по фактически замеренным корням и помечает остальные UNKNOWN. Не менять: request и bundle (если roster Darwin зашит в CI-REQUEST.json, пересобрать request, записать новый SHA-256 и показать diff), overlay std, Linux, параметры census FIX7, caps.

Проверка: полный suite, git diff --check, синтетика часов: 65 мин setup + слоты + batch + аттестация + финализация укладываются в 225 мин; YAML и exact gate. Новый control (parent 52b3048ca1), trigger с тем же tree и sole parent 467af9cb8d. Раздел FIX8 в начале CAL2-MAC-FIX-HANDOFF.md, READY_FOR_REVIEW, коммит g0 [skip ci]. Ревью — только diff; блокируют только: отклонение от состава и окон этого задания, нарушение бюджета 225 мин, изменение Linux, census или caps. Локально без cargo, rustc, Kani, CBMC; CI и push не запускать.
