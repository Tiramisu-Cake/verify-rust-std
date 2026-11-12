# KANI3300 B1PR — черновик описания upstream PR для B1 (только файл)

**Выдано координатором 2026-11-12 (ночь).** Runtime **Codex**, одна стадия, **Cloud $0**, без CI.
Kani: `/root/kani-fix-3300-b1`, ветка `fix/kani-uninit-unresolved-call` @ `d5f072f2bc` (5 коммитов на upstream `bf9c58e662`);
заметки `kani3300/b1/`, `kani3300/b1r/`, `kani3300/b1r2/`.

## Подтверждено исполнением

- Узкий fork CI (run 43110714635): все uninit-наборы PASS (kani 22, expected 83, ui 14, script 1).
- Полный Kani CI (run 43112332778): regression ubuntu-22.04 / 24.04 / 24.04-arm и macos-15-intel PASS; perf, llbc,
  docs, benchcomp PASS; macos-14 отменён (нет runner в форке).

## Что сделать

`kani3300/b1pr/PR-DRAFT.md` на английском, как PR в model-checking/kani:
- заголовок; что было не так (на `Err` от `try_resolve_instance` терялся весь target — операции, собранные до вызова, и
  entry loads; `Virtual`/bodyless формы проходили мимо обработки) с минимальным примером; что меняет патч (один
  `super_terminator`, сохранение собранных ops, явная классификация: bodyful shim как MIR callee, bodyless
  Shim/Virtual/LlvmIntrinsic → Unsupported с диагностикой); как изменилась диагностика существующих тестов (если менялась);
  тесты; раздел Testing с фактами выше (ссылки на runs форка — допустимы);
- ссылка на Kani issue #3300, если уместно; **без** ссылок на сторонние PR, без «Part 1», без внутренних путей/ID задач;
- последние строки: `*Disclosure: this change and description were prepared with AI assistance.*` и
  `By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.`
- Отдельно `kani3300/b1pr/COMMITS.md`: предложение, как сжать 5 коммитов в 1–2 с нейтральными сообщениями (не переписывать
  историю сейчас).

Независимое ревью текста на точность (каждое утверждение — по коду/CI). Research-коммит `[skip ci]`, push без force.
Последней строкой `B1PR READY <research sha>`, стоп.

## Запреты

- Никаких сборок/dispatch/Cloud/Actions/PR/issue/комментариев; push в Kani запрещён. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
