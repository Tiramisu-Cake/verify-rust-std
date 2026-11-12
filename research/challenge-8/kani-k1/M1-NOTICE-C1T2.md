# M1 — уточнение evidence и controls, 2026-11-12

Воркеру 14: прочитать во время текущей M1, не менять base и не переписывать уже опубликованные результаты.
Это верификация корректности, не security-работа. Cloud $0, без новых запусков/runner.

По координатору Quick **43219870063**, C1-T **28e684cbae348130d559b87e030536d8f8a3c1ff**, workflow-only
**172a7cfdbc02bd784873cfb4410d9b08fe51a9f1**: expected 125/1/2 ignored, единственный FAIL existing maybe-uninit-initialized.
Все 6 promoted-only C1-T matched goldens уже без M1: legal SUCCESS, hole FAILURE. Actual origins/causal failure sites неизвестны.

1. Не использовать C1-T как baseline-failing D0 reproducer или как доказанное Some/None immutable-mask qualification.
   Они остаются regression inputs. Inline MU refs могли дать другой storage/lowering/relevance путь — это пока гипотезы.
2. Не выводить MU raw_eq bypass по одному T: RawEq CheckAs uses [u8;size]. Нужны actual MIR/ops/фактический initializing event,
   либо доказанное отсутствие instrumentation; агрегатные verdict/golden match этого не дают.
3. D0-A диагноз конкретной .2 сохраняется: promoted immutable [u8;4] RHS стартует false, left tracked temporary setter работает.
   C1-T pass его не опровергает; M1 по-прежнему обязан исправить **оба исходных D0 legal** при сохранении full-byte checks.
4. Воркер 15 готовит C1-T2: mixed tracked stack/promoted, оба порядка, direct raw_eq/native == legal и valid MU-hole raw_eq.
   У hole через std [u8] == есть ранняя validity граница; такой input не считать faithful SpecArrayEq byte-read control.
5. Contract M0 не отменён, но доказательства M1 обязаны показать exact affected path: qualified actual immutable referent,
   source Some/None → emitted symbol → post-reset witness seed → нужный get. Не «лечить» один уже проходящий путь,
   не добавлять type-based true/skip, не расширять registry eligibility по SUCCESS новых probes.
6. Продолжать независимую реализацию/статику; fixture findings вернуть владельцу 15 через координатора.
   Импорт C1-T2 — exact test-only commit, старые шесть файлов не менять. Если путь/qualification M1 противоречит new binding,
   STOP semantic acceptance с конкретным gap; не присваивать READY статусу значение CI PASS.

Acceptance M1: unchanged D0 baseline FAIL → M1 legal SUCCESS с retained checks; mixed inputs и intended holes с operand binding;
сохранённые C1-T outcomes и остальные legacy controls без extra failures. Возможное совпадение baseline/M1 на C1-T отдельно
раскрыть. Без достаточной binding evidence оставить qualified control status UNKNOWN/NOT_RUN, не proof credit.
Дополнить CI-REQUEST/результат M1 ссылкой на это уведомление; runtime анализ/CI остаются у координатора.
