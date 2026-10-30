# BACKING2 — досборка прямого u64 N6/N7 (general split + stable aggregate) и проверка конкуренции

Дата: 2026-10-31. Исполнитель: Codex, одна свежая сессия, окно до 3 ч. Worktree `/root/verify-rust-std-kani-backing`,
ветка `experiment/kani-k1-backing-20261031`, продолжать от `a3e0dc4cda` (итог BACKING). **Бюджет Cloud Build: не
более $2,5 и не более 2 сборок** (свой список build UUID/request_id; agent label `k1-network` общий), пул k1-standard4;
`CAP_USD 73.96` не менять; перед сборкой `k1g.sh budget` и полный envelope + резерв закрытия в остатке окна. Сборку
ждать **только через `k1g.sh watch BUILD` и завершать ход**. Результаты своих сборок — штатно через `k1g.sh
summary/peaks/log-grep/log-lines/check-tooling`; не применяются Evidence Brief и процедуры Select/Merge, заменённые
штатным K-1 интерфейсом; остальные глобальные инструкции действуют. Pin Kani `9461e07a`, toolchain, flags, lane-файлы
не менять. Actions/CircleCI — нет. Ветки `submission/*` не трогать.

## Зачем

Цель — прямое (без stub merge) доказательство general/stable u64 N6..8 с уменьшенным пиком памяти (пригодность для
macOS — UNKNOWN; на dispatch aggregate backing не переносить: bytes17 N32 дал регресс). Есть:
general split N6/N8 (`merge::opt_split::general_direct_u64_n6/n8`, 0,83/1,51 GiB, OPT G1/G2) и stable aggregate N8
(`merge::backing::stable_direct_u64_n8`, 1,51 GiB / 214 с, BACKING). Не хватает: **general N7, stable aggregate N6 и
N7**. Также не измерено поведение этого набора при `--jobs=3` (OPT G3: старые stable N8 дали OOM на 16 GiB).

## Что сделать

1. В модуле `merge::backing` (opt-in) — `stable_direct_u64_n6`, `stable_direct_u64_n7` через тот же
   `stable_direct_body` и adapter `scratch_view` (единственное разрешённое изменение существующего helper —
   const-guard `N == 6 || N == 8` расширить до 6/7/8; тело, adapter и oracle неизменны), и
   `general_direct_u64_n7` — прямой `small_sort_general` с тем же oracle, `set_value_probe`, `lt_u64`, unwind(34),
   одним cover, без symbolic `stable` (как `opt_split::general_direct_body`; private helper `opt_split` не вызывать и
   visibility не менять — свой helper в `backing`). Прочие существующие символы не менять.
   Для N7 явно отметить нечётные половины merge (3/4).
2. Review: commit + push, последней строкой хода `PRE-BUILD REVIEW <sha>`, завершить ход; ждать GO координатора.
   До первого dispatch записать T0 и резерв закрытия. Evidence/requests BACKING2 — отдельный namespace
   (`backing2/`) и отдельный список UUID/расходов; старые BACKING/OPT исходы, расходы и OOM не переписывать.

## Сборки

1. `measurement`, jobs=1, controls:true: три новые гармоники (envelope 3×10+30 = 60 мин). Контроли BACKING уже
   проверили adapter/oracle на том же helper — новые не нужны, если helper/oracle не менялись (любое semantic
   изменение — delta-review и контроль). **Gate:** все три SUCCESS ≤ 600 с, covers SATISFIED, oracle/компаратор/flags
   прежние, память измерена; если клетка не прошла — успешные сохранить отдельно, полный набор 6 не объявлять принятым.
2. `diagnostic`, `kani_jobs: 3`, controls:true: полный прямой набор u64 N6..8 — `opt_split::general_direct_u64_n6`,
   `backing::general_direct_u64_n7`, `opt_split::general_direct_u64_n8`, `backing::stable_direct_u64_n6/n7/n8`
   (6 entries, envelope 90 мин) — только эти 6, без старых array-backed stable и без A. Это диагностика
   Linux-конкуренции на 16 GiB, не сертификация 7-GiB macOS и не measurement/полный CI: проверить по `peaks`, сколько
   CBMC реально перекрывались (меньше 3 — не подтверждение трёхпроцессного пика), пики CBMC/driver, OOM/missing,
   полноту всех 6; сумма RSS не равна физической RAM. Запускать только после gate сборки 1 и по фактическому остатку:
   резервы 60 мин ≈ $0,81 + 90 мин ≈ $1,215 = 150 мин / $2,03 — при полном расходе на остальное остаётся ~30 мин окна.
Timeout 600 с не менять; TIMEOUT/OOM — тоже данные.

## Результат

Дописать в `research/challenge-8/kani-k1/RESULT-BACKING.md` раздел «BACKING2» (≤ 50 строк): SHA, build ID,
стоимость; таблица (гармоника, маршрут/backing, статус, VT GCB, CBMC RSS, covers, checks); конкуренция jobs=3;
итоговый список **кандидатов прямого u64 N6..8 в ordinary** с источником по каждому имени (OPT G1/G2 — general N6/N8,
BACKING — stable N8, BACKING2 — остальные 3) и статической проверкой неизменности транзитивных helpers/oracle/flags
(старый PASS не выдавать за measurement нового SHA); оговорки: fixture ≠ любой backing; macOS UNKNOWN; пригодность —
только полный CI организаторов. Для ASSEMBLY: при успехе обеих ветвей N они могут заменить прежний stubbed caller
этого N; старые тяжёлые A/B — исторический opt-in; если одна ветвь не проверена — домен N не закрыт.
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
BACKING2 ЗАВЕРШЁН
```
После маркера сессию не продолжать.
