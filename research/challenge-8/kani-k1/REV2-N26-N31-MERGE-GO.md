# REV2 N26–N31 merge · GO

**GO** на один диагностический Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`. Решение координатора 2026-11-26 по делегированному праву GO. Планер не смог оформить GO: оба запроса остановил контент-фильтр его среды. Ревью R1 сверило пины и хэши напрямую. [Ревью R1](REV2-N26-N31-MERGE-REVIEW.md) · [Handoff](REV2-N26-N31-MERGE-HANDOFF.md) · [Задание](REV2-N26-N31-MERGE-TASK.md)

- **Std** `71953c45a9a38cff3538c8a5e413890efc896d70`, tree `f59ea89d61b25e34f06f9b14d61ad48694b86950`, parent `ea34c58ab9`.
- **Control** `108c45668b1c8aa41a6f0ae228697a639ad54933`, tree `e4997c4c94ba6b0ce426f4e2fdbbb86c38de05d7`, parent `302604ce81`. Координатор повторно сверил tree и parent.
- **Trigger** — новый коммит без `[skip ci]` с tree `e4997c4c94…` и единственным родителем `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. Actions variable `CH8_REV2_N26_N31_MERGE_TRIGGER_TREE=e4997c4c94ba6b0ce426f4e2fdbbb86c38de05d7`.
- **SHA-256:**
  - request `013f4c377d46f0620fd4082bd2666b8faf716b40f89d72d9bc02e21a2802a9a9`;
  - bundle `6ccc000275fc9790184ee0b1bb04c130ac4955a927a786d7bf53eb46534e8ca6`;
  - roster `47cd94f3d07647f62ce26e0e0f1f8451545775e45d46f985a8f1759adbc059db`;
  - bindings `04b1c9ad8d84a83a3cfb6afee74d4a1af73b9e33f319f3ee200e59da56f70b0d`.
  Координатор повторно сверил request и bundle.
- **Ожидание.** `PROVIDERS_WITHIN_PROFILE`: восемь `VERIFIED` exit 0 `MATCHED`. Лимиты 4 GiB / 120 с VT / 180 с cold wall, job 120 мин.
- **Замечания R1 1–3** переносятся в задание на сквозной пакет N26–N31.
