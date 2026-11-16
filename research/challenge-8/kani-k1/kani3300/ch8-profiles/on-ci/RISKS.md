# Profiles ON: заранее известные риски

Source P′ `9fa2f7f97760584f38738909625c064006d8a936`; manifest62 побайтно сохранён от OFF `112fcc9ada`. Полная поимённая карта всех строк — RISKS.json. Это статическая достижимость, не новый runtime verdict.

| Риск | Строки этого manifest | Source path |
|---|---|---|
| A1-R3 PolymorphicIter unsupported | **47 `freeze_noncopy_n2`**, **59 `rejects_always_true`** (case2) | `verify/forwarding_contracts.rs:122–132,201–236` → `UnstableSmallSortFreezeTypeImpl` для Freeze !Copy → `small_sort_general` → `small_sort_general_with_scratch`, `smallsort.rs:225–294`, array-offset loop267 → `array/iter.rs:63–81` → `iter_inner::PolymorphicIter`, `iter_inner.rs:35–60,95–97`. N2 не устраняет этот offset-array loop. |
| Network N32 RSS | **нет: 0/62** | Самые большие backing arrays профильных leaves — не вызов N32 dispatcher. Actual network forwarder/negative вызывают N2 insertion; остальные roots проверяют swap/sort4/insert/merge либо relation. |

Контекст A1: `kani3300/w0-a1/polyiter/ANALYSIS.md` §4–5 описывает прежние general/stable N32 unsupported и network N32 incomplete/RSS. Это прежние source-reported observations на других roots, не outcome этих62 и не independent proof credit. Не переносить численные расходы на новые rows.

PFC исполняет конкретный target и body. Пять Replace consumers (48–52) используют `stub_verified` профильной обёртки; real-body leaves квалифицируются отдельно, consumer не заменяет их evidence. `merge_scratch48_contract_u8_n9` — fixture bidirectional_merge, не general dispatcher.

SEL1 поддерживает требуемые flags; `uninit-checks` автоматически добавляет compiler flag `ghost-state` (`kani-driver/src/call_single_file.rs:161–166`). Valid-value OFF. PFC/function-contracts, mem-predicates, float-lib, c-ffi, loop-contracts, quantifiers, stubbing, export-json сохранены. Статически конфликтующих row flags/cfg не найдено. Required cfg `kani_smallsort_controls` сохранён для9 negatives; для остальных53 cfg пуст. Runtime availability NOT_RUN. Если CI выявит недоступный flag/cfg — явный STOP соответствующих строк с причиной, остальные не удалять. Setup/group failure сохраняет NOT_RUN/UNKNOWN и оригинальный exit/exception.

Reachable unsupported не становится ожидаемым negative: oracle всех9 controls, включая `rejects_always_true`, остаётся прежним. Дополнительный failure блокирует acceptance. Не отключать uninit, checks, covers, source unwind или failing properties ради PASS. Не увеличивать caps при OOM/timeout.

15 файлов contract/export/model source chain одинаковы между stock и SEL1 (TOOL-CLASSIFIER-COMPAT.json). Это обосновывает reuse функций accept-v4, но не перенос его62 admissions: новые ON-only properties, wrappers, roles, covers, frame oracle и matching-leaf dependency требуют fresh same-row binding. Неизвестная роль остаётся UNKNOWN.

Driver export features берутся из `common_args.unstable_features` (`schema_utils.rs:95–101`); автоматический compiler flag `ghost-state` туда не добавляется. Parser требует точное множество argv features, включая `unstable-options`; лишние/duplicate/valid-value записи отвергаются.
