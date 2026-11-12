# CBMC ZST bits2expr — исходники, план и границы

2026-11-13. Это верификация корректности, не security-работа. **GO на подготовку source/tests**, не на fork/CI/публикацию.
G-SC/PFC-resource остаётся на паузе до аудита; этот B3 backend-трек независим. Cloud $0, локальные CBMC builds запрещены.

## Факты и pinned source

- Владелец подтвердил CBMC6.11.0 в Kani fork CI [43241563566](https://github.com/Tiramisu-Cake/kani/actions/runs/43241563566):
  typed dereference W с zero-width array member → invariant/exit134; union и interior-field варианты — тот же invariant;
  memcpy control проходит. Здесь эти прогоны не повторялись, raw logs не читались.
- [Issue drafts](../b3p/ISSUE-DRAFTS.md) закреплены t0 @d377f342f49b2e39498745198df73f4d1999a593. Это ещё не опубликованные issues;
  placeholder #N нельзя выдавать за созданный issue. Kani B3 workaround6e9e782024 не исправляет CBMC и embedded-ZST case B.
- Release cbmc-6.11.0: **820ff0f555b43fb78e0cd9332e498461bd14244b**.
- Проверенный develop: **107a1e504cd69a2f3483717c8bcfcfa59814c557**, tree b5a15d682996f745e0a02004d813e18d08f3a068.
  На этой ревизии array guard всё ещё `el_size_opt.has_value() && *el_size_opt > bitst{0}`.
  **Этот барьер не исправлен.** Сам C repro на develop ещё не выполнялся; это source finding, не новый observed crash.

## Механизм и минимальный fix

[bits2expr](https://github.com/diffblue/cbmc/blob/107a1e504cd69a2f3483717c8bcfcfa59814c557/src/util/simplify_utils.cpp#L196)
восстанавливает expression из memory-order bit string после проверки размера type. Struct режет bits на компоненты,
допускает component width0 и рекурсирует; tags следуют определению с восстановлением tag type. Union выбирает первый arm,
который может представить переданные bits; отсутствие результата остаётся optional failure.
Array требует constant count, затем **ошибочно запрещает element width0**, хотя его цикл уже берёт `i*el_size,el_size`.
При el_size0 каждый slice пуст, рекурсия в empty struct/zero-width nested array естественна, result имеет N operands.
Нет деления на el_size в этой ветке. Следовательно узкая поправка — разрешить known **nonnegative** size вместо strictly-positive,
сохранив presence check и прежнюю обработку остальных размеров; на develop использовать сильный тип bitst, не старый mp_integer API.

[expr2bits](https://github.com/diffblue/cbmc/blob/107a1e504cd69a2f3483717c8bcfcfa59814c557/src/util/simplify_utils.cpp#L413)
уже конкатенирует bits operands: пустой struct/array добавляет пустую строку. Изменение этого направления пока не обосновано.
[simplify_byte_extract](https://github.com/diffblue/cbmc/blob/107a1e504cd69a2f3483717c8bcfcfa59814c557/src/util/simplify_expr.cpp#L1888)
имеет отдельный guard zero-width **outer result**; его нельзя путать с zero-width subtree внутри непустой W.
Путь constant byte-extract вызывает bits2expr и способен дойти до дефектной array recursion. Массовую замену >0 в соседних ветках не делаем.

Риски: type/tag/operand-count корректность nested arrays/unions; zero length против zero element width; unknown/negative sizes;
непустые bytes соседних полей и endian order; O(N) IR при очень большом N с нулевым extent; отдельные byte-extract пути.
Не подставлять fake bits, не zero-initialize весь enclosing struct (это затрёт 0x5a), не конструировать значение неподдержанного
subtype через произвольный initializer. Если recursion не умеет subtype, сохраняется optional failure. Vectors/complex — отдельно.

## Порядок и трудоёмкость

1. **Worker15, одна source-only сессия:** exact develop clone, минимальный array fix, регрессии в том же коммите,
   focused util unit tests для empty conversion/roundtrip при подходящем API, clang-format/static review. Ничего не собирать.
2. **STOP для решения владельца:** нужен ли его fork diffblue/cbmc и где выполнять CI. Пока форка нет; автоматически не создавать.
   До решения — локальный source commit и CI-REQUEST, без push/dispatch. Cloud не нужен при fork Actions, Actions quota отдельно.
3. **Координатор, после разрешения:** один paired CI baseline-develop + те же tests против fix; затем соседние regressions/unit.
   Старый6.11 repro использовать как известный baseline, не обещать новый develop crash до CI. Не нужен полный CBMC matrix в первом probe.
4. **Владелец:** после подтверждения develop repro сначала issue с минимальным C/версией/exit134 и корректной связью Kani#5085/B3;
   затем один PR в develop: fix+tests, subject+body, CI и scope. Подготовку patch не нужно задерживать ожиданием issue comment.
   Если develop уже не воспроизводит путь, STOP и минимизация текущего pipeline; старый invariant сам по себе не новый runtime verdict.

Оценка: source delta очень мала; tests/review и подготовка пары CI — около одной worker-сессии (ориентир полдня–день).
Точечного измерения времени CBMC build у нас нет; это отдельная CI-сборка, а не продолжение быстрых Kani probes.
При втором независимом failure после narrow fix — описать границу и вернуться к координатору, не расширять patch в общий backend rewrite.

## Критерий результата

Baseline + exact same C tests должен показать invariant для реального repro, fix — VERIFICATION SUCCESSFUL и сохранённые bytes/fields;
memcpy positive проходит в обеих версиях. Нужен negative assertion companion с правильным FAILED, чтобы не принять удалённые checks.
Unit cases: typed empty result/count и roundtrip на supported subtypes; nonzero/endian behavior не меняется, unknown-width support не добавляется.
Подготовленный source не compiled/proved; Kani B3 workaround не откатывается до отдельного обновления backend и Kani regression.
Никаких issue/PR публикаций, fork creation, push, builds или CI этой стадией не выполнено.

Политика: [AGENTS](https://github.com/diffblue/cbmc/blob/107a1e504cd69a2f3483717c8bcfcfa59814c557/AGENTS.md),
[CODING_STANDARD](https://github.com/diffblue/cbmc/blob/107a1e504cd69a2f3483717c8bcfcfa59814c557/CODING_STANDARD.md),
[regression runner](https://github.com/diffblue/cbmc/blob/107a1e504cd69a2f3483717c8bcfcfa59814c557/regression/test.pl).
