# Slice havoc MRE v2 — подготовка одной стадии

Control: `/root/kani-ch8-issue-mre2-w14`, branch `uninit-ci/ch8-issue-mre2-w14`.
Commit `47616f4105697ae3b6bc9a2203b53ccdf69168df`, tree
`4700ee944e19804dd4d7374a6635754044f9c1a3`; единственный parent — чистый upstream
`0aac16ef62da9e9d5645782d458593e5d78143ba`. Author
`Tiramisu-Cake <igkharin@gmail.com>`, сообщение `[skip ci]`.
Изменены только `.github/workflows/` и `ch8-issue-mre2-control/`;
stock workflows удалены, tool/model/std не менялись.

4 файла / 7 отдельных exact-harness вызовов. Во всех буферах —
`alloc(Layout::array::<u8>(2))`, raw `*mut u8`, без union/MaybeUninit.
Body пишет два байта через `p.add(i).write`; на завершении — `dealloc`.
При null harness возвращается без чтения; assumptions не добавлены.
Варианты: slice target, предварительно записанные два байта, thin targets
`p` и `p.wrapping_add(1)` (равен `p.add(1)` для этого live allocation).
Настоящий negative control читает неинициализированный байт `read_volatile`
из такого же allocation; постороннего value assertion нет.
Unsafe initialize имеет документированное требование live/exclusive allocation;
это конкретные diagnostic harnesses, не общий theorem для произвольного pointer.

В rows.json до запуска объявлены 5 SUCCESS и 2 UNINIT_FAILURE.
Для исходного check_slice_havoc ожидается именно safety_check в
`write_any_slice`, description:
```
Undefined Behavior: Reading from an uninitialized pointer of type `*mut [u8]`
```
Для actual_uninit_read — safety_check с description про `*const u8`.
FAILURE с иным function/class/description либо посторонними failures
не засчитывается. Generated IDs/locations пока неизвестны; runner сохранит
полный failure inventory, argv/cwd, оригинальные exits/errors и snapshots.
Все строки используют `-Z function-contracts -Z uninit-checks -Z stubbing`
плюс JSON export transport; остальные Kani настройки по умолчанию.

Новый source MRE — `../ch8-profiles/on-ci/gaps/MRE-B-slice-havoc-v2.rs`,
byte-exact с control fixture. MRE v1 и тексты issue не изменены;
valid-value результат run43830763471 не повторялся и здесь не переоценивался.

31 offline synthetic/static tests и actionlint1.7.7: PASS; frozen package,
sole-parent/scope и patch reconstruction проверяются `audit_static.py`.
Review и точные hashes/pins находятся в REVIEW.md и CI-REQUEST.json.
External caps сохранены: build720s, row30s, phase330s, job30min, RSS6GiB;
они не гарантируют завершение. Fallback сохраняет исходные receipts,
незапущенные строки NOT_RUN, неполные UNKNOWN; artifact исключает target/.

Следующая стадия требует отдельного поручения: coordinator может подготовить
same-tree sibling без skip-ci, с тем же единственным upstream parent, новой
веткой `uninit-ci/ch8-issue-mre2-*`, attempt1. CONTROL.patch восстанавливает tree.
Текущий пакет не разрешает dispatch, push или публикацию.

Push/CI/publication/ledger и локальные cargo/rustc/Kani/CBMC не выполнялись.
Runtime ALL_NOT_RUN; proof obligations closed0; proof credit NONE.
