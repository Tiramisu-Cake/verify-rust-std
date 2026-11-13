# KANI3300 GATE-P — full regression and SmallSort replay preparation (DRAFT / NOT ISSUED)

2026-11-13. Worker 15, отдельная сессия; подготовка параллельно M3, финальные bindings после C1 freeze.
Это верификация корректности, не security-работа. Сейчас не выдано; CI/Cloud/публикаций не запускать.
Local cargo/rustc/Kani/CBMC/Miri/builds запрещены. Подготовка Cloud $0; dispatch/slots/лимиты — только координатор.

## Exact inputs и непересекающиеся writes

Tool source lineage: `94c00a8859bc9e4f0f1b7db73a95dbee88f6213a` → E1+X1=C0 → accepted M3=C1.
Подготовить templates сейчас, но итоговый CI request содержит exact C1 export SHA/tree, clean diff и tool/runtime/test hashes.
CI-only overlay отдельным commit поверх C1, только собственный bounded workflow/scripts; удаление штатных workflows
если требуется принятой fork-only практикой — только в overlay. Export source tree не включает workflow/research receipts.
Не менять tests/compiler/runtime W14, не править штатный regression script для сокращения списка/игнорирования failures.

## Gate A — штатный полный Kani regression

Запуск в изолированном fork CI checkout exact export: **`scripts/kani-regression.sh`**, целиком, не Quick.
Сохранять pinned toolchain/dependencies/CBMC и solver checks; не импортировать CBMC-ZST patch или unrelated tool upgrade.
`KANI_REGRESSION_KEEP_GOING` должен быть unset/empty: непустое значение отключает errexit в этом script.
Сохранить настоящий exit status (не exit tee), полный bounded итог каждого этапа, timeout/signal и artifacts even on failure.
Не ставить глобальные `--object-bits 12`, `--no-slice-formula`, отключение checks или Quick timeout300 на весь script;
12 bits остаются у принятых heavy fixtures. Штатный per-test timeout по умолчанию2400; job/concurrency/dependency plan
предложить координатору по upstream recipe, без выдуманного измеренного времени/нового run authorization.

Receipt должен покрывать fmt/build-dev, все unit packages, все15 compiletest suites:
kani, expected, ui, std-checks, firecracker, prusti, smack, cargo-kani, cargo-ui, script-based-pre,
coverage, cargo-coverage, kani-docs, kani-fixme, json-handler;
затем firecracker codegen, cargo smoke/clean и заключительный warnings-denied build.
Не считать общий script0 доказательством всех этапов при keep-going/обрезанном выводе; counts/presence/exit обязательны.
Dependency/network/runner failure = infrastructure/NOT_RUN для незавершённых этапов; expected negative отдельно от unexpected FAIL.
Linux full gate не заявлять macOS/full-platform evidence. Любое исключение полного списка требует отдельного решения,
а не незаметного rename, filter или нового ignore. Оставить чистый export после smoke/cleanup в isolated workspace.

## Gate B — SmallSort replay, профиль12 и uninit ON

Source inventory стартует с read-only `/root/verify-rust-std-kani-traitpfc`:
HEAD `70ba5befc617627073738e26cb1466bd4fb76e41`, library tree
`6ea9d3425f6d0478cfc2517cbdd2fb7d7b32a53f` (= `1aac64c50d69382c8ce90811880225d0a047525f:library`).
Это явно выбранный snapshot, не установленный current PR#752 head; финальный library pin подтверждает координатор.
Сначала составить ROOT/EFFECT-MAP: actual full selector, cfg/control flags, unwind, proof_for_contract mode,
stub_verified edges, requires/ensures/callback, scratch type/extent/offset и настоящий shadow-transfer path.
Исторический TRAITPFC-G3 Build2 `2f1c45e519cc89e1dae532ad0f44243255a514d7` был с uninit OFF/valid-value OFF
на другом Kani: это inventory/compatibility reference, не Part1 replay evidence.

Минимальные representatives для рассмотрения, exact names проверить по frozen source:
- `slice::sort::shared::smallsort::verify::helper_contracts::sort4_safety_u64` — actual sort4 PFC,
  initialized src и `MU<[u64;4]>` output; Select/network real helper.
- `...::verify::merge::merge_scratch48_contract_u8_n9` — actual merge-profile PFC, scratch48,
  обе backing alternatives flat/general сохраняются, prefix initialized, tail uninitialized.
- `...::verify::helper_contracts_wide::merge_safety_u64_len8_scratch48_src32_dst0` — flat scratch48,
  nonzero source offset32, initially uninitialized output, actual merge body.
`sort8_safety_u64_scratch48_src32_dst0_merge_stubbed` — boundary/inventory, не substitute real merge proof:
stub may lack destination-initialization postcondition, Replace shadow transfer не заявлен.

Replay manifest: tool C1 binary/model identities, pinned std snapshot/overlay, nightly/deps, `-Z uninit-checks`,
object-bits12, exact unwind/argv, normal solver/slicing/checks. Ordinary comparison profile сохраняет organizer
`--no-assert-contracts`; PFC requires отдельную фиксацию selected Check body/проверяемого контракта.
Добавить uninit-OFF compatibility companion на тех же inputs, но не выдавать его за positive ON result.
Все прочие coverage/validity flags явно записать; не добавлять assumptions про initializedness или менять production helpers.

Matched negative обязателен: valid MU allocation, один отсутствующий live-source byte/value, intended retained read
в actual raw-pointer helper (sort4 — возможный маленький кандидат); legal companion с теми же geometry/call path.
Не делать initialized `&[T]`/assume_init от hole до входа в helper. Merge принимает initialized slice, поэтому такой
hole-repro может быть UB уже при построении аргумента; отдельно подтвердить location, не приписывать его merge.
Tail read после корректного helper — полезный scratch-state sensitivity control, но не внутри-helper negative.
Нужный test-only companion/overlay держать отдельно от library production; если отрицательный target недостижим
без раннего guard/invalid ref — записать GAP и предложить конкретный raw-helper control, не засчитывать чужой FAIL.

Оракул каждого root: useful checks/ensures действительно достигнуты; legal ON SUCCESS без Unsupported/frame error;
negative падает на intended read, не на unrelated requires, cycle/closure layout или runner limit.
Object-limit failure/timeout/OOM = незакрытый replay, не повод менять N/backing/offset/contract/geometry.
Существующие SmallSort phases/budgets/lanes сохраняются: fork tool gate не разрешает новый Cloud Build автоматически.
Использовать разрешённый coordinator lane; обычное CI evidence читать через принятый reporting interface,
без raw archives/logging downloads. Этот TASK готовит запрос, не dispatch.

## Handoff и final acceptance

`kani3300/final-gate/`: INPUTS, EXPORT-MANIFEST, FULL-GATE-REQUEST, REPLAY-ROOT-MAP,
REPLAY-CONTROL-MAP, CI-ONLY-OVERLAY-MAP, REVIEW, RESULT-template (всё новое NOT_RUN).
Каждый запрос с caps/phase/owner и перечнем expected outputs; ресурсы/runs утверждает координатор, новых Build budget нет.
Сверить C1 source tree, eight strong oracles + mode expectations + M3 mixed-order result, полный Gate A и Gate B
отдельно. No binding to "latest" и no source edits после gate. Reproducer/expected Unsupported не formal proof credit.
После выдачи завершить `READY <research/package sha>`; не push/issue/PR/run без координатора. Сейчас **DRAFT / NOT ISSUED**.
