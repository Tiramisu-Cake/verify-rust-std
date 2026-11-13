# CC4: cycle provenance before a recursive-contract boundary

2026-11-13. Это верификация корректности, не security-работа. Только review/черновик/patch artifact;
source reference не менялся, сборок/CI/выдачи нет.
База CC3: `76a706f8f8c5b0471bd5c8e6b48cdaf45bab9b66`; CC2 `9631aaf89e869624fbfc8cd22d327ce194eb779d`;
CC1 `b2e1a392ad27bd21758473bc208ff66c2d7d0405`. Quick43453928092/166+2 и mode results — сообщение координатора.

## Рекомендация

**Не включать fallback к source panic-body register.** Он делает анализ отличным от реально исполняемой trampoline
и может потерять capture/return/alias edges, нужные не только setters, но и checks. «Так было upstream» не доказывает
консервативность: нельзя обещать только возврат false FAIL, возможна и потеря проверки. Fresh retry с очищенными graphs
и точным override selector исправляет механизм retry, но не это semantic возражение.

До корректного summary/SCC оставить fail-closed на реальном interprocedural cycle. Но название scope должно следовать
actual cycle, не наличию `#[kani::recursion]` или имени файла. Текущее “Ordinary calls ... are not affected” уже неверно.
Корректный принцип документации: если delayed-uninit analysis обнаруживает межпроцедурный цикл, root получает Unsupported;
это возможно и в ordinary proof/contract-check harness, runtime depth не ограничивает статический обход.
Такое описание не превращает любую неразобранную ordinary regression в принятую границу выпуска.

**Неожиданность, обязательная для CC4:** `recursive_simple_check` на CC3 вызывает `bounded_transfer`,
который source-рекурсии не содержит: depth0→relay, depth1→relay(relay). Саморекурсия есть только в recursive_transfer.
Нужен actual repeated Instance/selected-body/call-site path этого root. Он может идти через generated/helper bodies;
по одному имени нельзя приписать его recursive sibling или объявить helper неподдержанным рекурсивным контрактом.
ActiveCalls создаётся отдельно для каждого entry; source не показывает простого переноса active stack между roots.
Общий immutable overrides map и actual transformed body selection всё равно требуют проверки.

Если причина — неверный/mismatched mode body, исправлять точность выбранного реального body до UB instrumentation,
а не возвращаться к source panic. Если это настоящий необходимый цикл, затем решать summary/SCC либо явно согласованную
границу после representative verify-std inventory. Без этого SimpleCheck companion остаётся BLOCKED.

## Было ли переполнение на обычной рекурсии upstream

В exact upstream `bf9c58e662fd65c64381ef2ac97a6397ffc0693a` regular-call effect тоже рекурсивно запускает run;
active/SCC guard нет, `call_graph` только хранится/передаётся, не обрезает self-call. Поэтому при достижении
такого FnDef cycle delayed-UB analysis имеет тот же дефект завершения и без контрактов. CC1 устраняет этот класс краха.
Это установленный source finding, **не выполненный upstream reproducer**. У конкретного fixture могут отсутствовать
analysis targets/сохранённый recursive edge или сработать другой Unsupported; не заявлять фактический stack overflow
на upstream без matched probe. Такой probe optional и не причина задерживать безопасную diagnostic CC4.

## Два ожидания

`s3-compat/cc4/expectations.patch` меняет только2 .expected, не Rust inputs:
- capture-reference-legal → точный Unsupported из UnsafeCell<MaybeUninit<u8>>::new (до полезного closure path);
- capture-union-reference → точный Unsupported dereference on a union field в callback.

В указанном координатором `cc3-r1.log` целево прочитаны только диагностики/итоги этих2 fixtures:
3380–3383/4301–4312 и4881–4885/5509–5522. У обоих ровно1 failed check, не uninit-payload negative.
Это фиксация поддержанной границы, **не положительное свидетельство capture semantics**; первое вообще обрывается на
создании Cell до вызова closure. Сохранять отдельные простые ref/scalar positives и poisoned-payload negatives.
Исторические reports/CI statuses не переписывать и новый Quick PASS до запуска не приписывать.

Черновик `TASK-KANI3300-CC4-draft.md`, patch не применён к source clone; **NOT ISSUED**.
