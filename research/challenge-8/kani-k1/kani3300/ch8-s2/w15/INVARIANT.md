# CAP32 merge pilot v1

Domain: u8 + S1 KeyLess<u8>, штатный полный порядок, len symbolic2..32,
h=len/2, r=len-h. Runtime и comparator не зависят от arbitrary query q.
Состояние: k,i,j,ir,jr; i+j=k=ir+jr, i+ir<=h, j+jr<=r.
Все counters сначала ограничены CAP; затем арифметика/индексы безопасны.
C3/C4 — stable forward/reverse cuts из Приложения C; равные значения вперёд
берутся слева, назад справа. Два output bands sorted; endpoint alternatives
охраняются i/j/ir/jr>0. Для фиксированного q каждый band имеет ровно count
соответствующих consumed input segments. Этот q не подменяется на шаге/выходе.
Sortedness использует cuts/guarded endpoints; одного count для вывода порядка нет.

Все predicates развёрнуты на literal0..31, без symbolic-bound quantifiers и
циклов внутри checker. Они читают только typed initialized arrays. Halves и
valid geometry проверяются раньше индексных выражений; k=0 не читает endpoints.
Whole-source array32 всегда initialized; pilot destination32 тоже initialized.
Это representation pilot, НЕ proof uninitialized-memory/valid-value tracking.
Real-body merge32 отдельно использует именно MaybeUninit output с interior base1.

Base root: nondet src/dst,len,q, только lawful sorted halves; zero fronts.
Step root: произвольное (включая недостижимое) invariant-состояние плюс k<h.
Вызывает actual merge_up/merge_down, восстанавливает counters из фактических
returned pointers; проверяет invariant preservation, точные pointer equations,
read bounds и frame (два destination cells). Никаких assumed summaries.
До шага i,j,ir,jr<=k<h: четыре reads остаются внутри исходных половин.
Reverse bindings строятся только base.add(h-1).wrapping_sub(ir), аналогично right.
Sentinel перед началом не разыменовывается и не передаётся в offset_from/add(-1).

Exit root: arbitrary invariant state с k=h. Сумма remaining равна len%2.
Для even обе половины полностью consumed. Для odd ровно один remaining,
реальная pointer-comparison выбора last_src совпадает с remaining side;
выполняются actual ptr::copy и updates odd epilogue. Проверяется именно
left==left_end && right==right_end, то есть отрицание ord-panic guard;
далее whole-output sorted и count(q), отдельный source/odd-cell frame.
Covers включают обе стороны odd остатка, len31 и len32.

Loop pilot: собственный while с loop_invariant и explicit loop_modifies только
fronts + dst[..len]; использует те же actual helpers, затем тот же exit checker.
Это проверка выразимости/extraction и partial correctness такого цикла, НЕ
прикреплённый контракт actual bidirectional_merge for-loop. Base/step/exit и
loop-extraction receipts должны сохраняться отдельно; ни один не переносится
автоматически в core. Actual merge32 остаётся monolithic независимым root.

Termination не заявлена: основной pilot без loop_decreases. На pin0aac локальный
test decreases_with_modifies.rs прямо описывает #4585: сложный measure может
вычисляться до цикла. Отдельные simple-variable positive/constant false-decrease
controls проверяют механизм; #3168 — исторический API-контекст, не доказательство
фикса. Нельзя заменить variant expression на len/2-k и принять termination без
его отдельной квалификации. Bounded actual loop finite, но это не credit loop proof.

#5148: constant predicates обходят symbolic quantifier bounds; это ещё не sound
extraction evidence. Нужны false-invariant и false-frame controls. #5141/default
checks и pointer-definedness остаются gates; extra-UB OFF не значит все UB flags ON.
Combined-ON/произвольный T/F/alias/provenance theorem/stability не заявлены.
Query-count в nondet real-body root соответствует каждому u8 q, поскольку input,
компаратор и actual output от q независимы. Индукционный root с условным invariant
даёт только implication для того же q; это не unchecked universal summary.

Frame: monolithic src readonly, output32 в отдельной allocation34 с двумя guards;
pilot frame — actual helper writes + explicit loop write set. KeyLess закрытый ZST,
callback writes отсутствуют. Arbitrary FnMut с внешними writes не квалифицирован.
Geometry same-allocation offsets/scratch→v/v→scratch остаётся S3: N32/base1 не
закрывает34 offset pairs sort8 и не разрешает stub_verified(actual merge).
Все утверждения выше — obligation/design описания; proofs и costs NOT_RUN.
