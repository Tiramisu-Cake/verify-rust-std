# MERGE-STOCK-26.10 — результат миграции

2026-10-08 Moscow. Фаза завершена; wrapping-поднаправление STOP на отсутствии
точных методов в stock26.10. G2/A/B и девять условных Rust-проекций повторно
приняты при прежних областях применимости. Actual merge и Challenge не доказаны.

Proof SHA **1be9c1311faf12613145e28f95a2471dec2433fe**,
[run37694164542](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37694164542).
Workflow_dispatch на sync/upstream-cd371-merge исполнил только ожидаемый
merge_geometry job113041515221; семь остальных jobs skipped. Полный артефакт
проверен; [компактная доказательная запись](stock-26.10/M1-EVIDENCE.json)
сохраняет фактические stages, тела, счётчики, предикаты и source/log/MIR hashes.
Это metadata, не копия скачанных логов или generated/injected Rust source.
Последующий documentation HEAD не является proof SHA.

## Прежние и новые результаты

Все PASS ниже условны ровно на прежних premises/full posts. Для математики
refinement к Rust не заявлен; для Rust refinement относится к изолированной
проекции и её ghost-free оригиналу. Исходные файлы, результаты и SHA сохранены.

| Компонент | Stock26.09 — прежний proof SHA / run | Stock26.10 — M1 | Область применимости / результат |
| --- | --- | --- | --- |
| G2 | b1ed0c22 / [37672184476](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37672184476) PASS | PASS | n>=2, произвольные нормальные Boolean choices: геометрия полного scalar trace |
| A | fc4d03d3 / [37677079473](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37677079473) PASS | PASS | G2+final scalar guard: точная occurrence permutation, write trace/coverage/multiplicity |
| B | 4e546ec1 / [37681190236](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37681190236) PASS | PASS | Fixed finite SWO, immutable keys, sorted halves, faithful normal answers, scalar odd choice: sorted stable permutation и guard |
| g2_steps | P3 PASS | PASS | Проверены локальные Rust step/terminal lemma bodies; whole Rust trace OPEN |
| init_const | P3 PASS | PASS | Exact const add(i), positive stride/byte bounds/stock provenance limits |
| init_mut | P3 PASS | PASS | Exact mut add(i), те же явно указанные premises |
| forward_left | P3 PASS | PASS | Exact add(is_l as usize), заданные i<n/byte/provenance limits |
| forward_right | P3 PASS | PASS | Exact add(!is_l as usize), те же premises |
| destination_up | P3 PASS | PASS | Exact add(1), i<n/byte/provenance limits |
| destination_down | P3 PASS | PASS | Exact sub(1), дополнительно i>=1 |
| pointer_order | P3 PASS | PASS | Checked stride_order; left<left_end iff i<j при positive stride и полных base/index associations |
| pointer_guard | P3 PASS | PASS | Checked stride_equal; exact OR guard iff scalar guard при associations всех четырёх указателей |

P3 для каждой из девяти строк: полный прежний proof SHA
1c318453efa4e3a774b2edd791a5298d76132eb0,
[run37686627140](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37686627140).
Все новые строки проверены на едином M1proofSHA/run выше. Предусловия и полные
постусловия не менялись; скопированные C bodies и все13Rust case bodies
побайтно равны историческим. Новых аксиом/лемм без тел/spec/tool patches нет.

G2:8/8тел,88statements,17return/17leak. A:19/19тел,178statements,
55return/55leak. B:65/65тел,505statements,197return/197leak, включая
проверенные в той же версии G2/A/SWO callees. Полный verifier exit0,
0errors, dead-code gate сохранён, source/log hashes совпали.

Rust:9positive isolated units,12own bodies,102execution records,
25return/25leak. Во всех exporter/decode/fullVF/refinement0; source integrity
сохранена на каждом этапе, все тела исполнены, нет errors/deadcode.
Для pointer functions сохраняются `on_unwind_ens false`; g2 ghost lemmas
математические. Это доказанный no-unwind scope проекций без callbacks/copies,
не normal/unwind post всего merge. Нет ignore_unwind_paths/allow_assume.

## Отрицательные контроли

G2 все3контроля приняты на marked assertion136: read at n18–19,
wrong double advance37–39, scalar read at -1 14–16. Последний — только
математическая граница, не Rust memory-access control. A duplicate/lost ID
без guard отвергнут на218:68–70. B повторяет A и отвергает wrong ties274:39–41
и wrong answers274:31–33. Все7математических negative instances достигают
точного predicate/location/own body,49fail-closed controls проходят.

Rust wrong_cursor отвергнут на verified/lib.rs20:23–25:
`ptr_add_(ptr_add_(base, i, T_typeid), 1, T_typeid) = ptr_add_(base, (i + 2), T_typeid)`.
address_index —14:18–20, `i = j`. Оба TARGET executed, exporter/decode/refinement0,
VF1 ровно на нужном assertion; source unchanged. Все128Rust classifier controls
проходят (108positive+20negative). Строки на1меньше P3 из-за отдельного заголовка;
предикаты и колонки не переопределялись ради admission, TARGET вычислен до запуска.
Никакие frontend/setup failures не считаются intended negatives.

## Wrapping: операция отдельно от требуемых свойств

| Точная операция | Stock26.09 P2 | Stock26.10 M1 | Семантические свойства |
| --- | --- | --- | --- |
| const-pointer wrapping_sub(is_l as usize) | No such function15:17–54 | UNSUPPORTED, VF1 at14:17–54 | NOT PROVEN / не проверялись после support boundary |
| const-pointer wrapping_add(1) | No such function14:20–44 | UNSUPPORTED, VF1 at13:20–44 | NOT PROVEN / не проверялись после support boundary |

Прежний P2proofSHA1f2eaaa832a7183180675389979ec15c62a78b5d,
[run37686101335](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37686101335).
В M1 оба минимальных generic probe изолированы друг от друга/проекций,
имеют req true/ens true/on_unwind_ens false. Только поддержка операции:
не доказывают pointer/index correspondence даже гипотетическим PASS.
Фактическая первая причинная диагностика после exporter/decode0:

- `verified/lib.rs(14,17-54): error: No such function: std::ptr::const_ptr::<impl *const T>::wrapping_sub`
- `verified/lib.rs(13,20-44): error: No such function: std::ptr::const_ptr::<impl *const T>::wrapping_add`

Refinement0 и source unchanged в обоих; отсутствует completed own return/leak
и полный VF0. Автоматический класс INCONCLUSIVE сохранён; evidence interpretation
UNSUPPORTED относится к stock mapping/spec exact call, не к Rust операции.
Минимальный воспроизводитель — case wrapping_down/wrapping_end в
[fixture](stock-26.10/pointer-cases.rs), [runner](stock-26.10/run.sh)
извлекает ровно один case плюс общий comment header. Хеши извлечённых source/MIR/
logs в M1-EVIDENCE. No substitution обычным sub, new pointer specification/axiom
или unchecked bridge. Stock source также не содержит pointer wrapping mapping.

Выход к signed index-1, modulo address semantics, provenance при выходе/возврате,
точный wrapping_add reentry и terminal pointer/index associations остаются OPEN.
Rust memory-read-at--1 control **NOT RUN / NOT ACCEPTED** в этой фазе: не достигнуто
обязательство points_to/доступа. Старые excluded corrected drafts не включались.
Семантическая модель W_P(i) из POINTER-DESIGN — целевое требование, не принятое
stock доказательство. Сравнение адресов не передаёт чужую provenance/permissions.

## Source admission и caller audit

Создан отдельно обозначенный hosted certificate
[SOURCE-ADMISSION-CD371.json](stock-26.10/SOURCE-ADMISSION-CD371.json), SHA256
**a280e8ff994ae5dbe7bb579a3fea9b44b355df3187caaa7509f5840d0017375f**.
Все6групп получили те же certificate bytes. Старый f2ccc11b235e8f2224131ddef4a12c17409c58863c5712726cb13a02a4960bc7
сохраняет прежний источник; не заменён механически новым хешем.

Full SmallSort85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1;
после содержательного Git-blob сравнения проверены exact signatures,
полные body hashes (не изменились),9/9/30active statements и их новый line map.
merge_up/down/bidir start677/710/754. Caller expressions raw-parts+deref ->
slice::from_raw_parts{,_mut} изменились, что явно отражено в
[SOURCE-MAP](SOURCE-MAP.md#merge-stock-2610-substantive-admission-review).
Все8repo paths сверены с844/cdGit blobs независимо от sparse checkout.
Externalb6references остаются отдельным историческим ledger, не repo pins.

Public stable/unstable sort ZST returns в неизменных repository blobs закрывают
только маршруты этих callers. Они не закрывают standalone generic target;
direct general scratch ZST, zero-stride noninjectivity и его pointer guard bridge
OPEN. Даже для nonzero pointers требуются caller resources и terminal associations.
Source-text admission не является whole-source Rust refinement.

## Profile, расход и следующий шаг

[Новый воспроизводимый профиль](stock-26.10/PROFILE.md) закрепляет official26.10
archive, console/exporter/refiner, schema и полный58-file spec manifest;
source f76012fb, nightly2026-09-25. Все17Rust rsspecs и C headers равны exact
source bytes; archive source correspondence имеет обычное доверие official release.
Фактический rustc1.100.0-nightly f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f;
export/decode/refinement согласованы operational gate. Capnp1.0.1,
actual binarySHA256d1918073299744a63dde470a03a3ec4fbe5ec62da948b7ac4e4a2e9cb1dd7fa8
записан; apt package не pre-pinned, схема и decoder exit проверены.
Старый26.09 профиль/runner/spec references/results сохранены отдельно от new dir.

Единственный newjob113041515221:22:08:01Z–22:09:32Z = **91hosted job seconds**,
включая checkout/preparation/failures/upload/post steps. Setup32s, suite50.79s,
peakRSS274168KiB. Не было дополнительных/ошибочных push jobs или отмен.
**512старых +91новых =603/1800used;1197remain**, без reset/transfer/new budget.
Артефакт11514548135,404018bytes;ZIP SHA256
`e20a93c8cc5494761354cceebdeb57f451bf97cd35e9c1ccce13aa01829f0f86`
совпал с GitHub digest. Все исполняемые проверки только GitHub-hosted.

Предложение следующего шага: отдельно согласовать **design-only фазу exact
wrapping support** для f760stock boundary: требуемые signed index/modulo-address/
provenance/reentry posts, source applicability и strict positive/memory-negative
regression gate. До review этого trust/admissibility design не вводить specs,
аксиомы или patches и не расходовать1197s на unchanged retry. Эта рекомендация
не авторизует implementation/new phase. Whole merge refinement, memory/copy/
ownership/FnMut/full unwind/ZST bridge требуют отдельных решений.
