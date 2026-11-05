# VEIGHTMAX — этап завершён; acceptance FAIL, inventory PASS
Build `daf1045c-5454-4662-93a7-df16cfd23e00`; source `7df3f7d3d68c458185c2f42f72483c13fbe9c161` (exact-packet GO).
Library `d3982a624072437d603f0f96ba974bb00ac5eb5b`; request `veightmax-g1-20261105-02`, SHA256 `5e6e812216996d281d57aa8bb2626c27b32fed1be71329b2c7cc96261e6161fc`.
Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`; k1-merge, diagnostic, standard4, jobs1, controls=false, inventory=true, 4 min/root.
Cloud FAILURE; summary PARTIAL, gate=false, Kani exit124; final Complete отсутствует. Summary build outcome=success сохранён отдельно от Cloud FAILURE.
Source/request/pool/check-tooling PASS; tooling base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`, runtime/tooling неизменны.
Inventory: компиляция/list успешны, **233 уникальных ordinary**, три полные bound-страницы; exact-name set совпал, missing/extra=0.
Canonical sorted-name SHA256 `a73e3c308728c7e7e560665547f79775ddffef2676d4ddee1cecd1b572bdd374` совпал с expected.
Artifact-order names SHA256 `7b466e9686cdf5f56c3a8359464399b13652f6ced336b479eb01cdb1e048c738`; порядок standard/contract отличается от сортированного.
Inventory artifact SHA256 `a3d48301e9b26b84567118c84b639afec5ac1a0f7ba57fd01f220fc78adb2884` одинаков на всех страницах.
Mapping относительно `verify::`: W=`widedomains`, A=`allocationcontracts`, T=`taildiag`, I=`tailcontracts`; W→A сохраняет leaf.

| Source → ordinary leaf | Status | с | Covers |
| --- | --- | ---: | --- |
| W→A `swap_safety_u8_backing32` | NOT_RUN | — | — |
| W→A `swap_safety_u64_backing32` | NOT_RUN | — | — |
| W→A `unstable_network_safety_u8_n32_stubbed` | UNKNOWN | — | — |
| W→A `merge_safety_u64_len8_scratch48_src32_dst0` | SUCCESS | 86.45552 | 5/5 |
| W→A `sort8_safety_u64_scratch48_src32_dst0_merge_stubbed` | SUCCESS | 8.113433 | 4/4 |
| T::`u64_backing17_tail1_to7_no_explicit_frame` → I::`insert_tail_safety_u64_backing17_tail1_to7` | NOT_RUN | — | — |
| T::`u64_backing17_tail8_to15_no_explicit_frame` → I::`insert_tail_safety_u64_backing17_tail8_to15` | NOT_RUN | — | — |

Два SUCCESS: checks 0/228 и 0/269, covers **9/9**; цель **42/42 не установлена**. Unreachable checks 8/9 не являются unreachable covers.
Сумма времени завершённых новых корней **94.568953 с**; сумма всех семи неизвестна. Прежние 226 корней, включая 11 частей CITRIM, не перепроверялись.
Причина: общий runner verify budget **269 с**, старт после validate через **2851 с**; exit124 оборвал проверку. Общая граница 3120 с включает подготовку/inventory; отдельный timeout network не установлен.
UNKNOWN/NOT_RUN не получают integrated proof/time credit; prior-source результаты не заменяют эту сборку. Нет новых универсальных T/F/unwinding claims.
Расход **$0.7290/$2**, reserve0; builds1/1, retries0, repairs0. Compile-error repair неприменим; новых dispatch нет.
Bounded evidence и reconciliation: [report](veightmax/evidence/verification-report.json), [summary](veightmax/evidence/summary.md), [checker](veightmax/verify_g1.py); evidence consistency PASS ≠ acceptance.
