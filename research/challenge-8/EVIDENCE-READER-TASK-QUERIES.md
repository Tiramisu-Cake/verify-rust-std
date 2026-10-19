# Адресные запросы к существующим Builds: Merge / Select

Редакция v0.9 от 2026-10-19. Сначала [краткий guide](EVIDENCE-READER-GUIDE.md). Это чтение существующего evidence, не новая proof-сессия. Информация о проверенных запросах ниже взята из инструкции установки v0.9.

## Merge: prefix214

В Build `5f668cd9-fb34-4570-ad1c-4b97abbb36d0` prefix-файл имеет 216 строк. Запрос **210–216** уже успешно проверен при установке и кешируется:

```bash
smallsort-brief 5f668cd9-fb34-4570-ad1c-4b97abbb36d0 --refresh --file 607839ba7f21c33ff3ad3e988fe0f260ff5dba89e277011f9a54a78b34b46872 --start 210 --end 216 --expect-sha256 dd2e56890c425d4c0a6ff68750c62b272d12ad29cdd8282e8b99d0b35ea2aecd
```

Путь: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/prefix/cases/actual_three_current_full_posts/verified/lib.rs`. По инструкции установки строка214 — `let begin = values.as_mut_ptr();`. Сопоставь диагностическую позицию с точным ответом/source identity; это не доказательство причины отказа.

**Не повторяй 210–218:** он уже вернул LINE_RANGE_OUT_OF_RANGE. Эти два разных диапазона заняли два резервирования; текущий остаток квоты может быть меньше из-за других запросов. Не делай новый Build ради фрагмента.

## Select: сначала вход парсера, затем позиция9362

Build `87df47e4-002b-432c-bc87-56612136b448`. После проверки сохранённого `/first_blocker` через Reader:

```bash
smallsort-brief 87df47e4-002b-432c-bc87-56612136b448 --refresh --file cc20cf422e3f3828330adb99a0a55222711961bbb855f3b12dfc360c537a3e96 --pointer /first_blocker --expect-sha256 81414bda84c65ced707c66e720f3c26938b4dd321e920952065807635e838769
```

Установи цепочку «ошибка → входной файл/поле → SHA → преобразование». Наличие `focus/P0a/normal-mir.txt` в каталоге её не устанавливает. Если binding отсутствует, оставь NOT_ESTABLISHED и ищи только адресные диагностические сведения; не меняй грамматику по синтетическому escape.

После установления входа запроси окно9362 с единицами, соответствующими коду парсера (`unicode-codepoint` для Python str), точным file ID/SHA и узким radius. Нужны реальный literal/field/escape, имеющееся decoder error и при необходимости hex; targeted не вычисляет отсутствующую ошибку парсера за него.

Для R2–R7 сначала Reader pointer `/case_status/R2` (и аналогично другие), затем тот же узкий pointer с refresh только при нехватке данных и с учётом общей квоты. Нужны status/reason/observed stage/outcome/provenance/gate/credit; неизвестное не заполнять из агрегата. Для P1 equality/reference и N-false31 lifecycle сначала найди конкретные receipts каталогом, затем запроси необходимые поля.
