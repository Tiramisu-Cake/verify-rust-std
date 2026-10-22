# Network: запуск направления 2026-10-22

Решение владельца 2026-10-22: третий proof-владелец **`network`** (метка Network)
наряду с `select-sort4` и `merge`. Миссия — W7 → W8 из
[COMPLETION-PLAN](https://github.com/Tiramisu-Cake/verify-rust-std/blob/main/research/challenge-8/COMPLETION-PLAN.md):
actual `swap_if_less` (R4), связь доказанных сетей 9/13 с actual Rust schedule,
затем `small_sort_network` caller (regions, insertion остатка, merge в stack
scratch, copy-back, panic/abort). Network-ветвь самостоятельна и не ждёт general.
Этот документ — вход нового владельца; он не выдаёт Cloud budget и не
регистрирует phase.

## Место работы

| Что | Значение |
| --- | --- |
| Worktree / branch | `/root/verify-rust-std-networks`, `challenge-8/networks` (прежняя исследовательская ветка сетей, последняя работа 2026-10-07) |
| Tool worktree | `/root/verifast-network`, branch `challenge8/network-20261022` от `f76012fb518703b1d98e243ac4f487f16877cfcb` (та же база, что у Select; Select работает поверх неё overlay/spec/profile chain) |
| Среда | Задание указывает `Runtime`. Первая сессия — Claude Code; следующая может быть Codex. В worktree устанавливаются обе точки входа (`CLAUDE.md`, `AGENTS.md`) |
| Shared std baseline | upstream `cd371e035c7e573760c43bf934d53e8118ee3e7d`, SmallSort blob `40939f922bcb6fdc7ee0d30427fa861827043827` (как в COMPLETION-PLAN) |

Библиотека в ветке сейчас старее: SmallSort blob `e555fce440872898e47fd5114f32eb15401d07df`
(main форка). [SOURCE-MAP](../networks/SOURCE-MAP.md) закреплён на full-file
SHA256 `32574fd0…`. Сертификаты последовательности 25/45 вызовов и тело
`swap_if_less` нужно перепроверить на shared baseline до их использования:
статическое сравнение Git/hashes/текста на VPS разрешено, compile/extraction — нет.

## Зависимость от Select: один callback-слой

`swap_if_less` использует тот же pointer-select (`select_unpredictable` на
`*mut T`), callback и ManuallyDrop/read/copy ресурсы, что Select строит для sort4.
Network — **потребитель** опубликованного слоя Select, без параллельной
реализации и без второго trusted profile. Снимок на момент запуска: published
head Select `8a1d0b14d0dcfa375c47056f6d1388389201af98` (R19, c3 прошёл, c4 —
frontier), pinned profile R17
`research/challenge-8/cloud-build/sort4-caller-entry-native/A1-ACTUAL-C2-R17-PROFILE-2026-10-21.json`
SHA-256 `87a0bfe586b40a33bdf840164aec8748872c8fdd11b3faad421d3860d1f2a091`.
Перед использованием заново определить актуальный published head/profile Select
по Git; чужой worktree/ledger не менять. Если слою нужно изменение для
`swap_if_less`, оформить его как reviewed patch-кандидат на точном commit и
явно передать; молча расходящиеся копии запрещены.

Одно сравнение `swap_if_less` проще пяти в sort4, поэтому R4 — ранний второй
потребитель интерфейса и проверка его переносимости. Это не делает Network
владельцем sort4 и не переносит кредит между целями.

## Cloud: пока нет

Coordinator v3 (`/root/smallsort-ci-coordination`) допускает только владельцев
`select-sort4`, `merge`, `verifast` (`V3_OWNERS` в `coordination.py` каждого
клиента), максимум 3 активных Build. У `network` нет собственного клиента
(`control.py` с phase registration), а `smallsort-session prepare/wait` его ещё
не поддерживают. Поэтому задания Network выдаются с **бюджетом 0** до отдельной
миграции coordinator на четыре владельца и публикации собственного клиента.
Подготовка этой миграции и клиента — допустимая работа Network в виде reviewed
пакета PREPARED_NOT_REGISTERED; исполнение миграции и изменение `active.json`
или клиентов Select/Merge — только по решению владельца. Прежняя миграция v4
(`/root/verify-rust-std-coordinator-v4-refinedrust`, 2026-10-12, не принята)
может служить образцом, но не авторизацией.

GitHub Actions разрешены только роли verifast; прежние hosted runs сетевой ветки
остаются историей и не задают текущий lane.

## Что уже есть и чего нет

Прежние результаты ветки (stock VeriFast 26.09, hosted Actions, 2026-10-07)
сохраняют свой scope: N9 exact и общий rank bridge приняты; N13 universal
symbolic component принят, exact adapter 0..12 OPEN; `swap_if_less` —
только effect-aware спецификация ([SWAP-CONTRACT](../networks/SWAP-CONTRACT.md)).
Ни одна из этих теорем не даёт Rust memory/UB coverage, ownership или proof
actual Rust тела; R4 остаётся на 25% (исторический Kani i32). Детали и
обязательства интеграции — [INTEGRATION](../networks/INTEGRATION.md),
[STATUS сетей](../networks/STATUS.md).

## Роли

Maintainer VeriFast принимает только готовые опубликованные tool-патчи
([VERIFAST-ROLE](../VERIFAST-ROLE.md)). Proof, contracts/source correspondence и
consumer pin остаются у Network. Independent review — по профилю среды
(Claude: `smallsort-reviewer`, Codex: Luna HIGH).
