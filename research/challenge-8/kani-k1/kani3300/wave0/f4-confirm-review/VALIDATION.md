Static/synthetic validation: **PASS**. Runtime: **NOT_RUN**.

Проверены exact candidate bytes (25 files), 12 payload files/modes, все source/profile/request/trace hashes, direct ancestry и patch reconstruction до exact control tree. Python AST, shell syntax, YAML и scoped Git whitespace checks прошли. Настоящий depth-three checkout exact control прошёл source preflight с shared reference objects; temporary checkout/index удалены.

Авторский `check_service.py` прошёл. Дополнительно проверены matching UNREACHABLE unsupported-class, stderr свыше 45KiB с первой/последней диагностикой и exit 73, сохранение TIMEOUT/SPAWN_ERROR/NOT_RUN, post-run source-stage mismatch → INCONCLUSIVE. Synthetic data подтверждает обработку сервисом, runtime F4 defect не устанавливает.

Повторить из `/root/kani-f4-confirm-w15`:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/wave0/f4-confirm-review/validate_review.py
```

Во время настройки проверки Git отклонил linked worktree как `--reference`; проверочный вызов исправлен на общий Git-каталог. Последний полный запуск PASS. Исходники кандидата не менялись. Compiler/verifier/full runner/CI не запускались; historical artifact повторно не получался, raw evidence не читалось.
