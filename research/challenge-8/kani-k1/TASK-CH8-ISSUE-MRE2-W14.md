# TASK — worker14: MRE v2 для slice havoc (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Итог run 43830763471 (clean upstream 0aac; artifact распакован read-only:
/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/mre/art):
- valid-value: copy_integer — ровно один failure `copy_nonoverlapping::<u8>.unsupported_construct.1` (как ожидалось);
  bool-контроли — Unsupported. Готово, повторять не нужно.
- slice havoc — НЕ воспроизведён, MRE негоден для upstream:
  1) все три *_check_slice_havoc: compile error «stub_verified requires activating the unstable stubbing feature»
     (в argv нет `-Z stubbing`);
  2) все *_check_body и actual_uninit_read: upstream не поддерживает uninit-проверку `[MaybeUninit<u8>; 2]`
     («contains union ... as a field») и raw ptr + union. Это то, что чинит наш C2 (#5151); в issue про upstream
     такой MRE не годится.

Сделать MRE v2 только для slice havoc на чистом 0aac:
1. Неинициализированный буфер без union: например `std::alloc::alloc(Layout::array::<u8>(2))` (raw *mut u8),
   modifies = `ptr::slice_from_raw_parts_mut(p, 2)`; body пишет через `p.add(i).write(..)`; dealloc в конце.
   Варианты: исходный (slice target), инициализированный буфер, thin targets (p, p.add(1)),
   отрицательный контроль настоящего чтения неинициализированного байта из того же alloc.
2. Флаги: `-Z function-contracts -Z uninit-checks -Z stubbing` (+ export), всё остальное по умолчанию.
   Заранее объявить исход и oracle для каждого harness; ожидание для slice_havoc — именно
   `write_any_slice` safety_check «Reading from an uninitialized pointer of type `*mut [u8]`».
3. Тот же kani-host шаблон (parent 0aac, только workflows + control dir; сообщение [skip ci]; новый trigger-префикс
   uninit-ci/ch8-issue-mre2-*). Synthetic tests, review. Обновить MRE-B-slice-havoc.rs только как новый файл v2.
4. g0 kani3300/issue-mre2/: CI-REQUEST, REVIEW, HANDOFF. Коммиты [skip ci], author Tiramisu-Cake <igkharin@gmail.com>.
   Последней строкой READY <control> <g0> или STOP <причина>.

Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC. Тексты issue не менять.
