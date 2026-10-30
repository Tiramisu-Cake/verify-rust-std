# BACKING — matched-пилот: форма stable scratch в гармониках

Дата: 2026-10-31. Исполнитель: Codex, одна свежая сессия, окно до 4 ч (основное время — ожидание сборок).
Worktree `/root/verify-rust-std-kani-backing`, ветка `experiment/kani-k1-backing-20261031` от `e6fee58855` (OPT;
library `f052d6b7ec` = Part 1 + DIRECT + opt-in модуль `merge::opt_split`). **Бюджет Cloud Build: не более $3 и не
более 2 сборок** (свой список build UUID/request_id; agent label `k1-network` общий с OPT/INTEG и расходы не
разделяет), пул k1-standard4; `CAP_USD 73.96` не менять; перед сборкой `k1g.sh budget` и полный envelope + резерв
закрытия в остатке окна. Сборку ждать **только через `k1g.sh watch BUILD` и завершать ход**. Результаты своих сборок —
штатно через `k1g.sh summary/peaks/log-grep/log-lines/check-tooling`; не применяются Evidence Brief и процедуры
Select/Merge, заменённые штатным K-1 интерфейсом; остальные глобальные инструкции, ограничения доступа и сохранения
evidence действуют. Actions/CircleCI — нет. Ветки `submission/*` не трогать. Pin Kani `9461e07a`, toolchain, flags,
lane-файлы не менять. Параллельно: OPT (его ветка, закончен по коду), INTEG (существующие символы `merge.rs`,
общий oracle/helper-ы). Новый код — **только новыми opt-in блоками в конце** `merge.rs` и `network.rs`; существующие
символы, в т.ч. `general_route_properties` и `dispatch_safety_fixed`, не менять. Свои блоки — отдельные именованные
opt-in модули `backing`; private функции `opt_split` из них не вызывать и visibility не менять (old B — по существующему
fully-qualified имени гармоники). Координатор переносит только library-diff этих блоков.

## Зачем

OPT (`RESULT-OPT.md`, G1/G2) на u64: гармоники, отличающиеся только формой scratch, расходятся по пику CBMC в 4–5 раз:
A N8 `MaybeUninit<[u64;48]>` 1,86 GiB / 222 с против `[MaybeUninit<u64>;48]` 8,03 GiB / 349 с; B N8 general 1,51 против
stable 7,93 GiB. Литерал `[MaybeUninit::<T>::uninit(); 48]` создаёт stable scratch во многих тяжёлых гармониках.
Две разные вещи: (а) законность adapter и сохранение API/proof-домена — статически обосновать **до** сборки;
(б) эмпирическая гипотеза стоимости — aggregate backing `MaybeUninit<[T;48]>`, переданный stable-входу как
`&mut [MaybeUninit<T>]` длины 48, дешевле. Нового generic-backing/E1/uninit результата эксперимент не даёт. Это изменение fixture гармоники (source identity меняется), а
не доказательство для любого backing: реальный driftsort даёт stack-буфер 4096 байт или heap, длина может быть > 48 —
ни старый, ни новый 48-slot fixture это не покрывает.

## Что сделать

1. **Adapter:** из живого `MaybeUninit<[T;48]>` получить `&mut [MaybeUninit<T>]` длины 48 (cast указателя +
   `slice::from_raw_parts_mut` или эквивалент) — без `assume_init`, без ссылок на неинициализированный `T`, без alias с
   `v`. SAFETY: provenance исходного указателя, выравнивание/размер, исключительный доступ и lifetime — backing живёт в
   caller-гармонике до конца использования среза; helper не возвращает ссылку на свой локал и не трогает holder при
   живом `&mut` view. Создаётся только `&mut [MaybeUninit<T>]`; `&mut [T;48]`/`assume_init` не появляются; assume о
   writability/non-alias вместо настоящей памяти не подставлять.
2. **Пары old/new, отличающиеся только backing** (+ adapter), прочее идентично (T, N, comparator, arbitrary значения,
   probe, oracle, flags, unwind, covers):
   - **B stable u64 N8:** old = `merge::opt_split::stable_direct_u64_n8`; new — тот же stable trait-вход
     (`StableSmallSortTypeImpl`, не прямой general) с aggregate backing.
   - **A N8:** новая stable-гармоника получает ровно геометрию `opt_split::general_contract_u64_n8` (aggregate backing,
     prefix N, хвост uninit, отдельный dst). Сверить и записать, достаточно ли этого PFC для нового stable caller;
     Это проверяемое условие: после adapter merge получает тот же prefix N от offset 0, хвост uninit, отдельный
     initialized any dst, тот же F/probe и frame; A проверяет merge, не stable trait. G2 OPT уже содержит matched пару
     old/new (`opt_split::general_contract_u64_n8` / `stable_contract_u64_n8`, source `c81c10e306`, build
     `0e44427c-18bd-4de4-95b2-e8730abec632`) — сверить прямой текст и транзитивные helpers/oracle/probe/T/F/flags/pin/
     memory setup; при совместимости переиспользовать с явной ссылкой (старый PASS/VT не приписывать новым именам/SHA),
     иначе включить пару в сборку. Новое доказательство не объявлять проверкой старого array-of-MaybeUninit контекста.
   - **Stable dispatch safety `[u8;17]` N32** (`network.rs`, `dispatch_safety_fixed` с STABLE=true; существующая ordinary
     `dispatch_safety_stable_unstable_bytes17_n32` проверяет обе ветви): old = stable-only вариант с текущим литералом,
     new = stable-only с aggregate backing; тот же `volatile_reading_less`, stub `panic_on_ord_violation`, unwind(65),
     covers normal return. Old может вызывать существующий `dispatch_safety_fixed::<[u8;17],32,true>` через новый
     stable-only wrapper. **Не сравнивать** new с прежним pair-harness или его 509 с macOS: это смешало бы эффект
     backing с удалением unstable-ветви.
   Все новые гармоники/helper-ы — opt-in под `cfg(kani_smallsort_controls)`.
3. **Контроли на новом backing** (opt-in, ожидание FAILED на конкретной проверке):
   - payload corruption после stable sort с сохранением ключа → отказ **настоящего** `assert_sorted_and_probe_preserved`
     (count);
   - нарушенный sorted-halves requires при корректной памяти aggregate backing → отказ precondition merge (штатный
     `--no-assert-contracts`, `stub_verified`, как A-контроль DIRECT);
   - намеренный raw-доступ за всю allocation 48 через указатель adapter → именно Kani memory/object-bounds failure, с
     cover до доступа и проверяемым check/location; safe indexing `scratch[48]` (Rust bounds assertion) не годится;
     non-ZST T. Compile error, unsupported и отказ иного класса контроль не закрывают; проверку uninit-чтения (не
     поддерживается на pin) успешной не объявлять.
4. Covers: нужные normal-return/ветви SATISFIED. Изменение числа checks из-за иной инициализации допустимо — объяснить;
   одного SUCCESS или равенства counts недостаточно.

## Сборки (kind `measurement`, jobs=1, controls:true, явные списки)

Перед первой: commit + push кандидата, последней строкой хода `PRE-BUILD REVIEW <sha>`, завершить ход; координатор
пришлёт GO или правки (review adapter и сопоставления доменов).
1. **Matched:** все пары old/new (без переиспользуемых по п.2) + 3 контроля в одном build. При reuse A — 7 entries,
   envelope (7×10+30)=100 мин, резерв ≈ $1,35; с парой A — 9 entries, 120 мин, ≈ $1,62.
2. Резерв: только необходимый subset по фактическому остатку (ошибка контроля, пара не попала); непоместившееся —
   PARTIAL/NOT_RUN. Если после первого build меняются setup/oracle/domain — delta на review до следующего proof-запуска;
   правка только request/expect_check не должна превращать посторонний отказ в успех. Третьего build нет.
Timeout 600 с не менять; old-вариант с TIMEOUT — тоже данные.

## Приёмка и результат

Пара принимается, если adapter законен, домен сохранён (описать по коду), new SUCCESS, covers выполнены, контроли
отказали на нужных свойствах и пик памяти new измеримо ниже в matched-паре; VT ≤ 600 с и суммарное время/цена
показываются отдельно (снижение памяти при умеренном росте VT — тоже полезный кандидат); выигрыш не обязан быть 4×.
Reuse A ясно отделять от новых B/dispatch-пар. GCB не подтверждает macOS/jobs3.
`research/challenge-8/kani-k1/RESULT-BACKING.md` (русский, ≤ 100 строк): SHA, build ID, стоимость; COMPLETE / PARTIAL /
STOP; таблица пар (гармоника, backing, статус, VT GCB, CBMC RSS, covers, checks); контроли; обоснование adapter и
доменов; какие ещё гармоники (по коду) используют литерал stable scratch и могли бы выиграть — список с приоритетом,
без изменения их кода; оговорки (fixture ≠ любой backing; macOS UNKNOWN; полный CI нужен).
Rustfmt:
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --check --edition 2024 --config-path /tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/fmtcfg/rustfmt.toml <изменённые .rs>`
— exit 0; строки ≤ 100; комментарии по бюджету соседних, без истории разработки.

## Ограничения

- Все коммиты `[skip ci]`; library-коммиты отдельно от `research/`. Push без force. Локально только Python и rustfmt;
  rustc/cargo/Kani/CBMC — нет. Логи — только summary/peaks/log-grep/log-lines (≤ 200 строк).
- Код, ветки и аудиты PR #576/#678/#694/#701 не открывать. Не упоминать rust-lang issues. Внешних действий нет.
  Спорное решать самому, владельца не ждать.

## Завершение

Commit + push. Последние строки ответа координатору (запрос review — не полученный GO):

```
REVIEW REQUEST <sha>
BACKING ЗАВЕРШЁН
```
После маркера сессию не продолжать.
