# LOOPREAL — G1: compile error; доказательств нет
Build `69ac5245-e83e-4d87-b8b6-68acd46b0e02`, source `3a1a71036fc48708094c59e3b1c70252ce4fbf9b`: Cloud FAILURE, summary COMPILE_ERROR, Kani exit 1.
Request `loopreal-g1-20261105-02`, SHA256 `8af5df8cdad82e52c3851d4caab263beb11a291ef437319feea9e2e94d9a5081`; k1-network, standard4, controls=true, jobs1, 4 мин/root.
Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`; check-tooling против `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`: PASS; build/source/request/pool identities совпали.
Причина: пять E0382 — `loop_modifies` перемещает `is_less: &mut F`; последующие обращения в двух настоящих функциях и cfg-копии недопустимы.
Точный внутренний инвариант: `size_of::<T>() == 0 || (crate::ub_checks::same_allocation(begin, sift) && crate::ub_checks::same_allocation(begin, gap_guard.dst) && begin.addr() <= sift.addr() && sift.addr() < gap_guard.dst.addr() && gap_guard.dst.addr() <= tail.addr() && gap_guard.dst.addr() - sift.addr() == size_of::<T>() && (sift.addr() - begin.addr()) % size_of::<T>() == 0)`.
Точный внешний инвариант: `size_of::<T>() == 0 || (crate::ub_checks::same_allocation(v_base, tail) && crate::ub_checks::same_allocation(v_base, v_end) && v_base.addr() < tail.addr() && tail.addr() <= v_end.addr() && (tail.addr() - v_base.addr()) % size_of::<T>() == 0)`.
False cfg-copy добавляет к внешнему инварианту `&& tail == v_base.wrapping_add(offset)`; invariant-step не запускался.

| Root под verify:: | Backing | Статус | Check / с / CBMC peak RSS |
| --- | ---: | --- | --- |
| `loopreal::insert_tail_u64_backing8` | 8 | NOT_RUN | н/д / н/д / н/д |
| `loopreal::outer_loop_u64_backing8` | 8 | NOT_RUN | н/д / н/д / н/д |
| `loopreal::insert_tail_u64_backing32` | 32 | NOT_RUN | н/д / н/д / н/д |
| `loopreal::outer_loop_u64_backing32` | 32 | NOT_RUN | н/д / н/д / н/д |
| `loopreal::insert_tail_u64_backing128` | 128 | NOT_RUN | н/д / н/д / н/д |
| `loopreal::outer_loop_u64_backing128` | 128 | NOT_RUN | н/д / н/д / н/д |
| `loopreal::outer_loop_false_invariant_backing8` | 8 | NOT_RUN | н/д / н/д / н/д |
| `realcontracts::insert_tail_safety_u64_tail1_to4_backing5` | — | NOT_RUN | н/д / н/д / н/д |
| `network::unstable_freeze_noncopy_bytes86_fallback_n2` | — | NOT_RUN | н/д / н/д / н/д |
| `realcontracts::unstable_network_safety_u8_n9_stubbed` | — | NOT_RUN | н/д / н/д / н/д |
| `assembly::safety_stable_unit_n16` | — | NOT_RUN | н/д / н/д / н/д |
| `assembly::safety_stable_unit_n32` | — | NOT_RUN | н/д / н/д / н/д |

Рост времени от backing 8→32→128 не измерен; matched PFC/consumer и отрицательный контроль не установлены; covers не оценивались.
Регрессии после изменения не запускались. Прежние K-1 времена: PFC backing5 38.1495 с, non-Copy fallback N2 8.783918 с, u8 network N9 8.316227 с.
ZST N16/N32: прежние Actions v7 `d1283ff22a`, тот же pin, данные координатора — ubuntu 4.687/35.126 с, macOS 3.657/25.670 с; сравнение с GCB ориентировочное.
Verify wall с компиляцией 43.20 с; time-v max RSS 1290476 KiB, sampled kani-compiler peak 1278800 KiB; per-root CBMC records 0, OOM scan none_seen.
Расход G1 $0.1080 / $2.00, резерв снят; проект used $100.4910, прочие reserves $0, cap $118.96. Repair reserve $1.053, own spent+reserve $1.161 ≤ $2.00.
В summary написано build success, но bounded Cloud status FAILURE; расхождение сохранено, успешная проверка не заявлена.
Произвольная длина, generic T/F, merge, остальные циклы и termination не доказаны; G1 не даёт нового proof credit.
Следующий пакет: compile-error repair только в атрибутах — передать raw pointer `is_less as *mut F`; новые GO и dispatch обязательны, G2 не разрешён.
Evidence: [проверенный отчёт](loopreal/evidence/verification-report.json), [bounded summary](loopreal/evidence/summary.md); воспроизведение `python3 -B research/challenge-8/kani-k1/loopreal/verify_g1.py`.
