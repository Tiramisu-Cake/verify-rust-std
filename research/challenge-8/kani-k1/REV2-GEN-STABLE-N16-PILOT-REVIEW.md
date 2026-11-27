# REV2 general/stable N16 pilot · ревью

## R1

Независимое ревью (Claude, `smallsort-reviewer`) 2026-11-27. **GO_WITH_NITS**, блокеров и should-fix нет. Пины: Std `14a5a7322a050c7d5028054acc5825172d43c14c` / tree `bf379fc6b4`, Control `046b1e0f8457390b1e6ffea9dd779a0a4acc053e` / tree `9021966b36dcbbf0a7f36d9065bd0dae580a4e98`, review-trigger `2783b10ee6`, задание g0 `b3614058e7`, handoff g0 `39877929b1`.

1. Nit (правдоподобно). Typed-copy свойства трёх Wide-слотов ожидают имя `ptr::copy_nonoverlapping::<slice::sort::shared::smallsort::verify::rev2_gen_stable_n16_pilot::Wide>`; прецедентов с не-примитивным аргументом нет. При ином печатном пути строки уйдут в `MISMATCHED` (fail-safe, итог `OPEN`). Действие при несовпадении — взять фактический ID из проекции, gate не ослаблять.
2. Nit. Комментарий `rev2_gen_stable_n16_pilot.rs:235` «Transcription of smallsort.rs:329–330» накрывает и локальную копию (`:236`), и actual `insert_tail` (`:237`). В request `transcribes` стоит только у `236:9 → smallsort.rs:329:17`, что проверяет `check_pilot_copy_sites`. Координаты заморожены, правку не делаем.

Проверено и в порядке: identity трёх коммитов и SHA-256 request `c105664a…` и bundle `c11285e3…` (83 842 байта, HEAD `14a5a732`, prerequisite `dab03cf510`); Std-дельта — новый модуль, check-cfg и две строки `mod`, runtime побайтно; actual вызовы `sort8_stable` (`:300–305`), `sort4_stable` (`:311`), `insert_tail`, `merge_up`/`merge_down` с курсорами `:1014–1024` и tie-правилами `:883`, `:916–920`; 204 = Σ(k+1)²; маршрут Wide `:189 → :222 → :261–273`, константные проверки размера 24, `!has_efficient_in_place_swap`, 1152 ≤ 4096; оракулы (сортировка, кратность по произвольному probe, frame, запись по меткам, `STABLE_EQUAL_KEYS`, точный пост вставки), covers не вакуумны; только скалярные сравнения, циклы ≤32, scratch48 разбит на интервалы; лимиты 120 с VT / 180 с cold / 4 GiB, часы 100-минутного job; discovery 163 + 6; ожидание 6/6 VERIFIED; tree pin; `test_results`/`test_run` 77/77; авторы, `[skip ci]`, без решётки перед цифрой.

## R2 · FIX1

Независимое ревью (Claude, `smallsort-reviewer`) 2026-11-27. **GO_WITH_NITS**, блокеров и should-fix нет. Пины: Std `5a8702f59ae309b8069d380b1e3887fd48c2564b` / tree `76ff14e1…`, parent `14a5a7322a`; Control `bcf4fd366d1fc3fe4e045bb8c6f3b54189a92435` / tree `981944277c…`, parent `046b1e0f84`; review-trigger `f3b6b68863` (tree равен Control, sole parent `467af9cb8d`); request `83e332c9…`, bundle `ded7e86e…` (83 486 байт); задание g0 `86e0c6a5a1`, handoff g0 `75280f628a`.

1. Nit. `ch8-cal1/test_run.py:531` ожидает подстроку `"REV2"` вместо `"standard harness has a contract target"`; при включённом FIX1 срабатывает «Check object mismatch», но подстрока не различает guard. Production `run.py:346–352` корректен. Исправить при следующей правке пакета.
2. Nit (fail-safe). Gate требует column 5 для contract/assigns внутри `mod fix1` (`561:5`, `658:5`); реальным прогоном не подтверждено. При несовпадении — `MISMATCHED`, итог `OPEN`; взять фактическое место из проекции, gate не ослаблять.
3. Процесс. Review-trigger несёт `[skip ci]`; trigger для запуска пересоздаётся координатором с тем же tree.

Проверено и в порядке: Std-дельта — check-cfg и +200 строк, старый модуль — побайтный префикс; actual `merge_up` (`:885:9`) и `merge_down` (`:918:9`) с курсорами и единственным `modifies`; tie-правила; точные посты курсоров (down на c=7 — указатель до D только сравнивается); frame V18 кроме одной цели и scratch48 интервалами `0..32`/`32..48`; только адресные предпосылки; циклы ≤32; 7 covers на корень; композиция up→down (`:1022–1025`) — внешнее ребро; roster 169 + 2, лимиты и часы 90-минутного job, отдельная переменная tree; синтетика; `unittest discover` 137/137; авторы, `[skip ci]`, без решётки перед цифрой.
