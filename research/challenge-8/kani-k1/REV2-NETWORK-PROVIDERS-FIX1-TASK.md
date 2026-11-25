# REV2 · провайдеры sort13 и merge · FIX1 после ревью

Закрой два блокера ревью новым локальным коммитом поверх control `bccbabf84d77fbc227862b5650baab506f3f580f` в `/root/kani-rev2-network-providers-control-w11`. Rust-корни, std, roster, пины, caps и окна прошли ревью и не меняются. [Ревью](REV2-NETWORK-PROVIDERS-REVIEW.md) · [Задание](REV2-NETWORK-PROVIDERS-TASK.md) · [Handoff](REV2-NETWORK-PROVIDERS-HANDOFF.md)

1. **Ожидаемый tree из независимого источника.** Используй прецедент fallback control: workflow передаёт в guard значение переменной Actions `vars.CH8_REV2_PROVIDER_COST_TRIGGER_TREE`, которую координатор задаёт перед push полным 40-символьным tree проверенного trigger. [Прецедент](/root/kani-rev2-fallback-control-w11/ch8-cal1/fallback_request.py:114) · [Workflow прецедента](/root/kani-rev2-fallback-control-w11/.github/workflows/ch8-q-pilot.yml:20)
   - `check_trigger` и `identity` сравнивают tree checkout с этим значением.
   - Отсутствующее, пустое или не 40-символьное hex значение — отказ.
   - Trailer `REV2-Control-Tree` и любое значение из проверяемого `HEAD` источником ожидаемого tree не считаются.
   - Регрессия на фактическом entry point:
     - fork, event, ref, attempt и sole parent верные; дерево изменено вместе с trailer → отказ;
     - переменная отсутствует → отказ;
     - совпадающее значение → допуск.
   - Отказ trigger guard по-прежнему ничего не публикует.
2. **Дедлайн слота включает работу с receipt.**
   - Телеметрия, `results.project`, сериализация и атомарная запись обязательных полей завершаются до дедлайна слота. Для этого заранее выдели окно, урезай или откладывай необязательную проекцию.
   - Если запись всё же закончилась позже, receipt фиксирует фактическое время и флаг превышения. Outcome при этом не переписывается.
   - Удаление cold target не должно съедать окно следующего слота. Перенеси его за пределы цепочки слотов или ограничь временем.
   - Регрессия: измерения стартуют у границы 45-минутного setup, три слота дают `TIMEOUT` с подтверждённым reap и медленной (16 с) проекцией. Четвёртый слот обязан стартовать.
   - RSS-стоп, guards, подтверждение reap и остановку после `REAP_UNVERIFIED` не ослаблять.

## Handoff

Обнови `REV2-NETWORK-PROVIDERS-HANDOFF.md`:
- новые control commit и tree, будущий trigger tree;
- хэши request и bundle (если изменились);
- diff `bccbabf84d..<новый>`;
- результаты Python suite, `git diff --check`, YAML и `bash -n`;
- синтетические проверки по двум пунктам.

Статус пакета: `READY_FOR_REVIEW`, `go=NOT_GRANTED`, `proof_credit=NONE`. Cargo, rustc, Kani, CBMC, CI и push не запускать. Коммиты с `[skip ci]`, автор Tiramisu-Cake <igkharin@gmail.com>, без знака решётки непосредственно перед цифрой в сообщениях.
