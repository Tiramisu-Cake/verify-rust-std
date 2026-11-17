W14: **U APPROVE; PFC APPROVE; S1-08 CHANGES_REQUIRED**. Composer w11 NOT_REVIEWED.

Продолжение после утверждения policy: FOLLOWUP.md / FOLLOWUP-VALIDATION.json.
Дополнительных concrete findings нет; original verdicts прежние, repair не принят.

Координатору → original S1-08 owner: finding **W14-S108-01 (P2/MEDIUM)**,
`s1-08/EMBEDDED-CI-REQUEST.json:258,294` / control `CI-REQUEST.json:258,294`.
Source `99e8456d...` переносит negative closure spans 100→95 и 106→101;
exact oracle IDs сохранили старые координаты. `prepare_package.py:75–81`
переносит лишь отдельное поле line; `verify_package.py:85–93` ошибку пропускает.
Matcher требует exact ID и отклоняет правильный relocated synthetic failure.

Исправить оба source-derived IDs либо сохранить исходные spans; регенерировать
source/control/request/payload/patch pins и regression для closure coordinates
внутри generic instance. Точные oracles не ослаблять. Нужен committed delta для
продолжения того же review. Сам авторский код reviewer не менял.

Полное обоснование и воспроизведение: REVIEW.md, REVIEW.json,
VALIDATION.json#/finding_reproducer; команда `python3 validate_review.py`.
Runtime/compiler/exporter/verifier/full runner/CI/push/ledger NOT_RUN.
U/PFC approval ограничен exact указанными components; independent B1/B2 и общий
sorting theorem не присвоены. Review не даёт dispatch GO или admission.
