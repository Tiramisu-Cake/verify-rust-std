# Дополнение координатора к C3b — новое жёсткое ограничение (важнее гипотез H1/H2)

П-6, job autoharness на **macOS** (run 40748125754, 18:50–22:09 UTC) закончилась: «Manual Harness Summary: Complete - 2068 successfully verified harnesses, 3 failures, 2071 total». Все три отказа — наши, каждый «VERIFICATION:- FAILED / CBMC timed out» ровно через ~10 мин:
- `merge::merge_contract_u64_n16`
- `network::insertion_permutation_u64_n12`
- `network::insert_tail_contract_u64_start1`

То есть в режиме `kani autoharness` (run-kani.sh `--run autoharness`) **каждая гармоника, включая ручные, имеет тайм-аут ~10 мин** (комментарий в `kani.yml` организаторов: Unicode-функции «exceed the 10m timeout on macOS»). Найди точное значение и откуда оно (исходник `kani-driver` autoharness на pin `9461e07a`, флаги). macOS-раннер: 3 CPU / 7 ГБ, 3 потока. Ubuntu autoharness умер раньше по другой причине (shutdown раннера), вопрос памяти остаётся.

Следствие: **каждая ordinary-гармоника должна надёжно укладываться в этот тайм-аут на macOS при 3 параллельных потоках**, с запасом на разброс раннеров (в финальном CI одна и та же гармоника на одинаковом macOS-образе отличалась в 1,7 раза). Финальный CI (macOS, партиции с default `-j`; старые имена → `mem-inputs/RENAME-MAP.tsv`) — гармоники ≥ 300 с (только slowest-15 каждой партиции, полного списка нет):
- m2 1266 s slice::sort::shared::smallsort::kani_k1::network::w2p2_k10_perm_u64_n12
- m2 924 s slice::sort::shared::smallsort::kani_k1::network::w2p2_k10_u64_n14
- m2 720 s slice::sort::shared::smallsort::kani_k1::merge::w2p2_gs_u8_len13
- m2 683 s slice::sort::shared::smallsort::kani_k1::network::w2p2_k10_u8_n17
- u2 569 s slice::sort::shared::smallsort::kani_k1::network::w2p2_k10_u64_n14
- m2 567 s slice::sort::shared::smallsort::kani_k1::network::w2_k16_a17_mid
- m2 522 s slice::sort::shared::smallsort::kani_k1::network::w2_k16_a16_mid
- m4 511 s slice::sort::shared::smallsort::kani_k1::merge::w2p2_bm_u64_len16
- u2 482 s slice::sort::shared::smallsort::kani_k1::network::w2p2_k10_perm_u64_n12
- m2 445 s slice::sort::shared::smallsort::kani_k1::merge::w2p2_gs_u8_len12
- u2 400 s slice::sort::shared::smallsort::kani_k1::network::w2p2_k10_u8_n17
- m4 398 s slice::sort::shared::smallsort::kani_k1::merge::w2p2_bm_u64_len15
- m2 388 s slice::sort::shared::smallsort::kani_k1::merge::w2p2_gs_u64_len12
- m2 386 s slice::sort::shared::smallsort::kani_k1::correct::l2_fallback_u64_n16
- u4 382 s slice::sort::shared::smallsort::kani_k1::merge::w2p2_bm_u64_len16
- m4 365 s slice::sort::shared::smallsort::kani_k1::network::w2night_k8r_start2_u64
- m2 363 s slice::sort::shared::smallsort::kani_k1::network::w2_k16_a17_n32
- m2 358 s slice::sort::shared::smallsort::kani_k1::merge::w2p2_gs_u64_len11
- m2 339 s slice::sort::shared::smallsort::kani_k1::merge::w2_a_all_len32_safety
- m4 334 s slice::sort::shared::smallsort::kani_k1::network::w2night_k8r_start1_u64
- u4 323 s slice::sort::shared::smallsort::kani_k1::network::w2night_k8r_start1_u64
- m4 319 s slice::sort::shared::smallsort::kani_k1::merge::w2p2_bm_u64_len14
- m4 316 s slice::sort::shared::smallsort::kani_k1::network::w2night_k8r_start3_u64
- m2 316 s slice::sort::shared::smallsort::kani_k1::network::w2p2_k10_u64_n8
- m2 316 s slice::sort::shared::smallsort::kani_k1::network::w2_k16_a17_n31
- m2 309 s slice::sort::shared::smallsort::kani_k1::network::w2p2_k10_u64_n13
- u2 308 s slice::sort::shared::smallsort::kani_k1::merge::w2p2_gs_u64_len12
- u2 298 s slice::sort::shared::smallsort::kani_k1::network::w2p2_k10_u64_n13
- m4 295 s slice::sort::shared::smallsort::kani_k1::network::w2night_k8r_start4_u64
- u4 277 s slice::sort::shared::smallsort::kani_k1::network::w2night_k8r_start2_u64
- m4 276 s slice::sort::shared::smallsort::kani_k1::merge::w2p2_bm_u8_len16
- u2 265 s slice::sort::shared::smallsort::kani_k1::merge::w2p2_gs_u64_len16
- u2 257 s slice::sort::shared::smallsort::kani_k1::network::w2p2_k10_u64_n8

Задача C3b расширяется (приоритет 1): найти **все** ordinary-гармоники, которые рискуют превысить тайм-аут autoharness на macOS (не только slowest-15 — используй `kani list`/измерения, групповые замеры в GCB e2-standard-4 jobs=1 и калибровку GCB↔Actions по общим гармоникам из финального CI), и для каждой реализовать лечение без потери домена, где возможно: разбиение диапазонов длин/позиций на отдельные гармоники, `#[kani::solver(cadical|kissat)]`, более узкий `unwind` там, где домен меньше, вынос общих частей. Где без потери домена нельзя — вариант «в opt-in с раскрытием» с точным списком теряемого (решает владелец). Предложи целевой бюджет на гармонику (с обоснованием: macOS ≈ k × GCB, 3 потока) и докажи замерами, что после лечения все ordinary в него укладываются. Бюджет сборок C3b увеличиваю до **$12 и 20 сборок**.
