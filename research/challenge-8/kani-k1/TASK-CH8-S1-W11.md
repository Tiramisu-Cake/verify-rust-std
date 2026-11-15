# CH8 S1 — worker11: KeyLess и чистая модель сортировки

2026-11-16. Одна сессия, затем handoff интегратору13. P0 принят владельцем.
Это верификация корректности, не security-работа.

## 1. Контракт стадии и точные входы

Подготовить verification-only модель для настоящих generic trait methods, не меняя их runtime bounds.
S1 проверяет механизм на N0..3; threshold16/32 и полный домен остаются целью S3/S4.
Основание: `PLAN-CH8-ITEM2-SORTING-v2.md` §§2–4, `ROADMAP-CH8-ITEMS1-2-FOUR-WORKERS.md`,
`TASK-CH8-S1-W13.md`, единый `CH8-DISPATCH-LEDGER.md`. Прочитать действующие root/project AGENTS.

- Std S: **`872d5a43380752786415bc00d2a12ce0e930cb37`**, tree **`384023c2f80a04d0618aa7ce971b1419494b062b`**.
  Это исходный #752, не std70ba+6075 из A1.
- Kani S: чистый upstream **`0aac16ef62da9e9d5645782d458593e5d78143ba`**,
  tree **`9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`**. C2/SEL1 patches запрещены.
- Создать только std worktree из существующего `/root/verify-rust-std`:

  ```sh
  git -C /root/verify-rust-std worktree add -b work/ch8-s1-model-w11 /root/verify-rust-std-ch8-s1-w11 872d5a43380752786415bc00d2a12ce0e930cb37
  ```

  Работать в `/root/verify-rust-std-ch8-s1-w11`. До создания проверить object, свободное место,
  `git worktree list`, отсутствие destination/branch. Существующий путь не reset/clean/stash/remove:
  использовать только после проверки согласованного SHA, чистоты и владельца, иначе STOP координатору.
- Общий Kani worktree `/root/kani-upstream-ch8-s1` создаёт **только13** из
  `/root/kani-fix-3300-c2-s6` на exact0aac; worker11 читает его или `git show` exact object в source repo.
  Не создавать второй Kani checkout, не переключать чужой HEAD. Полные clones, копии `.git`/target,
  submodule/toolchain setup и загрузка бинарников запрещены в этой сессии.

Никаких локальных cargo/rustc/Kani/CBMC/Miri/build/rustfmt запусков. Допустимы Git, чтение и небольшие
Python synthetic checks моделей/manifest без компилятора; это не Rust/Kani qualification. Только fork CI
координатора, Cloud $0; worker не push/dispatch/publish. S1 имеет **общие1–2 dispatch**, не по2 каждому worker.

## 2. Владение файлами

Все source paths ниже относительно `library/core/src/slice/sort/shared/smallsort/verify/`:

- новые **`sorting_model.rs`** и **`sorting_model_controls.rs`** — только worker11;
- не менять `smallsort.rs`, `verify.rs`, lib.rs/Cargo/check-cfg, tool_config, старые models/profiles,
  `sorting_entry_smoke.rs` и `sorting_entry_controls.rs` — интеграция/регистрация принадлежит13;
- future leaf modules не реализовывать в S1. Не править `verify/merge.rs` и старый FnPtr comparator.

Research в g0: только `research/challenge-8/kani-k1/kani3300/ch8-s1/w11/`.
Общий API и manifest предложения передавать в `INTERFACE.md` этого каталога; worker13 ведёт принятое
`kani3300/ch8-s1/integration/INTERFACE-ACCEPTED.md`. Не редактировать область13 или ledger параллельно.

## 3. Интерфейс11→13: сначала согласовать, затем реализовать

Семантический интерфейс фиксируется здесь; точную Rust specialization syntax и минимальную visibility
предложить13 до интеграции. Нужен unconditional facade для **любых** исходных `T,F`, включая типы,
которых модель не поддерживает. Пример ожидаемых имён/сигнатур:

```rust
KeyLess<T>::new() -> KeyLess<T>
NonCopyByte::new(value: u8) -> NonCopyByte
enabled::<T, F>() -> bool
snapshot::<T, F>(values: &[T]) -> Snapshot
post::<T, F>(before: Snapshot, values: &[T]) -> bool
```

- `KeyLess<T>` — закрытый именованный ZST, без function-pointer coercion/address guards.
  Реальные FnOnce/FnMut (`extern "rust-call"`) сравнивают чистые проекции двух ссылок штатным `<`.
  PhantomData допустим; capture/state/побочные записи запрещены. Fn feature gates в core включает13.
- Поддержанные пары ровно `(u8, KeyLess<u8>)`, `(Cell<u8>, KeyLess<Cell<u8>>)` и
  `(NonCopyByte, KeyLess<NonCopyByte>)`. NonCopyByte — transparent u8, Freeze, **без Copy и Drop**.
  Cell !Freeze; его projection только `get()`. Перечислить size/auto-trait/specialization ожидания.
- У внутренней проекции Copy требуется от **Key**, не от T. Для трёх текущих моделей Key=u8 и
  представляет полный logical value, а не сжатый ключ. Не добавлять T:Copy/Ord к реальным методам.
- Фасад допускает blanket inactive fallback + закрытые specialization. Для произвольного T/F
  `enabled=false`, snapshot не разыменовывает и не читает values, post не вызывает comparator.
  Ни один helper не требует нового bound от generic caller. Если core specialization этого не принимает,
  STOP с узким source repro; не подменять API FnPtr либо runtime-ограничением F.
- `Snapshot: Copy` — собственные значения и исходная длина, ёмкость **32**; копировать лишь initialized
  active prefix. Никакого `old(&slice)`, ссылок на изменяемый input, чтения scratch/unused tail/Cell после
  мутации вместо снимка. Для inactive fallback вернуть явный invalid token без чтений.
- Активная модель охватывает N0..32; S1 harness квалифицирует только0..3. Нельзя спрятать длинные N
  через `enabled = len<=3` и назвать threshold-постусловие полным. Для len>32 snapshot/checker должны
  безопасно отвергать активный запрос, не truncate и не panic в spec.
- `post` при active=true проверяет валидность снимка, неизменность len, adjacent sortedness и
  **полные кратности всех logical values**. Invalid snapshot/overflow для active модели → false,
  не benign true. У inactive модели guard в контракте явно выключает semantic claim.
  Подход count по всем distinct входным values при равной длине допустим с обоснованием; один
  выбранный fixed probe не полная multiset specification реального метода.
- Checker — чистый, без allocation, FnMut-вызова или предположений о sortedness. Для будущих payload
  моделей ключ и full value потребуют раздельного учёта; S1 ничего такого не утверждает.

Набор функции/API не менять молча после handoff. При borrow/old capture конфликте13 может предложить
raw-span adapter с доказанной геометрией; семантика, inactive read-free путь и snapshot остаются теми же.

## 4. Activation и отрицательные контроли

Подготовить exact selectors/oracles в `sorting_model_controls.rs`;13 регистрирует их под
`cfg(all(kani_smallsort_sorting, kani_smallsort_controls))`. Не вводить failing roots в ordinary inventory.

1. Позитив: три пары `enabled=true`, и identity/constructed sorted-permutation checker SUCCESS на
   N0/1/2/3, включая arbitrary duplicate bytes. KeyLess реально вызывает две корректные проекции.
2. Неверный comparator **другого типа**, включая descending/effectful closure, даёт enabled=false;
   negative root, требующий enabled=true, имеет именованный activation failure. Это отказ принять
   неподдержанную модель, а не доказательство сортировки чужим F.
3. Неподдержанный T тоже inactive. Не вызывать такой KeyLess и не читать невалидные storage ради контроля.
4. Order corruption: snapshot [a,b] с a<b, checker на [b,a] отвергает порядок при сохранённых кратностях.
5. Count corruption: snapshot [a,b], a<b, checker на [a,a] остаётся отсортированным, но отвергает
   кратности. Контроль не должен «проходить» за счёт отдельного order failure.
6. Guard/snapshot corruption: active invalid token не принимается; inactive path не разыменовывает
   переданный span. Не конструировать заведомо invalid Rust reference для доказательства отсутствия чтения.

Для4/5 один позитивный companion с тем же checker; negative asserts именно нужное ложное свойство
и ожидает именованный verifier failure. Если несколько проверок слились — изменить **fixture** для
однозначности, не угадывать будущий property ID. Названия/counts связываются с CI inventory, не с
совпадением общей подстроки SUCCESS. Native Python примеры не заменяют эти roots.
Контроли actual ensures attachment (default+override), шесть PFC и полезная return reachability — задача13,
в том же S1 CI batch. Отдельный model-only dispatch не разрешён.

## 5. STOP, handoff и критерий завершения

STOP: несовместимы generic-false facade/специализация/Fn ABI; нужна правка compiler/runtime или чужих
файлов; нет неизменяемого value snapshot; число/тип тела не совпадает с заявленным; обнаружен доступ
к unsupported/mutable model data. Сохранить минимальный source/типовую причину для P1, не открывать
новый Kani-трек и не ослаблять enabled/post.

В `kani3300/ch8-s1/w11/`: INPUTS с tree/parents; INTERFACE; MODEL-SCOPE с T/F/N; CONTROL-MAP с
selectors, expected failure/reachability и companions; TYPE-REVIEW (типы/width/conversions/Fn lifetimes);
локальный source commit/patch/hash, список необходимых registration/features для13; VALIDATION со
статическими/synthetic результатами и явным Rust/Kani NOT_RUN.
Не заявлять «шесть тел доказаны» после создания модулей. Приёмка механизма — только combined export
worker13 на exact clean pin после CI координатора и review P1.

G0 research worktree общий: согласовать короткое commit-окно с координатором/14/13, проверить index,
stage только свой w11 path. При чужих staged files STOP до освобождения index; не commit/reset чужое.
Локальный source commit содержит только два разрешённых новых файла от std872d; research commit —
только w11 scope, оба `[skip ci]`, author/committer `Tiramisu-Cake <igkharin@gmail.com>` через per-command
`git -c`, без Co-Authored-By. Без push. Завершить `READY <research-sha> <model-source-sha>` и путём INTERFACE.
