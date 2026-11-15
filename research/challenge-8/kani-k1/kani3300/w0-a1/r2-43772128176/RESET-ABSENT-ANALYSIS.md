# A1 R2 — почему autoharness не имеет reset в immutable-mask модели

2026-11-16. Статический разбор; код, CI, сборки и push не выполнялись.
Это верификация корректности, не security-работа.

## Вывод

**Да, это реальный integration-дефект PR-02:** finalizer требует reset в каждом seeded model,
но существующий uninit entry-pass не распознаёт автоматически созданный harness. SEL1 лишь проявил
несогласованность; select-патч её не создаёт. Минимальное направление — включить automatic harness
intrinsic в распознавание входа и вставлять тот же reset до первого действия wrapper. Убирать fatal
или просто объявлять reset в symtab недостаточно: reset должен исполняться, создавая nondet witness.

## Наблюдение и точные источники

- [Curated RESULT](RESULT.md), fork run [43772128176](https://github.com/Tiramisu-Cake/kani/actions/runs/43772128176):
  исходный [autoharness fixture](../native/issue-4854-autoharness.rs) на SEL1 получил
  `error: immutable masks: reset is absent from this model`; explicit-proof companion — SUCCESS0/156.
  На stock0aac оба случая упали прежним ICE. Новый результат не означает полного исправления #4854.
- Читать объекты Git, не «текущий main»: PR-02 `932fb8395a58f8c86c0d702ba2cae835823b2962`,
  C2 `8e299aa6243bc5f06a29c51e98aafa9564478220`, SEL1 `14bc57fdb99960240c4944845a3d985c8af4dcf7`.
  Local source repo `/root/kani-fix-3300-c2-s6` checkout = freeze `ad499e41dd`, его tree равен C2.
  `immutable_allocations.rs` между этими тремя заданными commits **не меняется**; recognition/reset
  logic также одинакова. У upstream0aac уже есть тот же attribute-only recognition, но нет finalizer PR-02.
- Ни model artifacts/inventory, ни полные CI logs здесь не читались. Точная причинная цепочка ниже
  установлена по исходникам; имя конкретного allocation, создавшего seed в R2, пока не установлено.

## Где и при каком условии возникает ошибка

`kani-compiler/src/codegen_cprover_gotoc/context/immutable_allocations.rs`,
[PR-02, L214–292](https://github.com/Tiramisu-Cake/kani/blob/932fb8395a58f8c86c0d702ba2cae835823b2962/kani-compiler/src/codegen_cprover_gotoc/context/immutable_allocations.rs#L214):

1. `-Z uninit-checks` включён; finalizer seal-ит registry и сводит origins/bindings/statics.
2. После target checks есть хотя бы один **admitted nonempty seed**: Freeze-qualified whole immutable
   allocation, без relocations, mask ненулевой длины. При `seeds.is_empty()` здесь ранний return.
3. Marker `InitializeMemoryInitializationStateModel` **найден** в `queries.kani_functions()` и
   `Instance::resolve` **успешен**. Иначе были бы другие сообщения: `missing reset marker` / `unresolved reset marker`.
4. Но `self.symbol_table.lookup(reset.mangled_name())` возвращает None — **L287–289**, точный reported fatal.
   Это отсутствие symbol в данной модели, не отсутствие marker во всём kani crate, и не `reset has no definition`.

`prepare_immutable_allocations` (L151–168) только собирает typed origins из reachable MIR constants.
Finalizer (L377–382) дописывает seed statements перед normal returns **существующего** reset body;
ни prepare, ни finalize не добавляют reset-call в harness и не расширяют reachability автоматически.
`compiler_interface.rs` вызывает prepare после reachable-item collection, finalize после codegen/quantifiers
(PR-02 L99–140, L197–204; C2 L99–145, L202–209). Поэтому произвольный admitted constant в reachable code
может проявить проблему; по одному тексту fatal нельзя приписать seed именно MEMCPY_RET.

## Почему automatic отличается от explicit proof

Ссылки/номера ниже для C2; relevant logic в PR-02/SEL1 такая же:

| Участок | Что делает |
|---|---|
| `transform/check_uninit/ptr_uninit/mod.rs:54–64,81–98` | `UninitPass` вызывает `inject_memory_init_setup` только если DefId имеет `kanitool::proof` или `kanitool::proof_for_contract` |
| тот же файл `:100–138` | Вставляет настоящий вызов reset первым действием harness; не зависит от наличия `kani::any()` или числа пользовательских аргументов |
| `library/kani_core/src/lib.rs:661–665` | `automatic_harness` имеет `fn_marker = "AutomaticHarnessIntrinsic"`, **не** один из двух proof attributes |
| `kani_middle/codegen_units.rs:155–170,398–418` | Создаёт instances automatic intrinsic и отдельные codegen units/models |
| `transform/mod.rs:122–150` | `AutomaticHarnessPass` выполняется раньше `UninitPass`: последний видит уже созданное wrapper body, но recognition всё ещё проверяет исходный intrinsic DefId |
| `transform/automatic.rs:2385–2402,2486–2526` | Генерирует args и вызов target; memory-init reset не вставляет |
| `codegen_cprover_gotoc/compiler_interface.rs:441–458` | Вызывает codegen_items для каждого harness/model, не объединяет reset из соседнего explicit-proof model |

У исходного zero-arg target список generated `arg_locals` пуст. Это делает пример особенно коротким,
но **отсутствие kani::any не причина**: argument generation/`kani::any` вообще не является механизмом
вставки этого reset. Autoharness с аргументами подвержен той же structural omission.
В automatic contract wrapper есть `reset_clause_depth`/`init_contracts` (automatic.rs:2447–2483),
но это другой state/reset, не `InitializeMemoryInitializationStateModel`.

Обычные **явные** proof/PFC harnesses распознаются даже без any: reset становится reachable, что
согласуется с SUCCESS explicit companion. Прямой новый отказ для них не следует из этой находки.
Автоматический PFC wrapper остаётся automatic intrinsic даже если metadata называется ProofForContract,
поэтому также требует исправления recognition. Иные entry/export paths без proof attributes нужно
отдельно проверить, не объявлять автоматически покрытыми. Reachable explicit proof callee может случайно
притащить reset, но это не корректный substitute для reset на входе automatic wrapper.

## Узкое исправление и необходимые контроли

Рекомендую расширить `is_harness` в `ptr_uninit/mod.rs`: сохранить обе attribute-ветви и дополнительно
распознавать **ровно** `KaniFunction::Intrinsic(KaniIntrinsic::AutomaticHarness)` через существующий
`KaniFunction::try_from(instance)`. Тогда уже имеющийся enabled-only UninitPass вставит reset в начало
полностью generated wrapper **до** argument generation/contract setup. Marker enum/recognizer есть в
`kani_middle/kani_functions.rs:44–52,341+`. Это design recommendation, не скомпилированный патч.

Альтернатива — explicit reset injection в AutomaticHarnessPass при Uninit ON; она дублирует entry logic
и должна обработать все early-return branches генератора. Первый вариант меньше и использует общий путь.
Не ставить reset в target function/каждый callee: повторный reset уничтожает witness/transfer state.
Не seed-ить при каждом read, не считать dummy `MemoryInitializationState::new()` заменой reset:
`mem_init.rs:54–75` задаёт fixed dummy state, а `:237–248` выбирает object/offset nondeterministically.
Просто materialize reset без вызова либо silent skip seeds скрывает нарушенный invariant.

До признания исправленным нужен будущий fork CI, здесь **ничего не запускалось**:

1. Exact original #4854 autoharness на cumulative C2/SEL1 + неизменный explicit companion; no ICE/fatal,
   полезный legal outcome и наблюдаемый reset перед target. Proof companion не заменяет original mode.
2. Различающий PR-02-native repro **без MU/storage**: zero-arg target, возвращающий typed immutable
   byte-array reference, например `fn seed_only() -> &'static [u8;4] { &[1,2,3,4] }`.
   Сначала подтвердить emitted admitted seed/fatal на старом PR-02, затем SUCCESS после patch.
   Это предложение fixture: различимость/точный inventory ещё NOT_RUN; исходный #4854 на голове2
   может по-прежнему останавливаться прежним ICE раньше registry, пока нет storage-изменений головы4.
3. Auto с аргументом + immutable seed; auto no-seed; auto с контрактом. Не предполагать, что сообщение
   исчезнет только у zero-arg. Проверить ровно один entry reset, на всех путях до target.
4. Auto uninitialized-read negative + initialized companion: witness действительно nondet и hole ловится,
   а не только исчез fatal. Проверить absence of reset при Uninit OFF; explicit proof/PFC прежние PASS,
   immutable legal/hole/alias tests и function-contract suites не регрессируют.

## PR-02, текст и стек

Дефект проявляется **в коде среза2**, хотя сам пробел autoharness initialization унаследован от upstream.
Ревьюер может встретить его на PR-02 при Uninit+admitted immutable auto model; точный #4854 был проверен
пока только на SEL1, не выдавать его за различающий runtime-тест standalone PR-02. Старые зелёные regression
gates не являются проверкой этого отсутствовавшего сочетания flags/entry mode.

До подачи/обновления PR-02 рекомендую короткий исправляющий stage + targeted CI, с включением fix/регрессии в PR-02;
upstream entry-reset prerequisite отдельным patch тоже возможен, если мейнтейнер предпочитает разделение.
PR-01/#5172 не переписывать ради registry. Heads2–7 и SEL1 после переноса fix потребуют новых identities
и review/проверки затронутых gates; старый freeze tree останется историческим, новый delta задокументировать.
Никакого force/rebase/push из этой записки: способ пересборки решает координатор с владельцем.

В PR-02 после **подтверждения** fix добавить: reset setup для generated automatic harnesses перед
immutable seeding; Testing — matched старый/новый PR-02-native test и cumulative #4854 отдельно,
точные новые SHA/run. До этого честно отметить known automatic-harness build rejection и не писать
«autoharness/#4854 fixed». Утверждение «after reset» сейчас описывает замысел seeding, не выполненный
invariant для всех entry modes. PR-02/PR-01 тексты этой сессией **не менялись**.
