# PROF-OFF-02 intake handoff

Одна стадия завершена. Содержащий этот пакет g0 commit — итоговый g0.
Control fix: `112fcc9ada67ee2bb8e1712d47983d6717487b78`;
tree `b8751524e6be94edb9c69c88c11c1734ed5a89f4`, sole stock parent
`0aac16ef62da9e9d5645782d458593e5d78143ba`.
Worktree `/root/kani-ch8-prof-off-intake-w11`, branch `work/ch8-prof-off-intake-control-w11`.
Исходный control worktree не изменён.

Runner исправляет только формат profile target binding. `control-delta.patch` — delta от `741b7183b4`, формат `--unified=0`; применять с `git apply --unidiff-zero`.
В отдельном temporary Git index patch точно восстановил fixed tree.
Review-only descendant `0089c0f2f8190ef1bb84011295e6a304fcdd8a00` имеет ту же tree;
его baseline — `741b7183b4d6e9d752c0b7951206d7257f69f951`.
`REVIEW.json`, `review-spec.json`, `review-packet-metadata.json`, `VALIDATION.json` фиксируют identities и GO.
Review packet в scratch `/tmp/ch8-prof-off-intake-w11/review`; его воспроизведение:
`smallsort-session review create --spec <этот каталог>/review-spec.json --out <новый scratch каталог>`.

Offline replay (только Python/JSON; команды из evidence не исполняются):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 reclassify.py \
  --zip /tmp/ch8-prof-off-intake-w11/artifact.zip \
  --control /root/kani-ch8-prof-off-intake-w11 \
  --output /tmp/ch8-prof-off-intake-w11/replayed.json
```

Артефакт и run metadata сохранены в `artifact-metadata.json` / `run-metadata.json`.
ZIP digest проверен. JSON evidence читалось из ZIP, logs не читались и не копировались в g0.
Исторические receipts, ledgers и prior packages не переписаны.

Итог: Kani 53 SUCCESS + 9 FAILURE, verdict/oracle 62/62; covers 189/189 SAT.
После fix classifier: 9 EXPECTED + 53 UNKNOWN; independent acceptance PENDING, proof credit NONE.
Дефект binding устранён, но inventory acceptance не изменена; пять consumers остаются заблокированы leaf.
До дальнейшего admission отдельно разобрать unreachable/unsupported inventory в рамках текущих гарантий,
связать generated frame property и mangled wrappers; raw verdict нельзя автоматически считать acceptance.
Эти действия находятся за пределами выполненной одной стадии. Нового CI не запускалось.

READY containing-g0 112fcc9ada67ee2bb8e1712d47983d6717487b78
