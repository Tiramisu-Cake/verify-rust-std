# Review инфраструктуры K-1

Reviewer: `claude-subagent:smallsort-reviewer`, модель Claude Opus 5.5, effort high, отдельный контекст. Пакета `smallsort-session review` не было: review шёл по явному списку закоммиченных файлов и диффам. Kani, rustc, раннеры и `gh` reviewer не запускал. Formats Kani и поведение раннеров остаются непроверенными до smoke (EXPERIMENT.md §7).

| Кандидат | Решение | Находки | Исправлено в |
|---|---|---|---|
| `e84817c1b96a7e7f4db55f81d762565b6d4b67c5` | NO_GO | 2 blocker: FAILED без локализованной проверки, measurement без разобранных cover. 5 should-fix: нет перекрёстных проверок итога, хрупкий timeout, нет привязки к инструментам, RSS всего прогона, `time -o` на macOS. 4 nit | `a087a7e0` |
| `a087a7e0a2330763328c86ccfb7a5c155717d618` | GO_WITH_NITS | 3 should-fix: `expect_check` необязателен, подстрока ищется в пути файла, check-tooling доверяет отчёту run. 4 nit | `44d67cd1` |
| `44d67cd1de08214b7650cce41d1401bfb3c836a1` | GO_WITH_NITS | 1 should-fix: второй workflow мог бы выгрузить поддельную сводку. 2 nit: граничные длины R12, счётчик unreachable | `71d19a93` |
| `71d19a93adb70717a8fbc39c00eeb724f682ea23` | GO | нет | — |

Synthetic-тесты инструмента: 23, все проходят на `71d19a93`.
