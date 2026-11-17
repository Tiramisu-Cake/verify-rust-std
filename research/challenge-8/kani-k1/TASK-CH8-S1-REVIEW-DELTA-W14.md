# TASK — w14: финальный delta-review composer + S1-08 r1

Это верификация корректности, не security-работа. Отвечай кратко.
Продолжение того же independent review, без /new и смены модели/effort; без субагентов.
Input g0 `7058b4f7c4d65d0dda600026c9d62738f9f95f7a`.
Owner-approved policy — `S1-ACCEPTANCE-DECISION-2026-11-17.md`.

## Exact committed deltas

1. Composer `kani3300/ch8-s1/s1-07/run-43923266772/accept-v3/`, commit
   `0a97c61cce9f6fca1acc9ab35509e314012b7bfa`, author w11.
   Его INPUTS.json фиксирует старый receipt и твои уже проверенные U/PFC components. Исходные компоненты
   `16e36c4a2c` / `013f288ca5` не менялись; не повторять их полный независимый аудит без новой причины.
2. Исправленный пакет `kani3300/ch8-s1/s1-08-r1/`, commit
   `d5dcb0fa5db210116101f440048a4f1fae7c2d20`, author w13.
   Source99e8456d200fff1299ee5756279cddb23921dc65 без изменений.
   Fixed control `/root/kani-ch8-s1-08-fix-w13` = `7c41333f9bfcfd7eb4e0ede7bd316443090c9025`,
   direct parent9208b373c0a08a265fa0d7493a6529e331065271, sibling original9ccd882ef.
   Embedded request SHA256 `77ae11136368b592f044da3f881408c87453d9bf5f28c3fd1a5eb0fcc1431c7e`.
   Old package8ea/source99e/control9ccd неизменны. ORACLE-REPAIR.json описывает exact old/new IDs.

## Scope

- Composer: exact verified input/hash/run/request/source/tool/group/row/harness/property namespaces; полное
  покрытие UNKNOWN U records, полноценные same-row PFC chains, сохранение остальных gates, 111 success roles
  остаются PENDING; никаких S1-08 labels задним числом. Правильные companion/union зависимости, отсутствие
  retroactive historical edits и independent proof credit. Вычисление verdicts должно следовать gate logic,
  не ожидаемому агрегату. Проверить meaningful mutation cases ниже hash gates; повторный replay.
- Repair: проверить закрытие твоего W14-S108-01 по pinned source/producer и negative_oracle.matches,
  два new spans95:32–95:48 /101:21–101:37, прежние logical expressions/status/sole-failure/type/helper/oracle
  semantics. Другие шесть oracles и source unchanged; новые identities/patches/payload/request/full manifest
  согласованы. Новая regression должна самостоятельно проверять source coordinates всех восьми declared
  oracles и отвергать старые/неверные/согласованно подменённые spans, а не повторять ошибочный generator.
  Посмотреть полный diff old9ccd→fixed7c413, что кроме coordinate repair/regressions/пинов не внесены
  посторонние semantic изменения. Сохранены runner/decoder/snapshots/caps/depth5/source/tool/domain/controls.
- Проверить old candidate immutability и self-contained readiness нового пакета. Source/assertion equivalence
  уже проверена тобой; без причины не повторять broad suites. Допустимы small synthetic/Git/demangler tests,
  не cargo/rustc/Kani/CBMC/rustfmt/full runner и не новые Builds.

Output только `kani3300/ch8-s1/review-after-07/delta-r1/`: REVIEW.json/md, VALIDATION.json, HANDOFF.md,
необходимый минимальный reproducer. Исходный review/finding сохранить; в delta явно CLOSED/OPEN для W14-S108-01.
Отдельные verdicts composer и repaired package APPROVE/CHANGES_REQUIRED с exact reviewed identities и assurance.
Не исправлять author code. При concrete finding — severity/path/line/evidence/minimal fix координатору для
возврата original owner. Review не является dispatch GO: после APPROVE координатор соберёт пакет к GO адресату.

Времени и объёма достаточно; STOP только реальный blocker/реально достигнутый установленный лимит, не оценка
«не успеваю», объём/контекст или исправимая ошибка. Продолжай до bounded review результата.
Без CI/push/публикаций/ledger; не stage чужие пути, без git add -A/reset/rebase. Commits `[skip ci]`,
author Tiramisu-Cake <igkharin@gmail.com>. Финал `READY <g0>` с verdicts либо реальный STOP.
