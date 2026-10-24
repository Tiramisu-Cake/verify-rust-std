# Review инфраструктуры K-1

Reviewer: `claude-subagent:smallsort-reviewer`, модель Claude Opus 5.5, effort high, отдельный контекст. Пакета `smallsort-session review` не было: review шёл по явному списку закоммиченных файлов и диффам. Kani, rustc, раннеры и `gh` reviewer не запускал. Formats Kani и поведение раннеров остаются непроверенными до smoke (EXPERIMENT.md §7).

| Кандидат | Решение | Находки | Исправлено в |
|---|---|---|---|
| `e84817c1b96a7e7f4db55f81d762565b6d4b67c5` | NO_GO | 2 blocker: FAILED без локализованной проверки, measurement без разобранных cover. 5 should-fix: нет перекрёстных проверок итога, хрупкий timeout, нет привязки к инструментам, RSS всего прогона, `time -o` на macOS. 4 nit | `a087a7e0` |
| `a087a7e0a2330763328c86ccfb7a5c155717d618` | GO_WITH_NITS | 3 should-fix: `expect_check` необязателен, подстрока ищется в пути файла, check-tooling доверяет отчёту run. 4 nit | `44d67cd1` |
| `44d67cd1de08214b7650cce41d1401bfb3c836a1` | GO_WITH_NITS | 1 should-fix: второй workflow мог бы выгрузить поддельную сводку. 2 nit: граничные длины R12, счётчик unreachable | `71d19a93` |
| `71d19a93adb70717a8fbc39c00eeb724f682ea23` | GO | нет | — |

Synthetic-тесты инструмента: 23, все проходят на `71d19a93`.

## Перенос lane на CircleCI

GitHub отключил Actions на форке (dispatch HTTP 422), lane перенесён на CircleCI. Тот же reviewer, те же условия.

| Кандидат | Решение | Находки | Исправлено в |
|---|---|---|---|
| `d79024ea6870563cfe82f14683a801cbb36135f8` | GO_WITH_NITS | 4 should-fix: потеря evidence при упоре в 60 минут, кеширование неполных артефактов, path traversal в путях артефактов, `.github/workflows` вне check-tooling. 1 adversarial: кеш Kani доверяется по коммиту. Мелочи | `a3073c49` |
| `f430cf132515a826b459e0f9d617198b35b61477` | GO_WITH_NITS | мелочи: файлы, влияющие на сборку, вне check-tooling; подпись пропуска verify; отмена при несовпадении ревизии | `897f19ec` |
| `77479d23b9d17d14abb39e0321e565843c46ffa2` | GO | Известная косметика: если запрос отмены в `dispatch` падает, вместо сообщения о несовпадении ревизии выводится ошибка отмены. Код выхода всё равно ненулевой | не исправлялось, чтобы не менять базу |

Ревизия после фазы 1: лимит памяти verify через cgroup v2. Тот же reviewer.

| Кандидат | Решение | Находки | Исправлено в |
|---|---|---|---|
| `951263dab59675b60eb7ede082d9a93e747c8cb6` | GO_WITH_NITS | Ложного GO нет. Мелочи: двусторонняя сверка OOM-kill и OUT_OF_MEMORY; пик cgroup включает page cache; swap не подтверждён; OOM при компиляции давал COMPILE_ERROR; место OUT_OF_MEMORY в вердикте; влезает ли компиляция в лимит | `aca80458`; последний пункт закрыл job 15 (пик 1,68 GiB) |
| `aca80458d4f60e6bee1697913a916b37b2ced0cb` | GO | — | — |

Smoke лимита: job 15, COMPLETE, gate true. Job 16: настоящий OOM `sort13_u8` дал OUT_OF_MEMORY, сводка сохранена. Synthetic-тесты: 27.

Smoke на CircleCI: job 2, 3, 4 — COMPLETE, gate true. Kani собирался с нуля за 204–208 с, весь job около 5 минут. Synthetic-тесты: 25, все проходят.

