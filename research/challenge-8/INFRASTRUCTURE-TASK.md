# Отдельное задание: стоимость и надёжность Cloud proof lanes

Статус: **поставлено, не реализовано**. Документационная задача не даёт бюджета,
не изменяет executable infrastructure/workflows/coordinator/pins/proofs и не
открывает фазу. Перед реализацией владелец назначает owner, worktree/branch,
scope, Cloud account/window/lanes и review gates. Сохранить существующий v2/max2;
изменение числа slots — отдельная согласованная миграция.

Цель: уменьшить измеренную стоимость содержательной итерации select и merge,
раньше находить известные setup/collector отказы, сохранив точные inputs и proof
результаты. Нельзя получать ускорение отключением checks или принятием diagnostics.

## Что уже есть: сначала проверить повторное использование

Main содержит общие docs; приведённые helpers находятся в рабочих ветках.
Не копировать их исполняемые файлы в рамках этой правки. Исходные ревизии:

| Механизм | Существующая точка и ограничение |
| --- | --- |
| Select preparation | [PREPARATION-REVIEW](https://github.com/Tiramisu-Cake/verify-rust-std/blob/4b0afb13609fac45884afb3bbd092980061d8d53/research/challenge-8/cloud-build/sort4-c1-caller-bridge/PREPARATION-REVIEW.md); exact source/MIR/refinement и caller inputs. Старый [preflight-sources.py](https://github.com/Tiramisu-Cake/verify-rust-std/blob/4b0afb13609fac45884afb3bbd092980061d8d53/research/challenge-8/overnight/preflight-sources.py) имеет GitHub-hosted guard и запускает preparers; не считать локальным service test или Cloud-compatible автоматически |
| Merge preflight | [preflight-source.py](https://github.com/Tiramisu-Cake/verify-rust-std/blob/2bf268f792a5a8705292d4b7b8935eba82ca9847/research/challenge-8/merge/overnight/or-join-liveness/preflight-source.py): manifest/fixture/harness/source hashes, сигнатура/guard/panic, `accepted:false`; это не proof admission |
| Selection и inputs | [selection.py](https://github.com/Tiramisu-Cake/verify-rust-std/blob/2bf268f792a5a8705292d4b7b8935eba82ca9847/research/challenge-8/merge/cloud-build/selection.py), recipes, source-input.py — exact selected paths/Git object closure, Cloud restore certificate |
| Учёт и время | control.py: API create/start/finish, reservation и conservative charge; run-proof.sh/run-merge.sh и existing stage resource files. Начать с этих данных, не вводить конкурирующий ledger |
| Packaging | package-evidence.py, manifest/inventory/config/input/archive hashes, ≤8MiB text index, upload receipt и независимый final verdict; обычный результат сообщается через Evidence Brief |
| Исторический cache | [console-cache.py](https://github.com/Tiramisu-Cake/verify-rust-std/blob/2bf268f792a5a8705292d4b7b8935eba82ca9847/research/challenge-8/merge/overnight/console-cache.py): exact input set/manifest/console hash и regular non-symlink files, но guard требует GitHub-hosted Linux, GITHUB_SHA и старую merge branch. Cloud support не доказан |

Проверить actual выбранные select/merge recipes следующего задания: прежние o26
и merge smoke не заменяют стоимость текущего actual-caller цикла. Source extraction
и preparers с compiler/proof subprocess остаются Cloud-only. Малые parser/classifier
service tests на synthetic data допускаются локально после проверки imports/entrypoint.
Full raw-evidence replay требует separately authorized administrative audit по
[Evidence Brief policy](EVIDENCE-BRIEF.md).

## Последовательность и критерии приёмки

| Шаг | Работа | Приёмка |
| --- | --- | --- |
| 1. Baseline расходов | Для актуальных select и merge lanes связать Build ID, exact SHAs/profile/cases с queue, restore/preparation, dependencies/verifier build, extraction/refinement/proof, packaging/upload и evidence processing. Использовать сохранённые данные; недостающее измерить только в разрешённых Cloud runs | По каждой lane таблица времени/charge и первичного blocker; «нет данных» явно, preparation и evidence не приписаны proof. Нет обещания ускорения до измерения |
| 2. Early rejection | Выделить быстрые проверки missing paths/closure, bad source/patch contexts/hashes/pins/profile schema и collector inventory/expected-case/stage/location. Проверить collector на saved positive, intended-negative, setup-failure и NOT_RUN до cold build | Каждый известный отказ ловится до дорогой сборки/verification, с исходным causal error и nonzero status. Неполный collector не превращается в accepted proof; negative до target остаётся setup/INCONCLUSIVE. Позитивный контроль проходит и доходит до прежних обязательств |
| 3. Подготовленное окружение | Отделить pinned dependencies/toolchain от изменяемых proof inputs; проверить reuse через digest-pinned Cloud-compatible image/artifact. Сохранить recipe/no-source и полный restore certificate | Cold и повторный Build обеих lanes на одинаковых semantic inputs/cases; stage timings показывают фактический reuse. Точное происхождение deps/target/compiler проверяется; untrusted/missing environment ведёт к безопасному cold path, без изменения proof scope |
| 4. Verifier cache | Проверить существующий cache helper для Cloud; адаптацию/замену спроектировать отдельно, не просто удалить hosted guard. Полный ключ и immutable manifest связывают verifier source/tree, ordered patches и применённые bytes, parser/translator/kernel/spec/prelude/refiner/exporter, compiler/toolchain/build flags/scripts/helper schema, dependencies/solver и image/OS/arch/ABI | Same-input warm hit и cold baseline обеих lanes дают те же case/stage/target normal/unwind/negative/refinement/leak/nonvacuity/UB results. Artifact digest/provenance/inventory проверены перед использованием; cached binary не является cached proof |
| 5. Cache refusal | Изменить по одному ключевому входу: source, patch/order, build config, dependency/toolchain, target/platform; отдельно missing/truncated/corrupt manifest/binary, wrong digest, stale schema и symlink | Все несовместимые/повреждённые caches отвергнуты без выполнения binary, причина записана; cold fallback или fail closed по reviewed policy. После cold fallback proof obligations/results сохранены; silent cache match невозможен |
| 6. Classifier-only replay | Только в separately authorized administrative audit: неизменные archives/logs и synthetic controls; raw hashes, old/new auditor и verdict/reason. Обычный service test использует только synthetic data | Ни compiler/exporter/refiner/verifier, ни source extraction не запускаются; original evidence/verdict не меняются, replay имеет отдельный result. Missing/NOT_RUN остаются таковыми; неправильные stage/location и обрезанные данные fail closed. Нет переноса PASS на иной profile |

Для cold/warm сравнения фиксировать одинаковые proof cases, semantic pins,
timeouts/checks, machine/target; различия в image/cache инфраструктуре описать.
Сравнивать не только badge, но target reached/posts и intended rejection sites.
Сохранить source-produced evidence и hashes; raw logs доступны только по separately
authorized administrative audit. Ожидаемые отказы
и misses тоже учитываются в бюджете. При semantic изменении cache/окружение не
заменяет новый proof run и затронутые regression gates.

Итоговый deliverable — reviewable infra PR отдельно от proof истории, измеренная
таблица cold/warm для обеих lanes, incompatibility/corruption checks, evidence
identities и подтверждение сохранённых proof результатов. Ускорение оценивать
по setup wall/Cloud seconds и содержательным итерациям в 120 минут; не менять
конечные claims, чтобы получить красивую цифру.

## Отдельная малая задача: Flux/RAPx filters

Согласовать path/input filters automatic Flux/RAPx только для нерелевантных
изменений. Проверить matched/unmatched source/config/tool-pin/docs paths,
сохранить запуск при изменении входов и требуемые checks; не выключать CI целиком.
Research Actions остаются manual и не получают разрешение на dispatch.
Эта задача имеет собственный diff/review, не включается молча в cache работу.
