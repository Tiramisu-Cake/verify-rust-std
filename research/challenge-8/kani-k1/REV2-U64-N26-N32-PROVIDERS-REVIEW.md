# REV2 u64 N26–N32 providers · ревью

## R1

Независимое ревью (Claude, `smallsort-reviewer`) 2026-11-27. **GO_WITH_NITS**, блокеров нет; координатор требует FIX1 по пп. 1, 3–5 до запуска. Пины: Std `72bb79d26dd495d0461c6e6d3c05d21c2d1b1878` / tree `c513d0ec1a`, Control `a068b3ac3b6d75b8897ff9af193ac09b0b02c5f3` / tree `1f91e3aa4cfa3cdced3d97944214b018cda3772d`, review-trigger `0bb712a1ea`, request `fcf327b2…e0b6cc`, handoff g0 `baad5ddc17`.

1. **Should-fix (метка evidence).** Odd-center `check_evidence.copy_sites` указывает actual `smallsort.rs:1034:13` (`CI-REQUEST.json:2821/3053/3162`, `request.py:828-831`), а копия выполняется в транскрипции `rev2_u64_n26_n32_providers.rs:1018:9/1104:9/1190:9`. `results.py:600` переносит метку в receipt без сверки — receipt выглядел бы как нативная привязка центра к actual-коду. Записывать собственный site с пометкой «transcribes :1034:13», как в N23/N25.
2. **Should-fix (процесс).** Handoff ссылается на отдельное ревью девяти адресных переносов вставок, записи которого в g0 нет. **Ревьюер R1 сверил переносы сам и принимает все девять** при условиях: отсортированный префикс, инициализированный tail; `insert_tail` (`smallsort.rs:701–735`) и driver (`:742–769`) используют только относительную арифметику; максимум B17 R15 → `v[17..33]`; выравнивание 8 байт. Это внешние рёбра того же класса, что rel11 в N22–N25 consumer, — самые слабые места композиции; фиксируются в admission.
3. Nit. `request.py:668`: вернуть проверку унаследованного шага layout `b09c6f22→a1335f8e`.
4. Nit. Геометрия swap-слотов скопирована из bits («45-pair network», `CI-REQUEST.json:4382` и др.).
5. Nit. Неиспользуемая `target_name` в `request.py:822`.
6. Nit. `test_results.py:688`: `== "MISMATCHED"` ослаблено до `!= "MATCHED"`.
7. Операционно: новый trigger без `[skip ci]`.

Проверено и в порядке: геометрия против `smallsort.rs:383–425, :1000–1042` для N26–N32; 45 пар; pair/центр по шаблону N25/N23; компаратор; посты и covers; только скалярные сравнения, циклы ≤34; стоимость PAIR m13–16 VT 55–70 с, S13 B14–B17 ~48 с / ~2,46 GiB; часы 18 слотов, резерв 136:30 ≤ 140 мин; Std-дельта 3 файла, rustfmt чист; все SHA-256 и 64-hex хэши handoff; авторы; suite 130/130.

## R2 · FIX1

Независимое повторное ревью (Claude, `smallsort-reviewer`) 2026-11-27. **GO_WITH_NITS**, блокеров и should-fix нет. Пины: Std `72bb79d26d` (без изменений), Control FIX1 `f50d86dffac4c1265797189511feaec8bba9d09b` / tree `dcccfc903bb1953d2184282c5fc1da5067e6f6bb`, review-trigger `68aa2e4b93`, request `3d97d789…9043`, handoff g0 `a4fc7f66e7`.

- R1-1 исправлено: `copy_sites` центров N27/N29/N31 — собственные сайты модуля `:1018:9/:1104:9/:1190:9` с `transcribes: smallsort.rs:1034:13`; receipt (`checked_write_set`) больше не заявляет нативную привязку; новый тест отличает исправленную версию от R1.
- R1-2 исправлено: ссылка на несуществующее ревью удалена, приёмка девяти переносов ссылается на R1.
- R1-3…6 исправлены. Diff Control ограничен `CI-REQUEST.json`, `request.py`, `test_results.py`; selectors, исходы, covers, лимиты, workflow прежние.
- SHA-256 request, roster `5b12d12a…`, bindings `9fd4a201…`, bundle `d9b30842…` (HEAD `72bb79d26d`); trigger tree == Control tree; авторы; suite 131/131.
- Nit: новые проверки gate/layout не покрыты тестами suite (ревьюер проверил подмены скриптом); имена `actual_odd_center_n27/29/31` оставлены, как у N23/N25.
