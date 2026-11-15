# Rebinding — Q завершён, A/B ждут freeze

Q уже привязан к14bc57fdb9; текущие identities и READY overlay в HANDOFF.md.
Ниже сохранена последовательность подготовки; заново Q не запускать и source не менять.
Проверка текущего пакета: python3 quick/validate_bound.py из соответствующего каталога.
A/B всё ещё требуют новой привязки после принятого Q/freeze.

## Исходная последовательность (Q выполнен статически)

Ни один PENDING token в оставшихся A/B шаблонах не является source identity. Не cherry-pick/rebase prep stack поверх порта:
пересоздать один CI-only overlay из full-export на exact принятом source, убрать stock workflows только в нём,
проверить diff allowlist и parent. Чужие refs/source не двигать. Worker15 не push/dispatch.

## Q — после принятия P, до freeze

- Записать candidate SHA/tree/parent (parent exact8e299aa624), source clean; independent delta review отдельно.
- Пересоздать native selector inventory из actual candidate; сохранить471+29, goldens/directives/ignore states,
  проверить controls против corrected39a и причины17 negatives. Заполнить все file blob/SHA256/mode в test-manifest.
- inputs.json: source_sha/tree/parent, test_manifest_sha256, recipe_commit/path/hash, current qualification identity.
  Не переносить runtime status старого run. Сохранить native unit names и S5/F7 требования; additions review явно.
- sensitivity.py SOURCE_SHA; sensitivity-manifest source_candidate/base/input hashes; patch hashes сверить без изменения bytes;
  inputs.sensitivity.manifest_sha256. Structural manifest/source/18 comparisons/11 invocations сохранить,
  inputs.structural.manifest_sha256 сверить. Observer читает source-owned validate_json_export/schema из export.
- Workflow exact export ref, local CI parent; обновить CI-REQUEST/CI-OVERLAY/receipt source fields и inventory/patch hashes.
  Снять false guard только в проверенной финальной CI-копии. Обеспечить fork manual dispatch availability отдельно.
- Synthetic checks + service error paths на final bound recipe, без local compiler. Coordinator один Quick → acceptance.

## A/B — после Quick и точной freeze

- Записать freeze source SHA/tree и Quick acceptance; source/tests/docs drift запрещён, A/B на той же голове.
- A binding.json: export_sha/tree/state SEL1_C2_FROZEN, все file SHA256, subtrees, submodule pins,
  symlink targets,33 stages/lines/commands от собственного неизменённого regression script.
  receipt.py FROZEN_SHA/FROZEN_TREE; workflow export ref; own setup/dependency/toolchain pins без upgrades.
  Source change in regression/setup/stage definitions за рамками порта → STOP/review.
- B sel1-c2-source-binding.json: заново обнаружить полное нужное coverage (570/7 — лишь skeleton),
  exact export SHA/tree/state SEL1_C2_FROZEN, каждый file/subtree hash, включая все новые tests/docs/5 production files.
  Проверить added/deleted source paths и symlink raw bytes. Не оставлять C2/S1 hashes или receipt assurance.
- B request: tool_export_sha/tree, source status, dependency/runtime build identity pending до actual build;
  std70ba/test6075/5 patched hashes/test patch unchanged. Шесть exact selectors, geometry/covers/unwind и caps не менять.
- replay.py: SEL1_C2_SHA/TREE, REQUEST_SHA после сериализации request; PATCH_SHA/PATCHED_FILE_HASHES сверить.
  Не превращать raw-negative exit1 в automatic PASS. Source binding pending guard должен разрешать только final state.
- Для A/B заново CI-OVERLAY, source-binding/request checksum links, full-export hashes, overlay patch SHA,
  local CI SHA/tree/parent; внешний TEMPLATE-INVENTORY/PACKAGE и request-copy hashes обновить последними.
  Manifest не включает собственный hash; внешний inventory фиксирует его bytes. Generated properties/runtime/binaries
  до запуска неизвестны; не заполнять старым receipt.
- Bound runner synthetic checks, whole final CI diff review; worker14 review A, coordinator только publish/dispatch.
  A три exact receipts/aggregate → acceptance; затем B шесть complete receipts/check inventory → curated RESULT.
