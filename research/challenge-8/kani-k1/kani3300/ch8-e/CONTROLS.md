# E — калибровка и oracles, всё NOT_RUN

Это план следующей отдельно разрешённой стадии, не CI request/dispatch permission.
Сейчас только source inspection. STOP E уже найден для quantified-pointer ON
кандидата; не расходовать proof batch на полный insertion до решения этого gate.

## Минимальный reproducer отказа

Калибровочный отдельный Kani файл (здесь текст, локально не компилировался):

```rust
#![feature(stmt_expr_attributes)]
#![feature(proc_macro_hygiene)]

#[kani::proof]
fn e_quantified_pointer_on_gate() {
    let values = [1u8, 2];
    let p = values.as_ptr();
    let mut remaining: usize = 1;
    #[kani::loop_invariant(kani::exists!(|i in (0, 2)| unsafe { *p.add(i) == 2 }))]
    #[kani::loop_modifies(&remaining)]
    #[kani::loop_decreases(remaining)]
    while remaining != 0 {
        remaining -= 1;
    }
    kani::cover(remaining == 0, "E quantified pointer loop returns");
}
```

Flags: `-Z loop-contracts -Z quantifiers`; ON добавляет `-Z uninit-checks`,
OFF его не имеет. Для constant bound SAT достаточно. Ожидаемый ON отказ по
`quantifier predicates containing safety checks ...` задан guard в
`U:kani-compiler/src/codegen_cprover_gotoc/overrides/hooks.rs:1267,1337`.
Изолированный predicate `exists!(|i in (0,2)| unsafe { *p.add(i)==2 })` совпадает
с документированным pointer witness `U:docs/src/reference/experimental/quantifiers.md:44`.
Если loop macro даст другой diagnostic, сначала изолировать этот witness.
Фактический compile exit ещё UNKNOWN; ожидаемый refusal — не recorded run.
Этот `[u8;2]` — diagnostic, не arbitrary-length theorem.

Связанный существующий issue: [#5141](https://github.com/model-checking/kani/issues/5141)
(из локального плана §5: checks в quantified predicates). Текущий online status
не проверялся; новая issue/comment не публиковались. Exact new diagnostic и
MRE attach — владельцу после отдельно разрешённого запуска. Не требовать удалять
guard: он предотвращает потерю checks, а не является дефектом проверяемого std.

## Порядок и минимальная матрица

S=SEL1 и P′ pins — из DESIGN. Все rows получают S/OFF и S/ON companions;
U/OFF отдельно показывает baseline, без смешивания identities. Valid-value-checks
OFF/ON фиксировать отдельной осью; первый ON — uninit ON, остальные default checks
сохранены. Дополнительный valid-value ON не заменяет uninit ON.

| ID / root | Минимальный construct | Oracle |
|---|---|---|
| E-Q | Приведённый raw-pointer quantifier + false-quantifier mutant | ON refusal ⇒ STOP encoding. OFF положительный root обязан завершиться; false predicate обязан fail утверждение/base, а не пройти. Unsupported/dropped predicate никогда не PASS. |
| E-S | `kani::any_slice_mut_unbounded::<u8>()` в alloc-enabled diagnostic; symbolic len без CAP; arbitrary valid index прочитан до loops | ON legal-read SUCCESS + reachable covers len>32, interior index, return; проверить actual generator/layout/target binding. Это ещё не core proof. Если core root выбрал bounded fallback/нет модели ⇒ STOP storage, без подмены CAP32. |
| E-L | Actual insert_tail на маленькой геометрии `[u8;4]`, k=1..2; direct comparator реально читает оба аргумента, возвращает arbitrary bool; inner attrs из proposal | Named base, step, assigns, live decreases и все default/ON memory checks SUCCESS; covers initial false, shift до begin, comparator false после сдвига, repair и return. Бounded diagnostic, не E theorem. |
| E-B / E-I | Отдельно сломать base relation guard.dst=sift+1; отдельно оставить верный base и false step (например неизменность initial dst) | E-B fails named loop_invariant_base; E-I — loop_invariant_step после reachable shift. Other compile error/timeout не засчитывать. Не заменять invariant на assume. |
| E-F | Сохранить locals frame, сузить data frame так, чтобы actual copy писал вне него; отдельно alias к excluded destination/sentinel | Named loop assigns/write inclusion FAILURE при реальной записи. SUCCESS ⇒ STOP frame; общий unrelated failure не подтверждает sound frame. Повторять на exact MIR opt setting intended proof. |
| E-D | Непосредственно читаемый ghost rank, связанный с pointers; mutant rank не меняется на reachable back-edge | Positive live decreases SUCCESS; stale/constant rank mutant — named decreases FAILURE. Measure computed-once warning ⇒ непригодный encoding, не доказательство termination. |
| E-H | Малый `MaybeUninit<u8>` region с live byte и заранее false byte, плюс отдельный outside sentinel. Loop writes только объявленный live byte; aliases к обоим; fixed tracked witness | Legal read live byte после havoc — ON SUCCESS. Read unwritten/false byte — ON uninit FAILURE, включая alias; outside sentinel payload/shadow сохраняются. OFF uninit-read outcome не oracle initializedness. Ошибка assigns на shadow write тоже blocker, не повод расширить frame на весь shadow. |
| E-R | Actual hole/guard repair: read tmp и разрешённых элементов перед/после abstracted iteration; обе break edges; actual Drop. Отдельный subfixture actual CopyOnDrop с initialized src и физически uninit MaybeUninit destination | ON legal reads после repair SUCCESS. В subfixture пропустить Drop и прочитать destination — ON uninit FAILURE. Это не вызов insert_tail с нарушенным requires. Пропуск repair после одного ptr::read может остаться незаметным по shadow: такой negative требует также ownership/Drop oracle. |
| E-P | Отдельный comparator panic после хотя бы одного shift, actual cleanup/Drop, без panic stub | Проверенный cleanup restores region; различать expected panic и UB/double-drop. Если pin/root не поддерживает unwind — NOT_ESTABLISHED, нормальный return не расширять на unwind. |
| E-O / E-Z | Actual outer while с доказанным inner route; symbolic valid offset, включая offset=len. ZST — отдельный typed root | Outer base/step/frame/decreases + fully-live post SUCCESS; covers offset=len, offset=1, несколько outer steps, return. ZST: ноль comparator calls; direct insert_tail ZST negative отклоняется requires. |

На E-H добавить complementary варианты: (1) havoc legal region и сохранение fixed
witness; (2) unwritten byte **внутри** modified region не становится initialized
без доказанного summary; (3) false bit **снаружи** region сохраняется через alias;
(4) actual write и copy из initialized source делают destination readable.
Тот же протокол нужен для возможной Replace summary, с arguments/return отдельно
и с normal-return-only границей. Ни один helper не должен вручную выставлять shadow
true/вызывать unchecked init summary ради положительного результата.

При E-S сначала отделить генерацию storage от insertion. Модель требует alloc
и отсутствует в core::kani. В actual core roots нет права молча импортировать этот
путь или переносить результат копии алгоритма. Для общего T отдельно validity и
padding; `u8` legal memory не квалифицирует struct/Drop/ZST. Для all-length actual
E-L/E-O fixture заменить **только после** доказанного E-S binding на uncapped slice;
не ставить `kani::unwind` на целевые inner/outer loops. Инициализация fixture также
не должна скрывать bounded loop/CAP. Covers len>32 проверяют отсутствие очевидного
ограничения, но сами по себе all-length theorem не устанавливают.

Direct-ZST negative запускать только с активной проверкой requires и требовать
именно precondition FAILURE; отключённый contract check не даёт нужного oracle.

## Resource/cost gate

План исполнения: jobs=1; organizer default checks и `--object-bits 12`; exact argv,
solver/version, MIR opt level, cfg, target, generated root и PFC/Original mode в receipt.
E-Q/E-L/E-H сначала на SAT constant-size diagnostics. Для symbolic `forall (0,len)`
SAT не годится: отдельный pinned Z3 preflight, затем matched roots и те же checks.
Наличие Z3/работоспособность driver здесь UNKNOWN; смена backend — отдельная калибровка.

Оценка до запусков: scalar rank/base и малый bounded frame — малые по размеру
формулы; quantified ON может отказать ещё на compile stage. Это не измеренная
стоимость. Symbolic heap + nested loops + shadow/quantifiers — высокий риск
driver RSS/solver timeout; обещать укладывание в **600 s / 6 GiB на root** нельзя.
Полезная декомпозиция — сначала inner actual body/repair, затем outer composition
с **доказанной** совместимой summary, не assumption. Уменьшение fixture до32 не
является исправлением arbitrary-length proof.

При исполнении отдельно записывать compile/driver/goto-instrument/CBMC time,
полный root elapsed, solver VT и peak RSS каждого процесса/совокупный peak;
единицы 6 GiB=6,442,450,944 bytes. Full-root time и VT не отождествлять.
600 s/6 GiB, missing named checks/return, Unsupported/dropped invariant, неверный
frame negative, утрата/подделка init shadow, compile blocker или CAP ⇒ STOP E
для текущего кандидата с точным первым blocker. Не повторять весь sweep.
Runs/measurements этой стадии: **0**, cost: **UNKNOWN**, proof credit: **NONE**.
