# VeriFast documentation review snapshot

Копия документации роли сопровождающего VeriFast для внешнего review.
Исходный рабочий репозиторий: `/root/verifast`; upstream:
`https://github.com/verifast/verifast.git`. Исходная ветка: `challenge8/verifast-maintainer`.
Commit: `d1d533d27fed74758b1462af29af7e17b2d960c9`; parent: `f76012fb518703b1d98e243ac4f487f16877cfcb`;
tree: `f4960777b638d4b9e7bf39c9c3232cb79a8f3a34`. Время упаковки: `2026-10-09T17:26:22+03:00`.

Исходные документы сохранены байт-в-байт из Git objects этого commit:

- [AGENTS.md](AGENTS.md)
- [docs/challenge8/WORKFLOW.md](docs/challenge8/WORKFLOW.md)
- [docs/challenge8/STATUS.md](docs/challenge8/STATUS.md)

[manifest.json](manifest.json) содержит исходные и пакетные пути, Git blob SHA
и SHA-256. [documentation.patch](documentation.patch) — исходный commit,
экспортированный через `git format-patch -1 --stdout --full-index --binary`;
он сохраняет фактическое авторство и точный diff относительно parent.

Выполнены статические проверки: исходный commit добавляет только указанные три
Markdown-файла; `git diff --check`; разрешение относительных ссылок в исходном
Git tree; parsing состава format-patch; побайтовое сравнение копий, Git blob SHA
и SHA-256 manifest; точный состав пакета и отсутствие изменений вне его каталога.
Это проверки документационной упаковки, а не tool regressions или proof results.

Инструкции относятся к рабочему репозиторию **VeriFast**. Этот каталог является
копией для review и не задаёт инструкции для работы proof-агентов в репозитории
назначения. Исторические ограничения и STATUS исходного запуска сохранены;
отдельное разрешение владельца сейчас охватывает только публикацию этого пакета
в `review/verifast`, без PR, merge, code review или расширения фазы.

Исходники инструмента не менялись. Cloud Build, компиляция, proofs и полноценные
регрессии не запускались; новых proof results нет. Review `ManuallyDrop::new`
не начат; coordinator, ledgers и proof pins не менялись.

Ограничения копии: upstream README-файлы, на которые ссылается AGENTS.md, не входят
в снимок; эти ссылки требуют исходного VeriFast checkout. Абсолютные VPS-пути и
Git-команды в STATUS относятся к исходному проекту. Snapshot не является полным
checkout, поставкой инструмента или новым checkpoint доказательств. Уже описанное
в STATUS расхождение merge checkpoint/ledger не исследовалось при упаковке.
