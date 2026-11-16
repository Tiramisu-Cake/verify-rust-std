# Передача пакета worker15

Статус новой редакции: подготовка для будущего CI-прогона; Kani **NOT_RUN**.

Исходный вход g0 задания: `18743fb816465180215fcd86410ecfd46763b0ed`; HEAD g0 при обновлении: `83c101ca810a24f14f932f6e5bb96dc6571d3872`. Kani stock: `0aac16ef62da9e9d5645782d458593e5d78143ba`. Worktree: `/root/kani-confirm-main-w15`, ветка `uninit-ci/confirm-main-w15-context-fix`.

Control: `bb427b45f38d05697e5b8bc0f15ff5e57eba7c19`; tree: `622d35a8fe4289dd16c76cb027998caf3252c13a`; единственный parent — stock `0aac16ef62`. Прежний control `6b653427d2911cb61c14757908e5e19491add138` сохранён на ветке `uninit-ci/confirm-main-w15`. Author control и g0: `Tiramisu-Cake <igkharin@gmail.com>`; сообщения содержат `[skip ci]`.

По сообщению пользователя, push-запуск `43878357528`, trigger `fd036c225f` (same-tree child прежнего control), отклонён при проверке workflow, jobs: 0. Выводов F1–F4 этот отказ не даёт. Причина в исходном YAML согласуется с документацией GitHub: `runner` недоступен в `jobs.<job_id>.env`.

Исправление: job env `CONFIRM_EVIDENCE_DIR` задаётся через `${{ github.workspace }}/../confirm-main-evidence`; upload читает `${{ env.CONFIRM_EVIDENCE_DIR }}/`. Все семь выражений сверены с [таблицей доступности контекстов](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts#context-availability): `github.workspace` в job env, `always()` в step if, `job.status` в step env, `github.run_id`, `github.run_attempt` и `env.CONFIRM_EVIDENCE_DIR` в step with.

`check_service.py` проверяет выражения текущего workflow и отвергает исходный `runner.temp` в job env, другие недоступные контексты/функции и неподдержанный синтаксис/расположение. Проверка не требует внешних Python-пакетов. Список всех выражений дополнительно сопоставлен с локальным YAML-разбором. Область проверки и ссылки на документацию: `STATIC-VALIDATION.json#/workflow_context_review`.

Статические и синтетические проверки прошли. `control.patch` применён в изолированном Git index поверх stock и восстановил точный control tree. `SOURCES.json` фиксирует SHA-256 и Git modes копий. Тесты F1–F4 и исходники компилятора/библиотеки в этой доработке не менялись. Совместимость F4 и его синтетический результат сохранены из предыдущего пакета с отдельной привязкой к прежнему control.

Следующая стадия: отдельно авторизованный push одного пустого дочернего trigger-коммита без `[skip ci]` с тем же tree; source gate принимает control или ровно одного такого потомка, fetch depth — 3. Возможен `workflow_dispatch` на control, если workflow доступен для dispatch. Новый trigger не создан; push, CI, публикации и ledger в этой доработке не выполнялись. Локальные cargo/rustc/Kani/CBMC не запускались. Для F4 покрытие порядка компиляции остаётся **UNESTABLISHED**.

Обновляется только `wave0/confirm-main/`; соседние изменения общего g0 сохранены.
