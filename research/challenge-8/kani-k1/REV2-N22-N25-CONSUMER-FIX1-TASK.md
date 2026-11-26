# REV2 N22–N25 consumer · FIX1 после ревью R1

Задание для **w14**, та же стадия. Ревью R1 — NO-GO с одним блокером, содержание пакета признано корректным. [Ревью](REV2-N22-N25-CONSUMER-REVIEW.md) · [Handoff](REV2-N22-N25-CONSUMER-HANDOFF.md)

1. **Автор.** Пересоздай Std-коммит поверх `b076d2ff4e` с автором и коммиттером `Tiramisu-Cake <igkharin@gmail.com>` (например `git -c user.name=Tiramisu-Cake -c user.email=igkharin@gmail.com commit --amend --reset-author --no-edit` в чистом worktree). Содержимое tree Std не меняется. Затем пересобери bundle, обнови OVERLAY/BUNDLE_SHA256 и CI-REQUEST, пересоздай Control-коммит поверх `279c2200a8` тем же автором, и detached review-trigger с тем же tree и sole parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. Все дальнейшие коммиты, включая g0, — с явным `-c user.name=Tiramisu-Cake -c user.email=igkharin@gmail.com`. Уже записанный g0 `ca3e7862f2` не переписывай.
2. **Неблокирующее 3.** В `ch8-cal1/request.py:455` замени `bindings.get("historical_blobs", {})` на обязательный ключ с явной ошибкой и добавь тест на отсутствие ключа.
3. **Неблокирующее 4.** В handoff пометь covers путей (`*_ALL_TAIL_SHIFTS`, `RIGHT_S13_PREFIX13_INVERSION`, `ODD_*_REMAINDER`) как предикаты входной маски; путь привязан офлайн-аргументом.

Повтори все проверки из handoff (Python suite на четырёх шкалах, rustfmt, `git diff --check`, YAML, `bash -n`, импорт bundle на shallow базе, сверка blobs и координат) и обнови в `REV2-N22-N25-CONSUMER-HANDOFF.md` раздел FIX1: новые commit/tree/parent Std/control/trigger, SHA-256 request/roster/bundle/bindings, diff от R1, результаты. Статус `READY_FOR_REVIEW`, `go=NOT_GRANTED`, `proof_credit=NONE`. CI, push, Actions variables, cargo/rustc/Kani/CBMC — не запускать. Коммиты с `[skip ci]`, без знака решётки перед цифрой.
