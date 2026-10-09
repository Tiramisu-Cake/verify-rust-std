# Архив прежних инструкций — не действующая процедура

Снимки сохранены **побайтно**, без правки historical claims, budget и stop wording.
Все команды/«next»/«CURRENT» в них относятся к исходной дате/поручению. Для работы
использовать [WORK-POLICY](../../WORK-POLICY.md), [runbook](../../AGENT-RUNBOOK.md)
и последнее конкретное поручение/checkpoint своей ветки. Эта архивация не
возобновляет Actions, закрытые proof-фазы или retired budgets.

AGENTS, AGENT-RUNBOOK, README, WORK-POLICY, COMPLETION-PLAN сняты с main
`d8a3207bbf3a0c865745152162753aa733b41fba`. Снимок AGENTS назван AGENTS-ARCHIVED.md, чтобы tooling не обнаруживало
исторические правила как действующий nested AGENTS. Оригинальные расположения:
`AGENTS.md` и `research/challenge-8/<имя>.md`.
[Main tree исходной редакции](https://github.com/Tiramisu-Cake/verify-rust-std/tree/d8a3207bbf3a0c865745152162753aa733b41fba/research/challenge-8).
Cloud README/PARALLEL snapshots — из обеих рабочих веток:
merge `fbc063ce609cc549358e3bbc0f8b3a12b75b3945`, select
`4b0afb13609fac45884afb3bbd092980061d8d53`, исходно
`research/challenge-8/cloud-build/{README,PARALLEL-BUILDS}.md`.
[Merge original Cloud docs](https://github.com/Tiramisu-Cake/verify-rust-std/tree/fbc063ce609cc549358e3bbc0f8b3a12b75b3945/research/challenge-8/cloud-build),
[select original Cloud docs](https://github.com/Tiramisu-Cake/verify-rust-std/tree/4b0afb13609fac45884afb3bbd092980061d8d53/research/challenge-8/cloud-build).

Относительные ссылки внутри неизменных снимков сохранены в **исходной** топологии;
для их навигации открыть оригинал в закреплённом tree выше. Ссылки активной
редакции и этого индекса проверяются относительно текущего расположения.
Ранее существовавшие несовместимые/устаревшие указания внутри snapshots не
исправляются задним числом. История proof-веток остаётся там, куда ведёт оригинал.

| Побайтный snapshot | SHA256 |
| --- | --- |
| [AGENT-RUNBOOK.md](AGENT-RUNBOOK.md) | `bb304d75b021970413b9e7d3b75c8f53363593e170bbf50428e47bc3e73cc3cb` |
| [AGENTS-ARCHIVED.md](AGENTS-ARCHIVED.md) | `03d3364318b57a87cdd5c65f1cab53e84461701d68f1f2f6653d4e79c83604f6` |
| [COMPLETION-PLAN.md](COMPLETION-PLAN.md) | `11c51d7ea04263d1a83381b149eaafae4d428166ee74f60400d20a44f2934dcc` |
| [README.md](README.md) | `72d8e6a6e070a23d2a5f187c9f27d93a9d57ec68984244bf1aa5d6d35a94359f` |
| [WORK-POLICY.md](WORK-POLICY.md) | `f26b886446220d6aeb34ac014059126d2a8832a8359a88118200ce934f380184` |
| [merge-cloud-PARALLEL-BUILDS.md](merge-cloud-PARALLEL-BUILDS.md) | `dbc2c8efafc307a154f1050ddad7903946c5c21b37507c555888dbadb59b0f3b` |
| [merge-cloud-README.md](merge-cloud-README.md) | `e5e502f62d1f87715a9845f6654eea1f5ef280ccaec9603c5ecb0c1f2d7e381e` |
| [select-cloud-PARALLEL-BUILDS.md](select-cloud-PARALLEL-BUILDS.md) | `dbc2c8efafc307a154f1050ddad7903946c5c21b37507c555888dbadb59b0f3b` |
| [select-cloud-README.md](select-cloud-README.md) | `a6cd36dcb66cf45ffb80f0948a7f5c2db172a970ff924be18b0874b10e40cdac` |
