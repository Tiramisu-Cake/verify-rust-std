# Офлайн-review семи открытых PR

Все семь review завершены; root проверил запечатанные файлы, manifests и привязки к опубликованным исходникам. Ветки, тесты и публичные тексты не менялись. Это рекомендации по точным версиям PR; native-тесты и CI в рамках review не запускались. #4591 и его новый CI ведутся отдельно; verify-rust-std#752 отложен для отдельного разговора.

Большая часть смысловых тестов обоснована. Основная экономия — общие helpers/expected, упаковка файлов и повторные вызовы драйвера. Соотношение строк тестов и фикса само по себе не стало основанием для удаления проверки.

| PR | Что сохранить | Конкретные рекомендации |
|---|---|---|
| [Kani #5172](pr-5172/HANDOFF.md) | Все 24 harness в 22 отдельно компилируемых исходниках; fail-closed guards, plain/seeded разделение | Вынести 11 одинаковых copy helpers в стандартный auxiliary; объединить 8 одинаковых expected через существующий directory fallback. Исправить комментарий о переносе return-state, упростить один одноразовый адаптер, сократить PR-текст. Негативное покрытие новых shim-guards вынесено отдельно. |
| [Kani #5176](pr-5176/HANDOFF.md) | Все 14 смысловых случаев и небольшой typ.rs fix | Перенести 5 edge-shape fixtures в main с 12 harness и полным итогом успеха/всеми covers. Две recursive-проверки оставить отдельными компиляциями, но в том же каталоге. Тестовые артефакты могут сократиться с 16 до 6. Убрать повторные комментарии и неверное «cover в каждом harness» из PR. |
| [Kani #5195](pr-5195/HANDOFF.md) | Оба regression harness, compiler fix, полный uninit singleton/pair oracle с именами/статусами/locations/signatures | Удалить отдельный дублирующий padding control и 4 ordinary singleton-вызова: 14 вызовов драйвера → 8, из них 6 uninit и 2 ordinary pairs. Переименовать order-implying labels в реальные call-path names, слегка упростить plumbing. Большая часть check.py защищает оракул и нужна. |
| [Kani #5159](pr-5159/HANDOFF.md) | Все 8 harness и существующий volatile/ZST fix | Усилить expected для unaligned и uninhabited негативов конкретными причинами/завершёнными итогами; сократить комментарии и PR-текст. Удаление смысловых тестов не обосновано. |
| [Kani #5184](pr-5184/HANDOFF.md) | Все 3 harness и обе компиляции; compiler byte-exact | Только необязательное пояснение depth-zero analysis и короткий PR-текст. Recursion rejection и оба acyclic repeated-call контроля нужны. |
| [Kani #5183](pr-5183/HANDOFF.md) | Оба automatic target и оба отдельных вызова; compiler/body/shell byte-exact | Добавить 2 именованных target banner в expected, сохранив текущие статусы и summaries. PR должен описывать entry initialization; текущий тест использует два процесса. Удалять тесты или строить новый driver не нужно. |
| [CBMC #9487](pr-9487/HANDOFF.md) | Однострочный production guard, все 3 unit cases и C-регрессию | **P2: вставить пустую четвёртую строку test.desc.** Сейчас `^EXIT=0$` поглощается полем grep_options и не проверяется. Сохранить остальные verdict/signal/invariant patterns и GNU boundary. Опционально сократить исторические комментарии и PR по правилам CBMC. |

## Отдельный пробел покрытия #5172

Новые generated-shim guards для union/unclassified storage не имеют направленного негативного fixture. Текущие guards сохраняются. Нужен отдельный ограниченный follow-up, который доказывает достижение конкретного guard: ранний UnionAsField/setup error или только caller-side rejection не заменяет нужную проверку. Review не установил unsound execution. Точные условия — в [SOUNDNESS-FOLLOWUP.md](pr-5172/SOUNDNESS-FOLLOWUP.md).

## Предлагаемый порядок дальнейших решений

1. Выбрать один PR для отдельной правки. Наиболее конкретные небольшие oracle-исправления — descriptor CBMC #9487 и два expected Kani #5159.
2. Отдельно решить scope негативного shim-покрытия #5172; не добавлять его незаметно к уборке дубликатов.
3. Для снижения нагрузки на ревьюера применить обоснованную упаковку #5172/#5176 и сокращение вызовов #5195. Смысловые случаи, flags/discovery и точные оракулы сохраняются.
4. Короткие комментарии и PR-предложения уже даны в каждом packet. Kani license/AI disclosure сохраняются; для CBMC использованы его template/license, без вставки Kani Apache/MIT текста.

Перед изменением исходников — отдельное ограниченное задание; затем exact review и CI соответствующей версии. Push в открытую ветку, PR-body и комментарии — только по команде владельца, по одному PR. Эта сводка не запускает реализацию, CI или публикацию. Публичные/исторические CI-утверждения из PR bodies не были заново подтверждены этими source/static reviews. Перед дальнейшей работой проверить, не изменились ли публичные головы.

Точные commits, source heads/trees, merge bases, body и manifest digests — в [REFERENCES.json](REFERENCES.json) и [HANDOFF.md](HANDOFF.md). Каждый review содержит точную таблицу KEEP/REMOVE/MERGE/REWRITE и предлагаемые изменения.
