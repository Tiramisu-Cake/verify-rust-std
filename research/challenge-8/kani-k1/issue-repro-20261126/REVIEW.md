# Issue repro · ревью R1

**NO-GO**, блокер один. Ревьюер Claude (smallsort-reviewer, read-only), 2026-11-26. Пины: control `cdff77be85363b6096c8945791ab4868cfe65ade`, tree `2a461d31bc8558ea469c6d758979dbfcf4045eab`, review-trigger `844f093ad4`, g0 `d8c6a6ecc4`.

## Блокер

1. `.github/workflows/ch8-q-pilot.yml:21` ставит `ISSUE_REPRO_STATE: ${{ runner.temp }}/…` в `jobs.repro.env`. Контекст `runner` на уровне job env недоступен, GitHub отклонит workflow. Нужно убрать строку и в `run.py:83` брать `RUNNER_TEMP` из окружения. В `with:` у upload `runner.temp` допустим.

## Неблокирующее, исправить в том же FIX

2. `run.py:241-243`: SUCCESS-команды не требуют `checks > 0` и `cover SATISFIED`. Нужно требовать оба.
3. `ch8-q-pilot.yml:66`: лимит шага 20 мин меньше суммы лимитов команд (около 32 мин). Сводку писать по мере выполнения или уменьшить лимиты.
4. В боевом trigger не должно быть `[skip ci]`. Записать это в HANDOFF.
5. Черновик bool: фраза «same with and without `-Z valid-value-checks`» этим прогоном не проверяется. Координатор удалил её из черновика, блоки кода не изменились.
6. Actions закреплены тегами — тот же шаблон, что раньше.

## Проверено

Триггер и гейт, `permissions: contents: read`, секретов нет. Stock Kani 8c6dba5935 на собственном nightly-11-23, identity проверяется до и после сборки. Блоки кода побайтно совпадают с черновиками. Шесть argv без лишних флагов. Судья ожиданий строгий. Авторство в порядке. selftest и check_drafts — OK.
