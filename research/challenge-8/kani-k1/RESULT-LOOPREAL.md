# LOOPREAL — контроль работает; масштабирование и regression gate не пройдены
G1 `69ac5245-e83e-4d87-b8b6-68acd46b0e02`, source `3a1a71036fc48708094c59e3b1c70252ce4fbf9b`: COMPILE_ERROR E0382, 12 NOT_RUN; repair убрал перемещение &mut F в трёх loop_modifies.
Repair `8400bb9d-f0f3-43fe-b47e-df5b4a4aae67`, source `dc0d792f74c437966aff93c734d43fcedc4dc7a7`: Cloud FAILURE, summary COMPLETE, gate=false, Kani exit 1.
Request `loopreal-g1-repair1-20261105-01`, SHA256 `92b07d04e7bf08dcfaba93c0b92601236e3ce9cf987b00b34e181797ffe0ff22`; k1-network, standard4, controls=true, jobs1, 4 мин/root.
Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`; tooling base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`; build/source/request/pool и check-tooling PASS.
Точный внутренний инвариант: `size_of::<T>() == 0 || (crate::ub_checks::same_allocation(begin, sift) && crate::ub_checks::same_allocation(begin, gap_guard.dst) && begin.addr() <= sift.addr() && sift.addr() < gap_guard.dst.addr() && gap_guard.dst.addr() <= tail.addr() && gap_guard.dst.addr() - sift.addr() == size_of::<T>() && (sift.addr() - begin.addr()) % size_of::<T>() == 0)`.
Точный внешний инвариант: `size_of::<T>() == 0 || (crate::ub_checks::same_allocation(v_base, tail) && crate::ub_checks::same_allocation(v_base, v_end) && v_base.addr() < tail.addr() && tail.addr() <= v_end.addr() && (tail.addr() - v_base.addr()) % size_of::<T>() == 0)`.

| Root под verify:: | Status | Failed/total check | с | CBMC peak RSS, KiB |
| --- | --- | --- | ---: | ---: |
| `loopreal::insert_tail_u64_backing8` | TIMEOUT | — | — | 4045108 |
| `loopreal::outer_loop_u64_backing8` | SUCCESS | 0/609 | 151.6557 | 6390444 |
| `loopreal::insert_tail_u64_backing32` | TIMEOUT | — | — | 99304 |
| `loopreal::outer_loop_u64_backing32` | TIMEOUT | — | — | 11258384 |
| `loopreal::insert_tail_u64_backing128` | TIMEOUT | — | — | 4205332 |
| `loopreal::outer_loop_u64_backing128` | OUT_OF_MEMORY | — | — | 15503184 |
| `loopreal::outer_loop_false_invariant_backing8` | FAILED (expected) | 1/636 | 88.192055 | 5999420 |
| `realcontracts::insert_tail_safety_u64_tail1_to4_backing5` | TIMEOUT | — | — | 646640 |
| `network::unstable_freeze_noncopy_bytes86_fallback_n2` | TIMEOUT | — | — | 136264 |
| `realcontracts::unstable_network_safety_u8_n9_stubbed` | SUCCESS | 0/775 | 13.157118 | 315908 |
| `assembly::safety_stable_unit_n16` | SUCCESS | 0/514 | 6.4619365 | 209476 |
| `assembly::safety_stable_unit_n32` | SUCCESS | 0/514 | 92.49891 | 13089768 |

TIMEOUT/OOM: verification time отсутствует, не равен 240 с; указан бюджет 4 мин/root. Все 12 CBMC peak имеют direct metadata attribution; OOM подтверждён Kani и bounded kernel scan.
Отрицательный контроль: ровно `Check invariant after step for loop ...::insertion_sort_shift_left_false::<u64,...>.0`, `verify/loopreal.rs:115`; полный текст в отчёте. Успешные invariant base/step поштучно не перечислены terse-выводом.
Все PFC backing 8/32/128 — TIMEOUT; outer 8 SUCCESS только условно со stub_verified: без успешного matched PFC композиционный credit не засчитан. Outer 32 — TIMEOUT, 128 — OOM.
Почти постоянная стоимость от длины не установлена: нет завершившихся PFC для сравнения 8→32→128; успешное outer 8 не доказывает произвольную длину.
Ordinary до→после (K-1): insert_tail backing5 38.1495 с→TIMEOUT; non-Copy fallback N2 8.783918 с→TIMEOUT; u8 network N9 8.316227→13.157118 с. Причинность и аппаратный шум не изолированы.
ZST N16/N32 SUCCESS: 6.4619365/92.49891 с. Прежние Actions v7 `d1283ff22a`, тот же pin, данные координатора: ubuntu 4.687/35.126, macOS 3.657/25.670 с; сравнение с GCB ориентировочное.
Covers завершённых SUCCESS-строк 7/7; полное ожидание 34 covers не установлено. Unreachable прочих checks не считаются недостижимыми covers; неуспешные строки не получили zero-cover credit.
Verify wall с компиляцией 40:18.76; time-v max RSS 15601676 KiB; sampled CBMC peak 15503184 KiB (~14.78 GiB), machine 15.63 GiB, swap off.
Расход G1 $0.1080 + repair $0.6480 = $0.7560 / $2.00, own reserve $0; проект used $101.5710, прочие reserves $0.9450, cap $118.96.
В обоих summary run text говорит build success, но bounded Cloud status FAILURE; расхождение сохранено и не означает успешную приёмку.
Произвольная длина, generic T/F, merge, остальные циклы и termination не доказаны; нужны успешные PFC и закрытие ordinary-регрессий. Пакет к ordinary-интеграции не принят.
Интеграция: smallsort.rs:695 имеет 108 символов; по замечанию координатора перенести аргументы loop_modifies на отдельные строки при интеграции.
Выполнены G1 и один разрешённый repair; G2 не запускалась и требует нового GO. Новых изменений исходника после approved repair не внесено.
Evidence: [repair report](loopreal/evidence/repair1/verification-report.json), [bounded summary](loopreal/evidence/repair1/summary.md), [исходный G1](loopreal/evidence/verification-report.json). Проверка: `python3 -B research/challenge-8/kani-k1/loopreal/verify_repair1.py`; это сверка bounded responses, не независимый verifier run.
