# REV2 N26–N31 consumer · GO

**GO** на один диагностический Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`. Запуск после завершения прогона `45870184232` на `refs/heads/uninit-ci/ch8-q-pilot-v1`. Пакет содержит 12 слотов, пара N31 идёт первой. Лимиты на корень — 120 с VT, 180 с cold wall и 4 GiB group RSS. [Ревью R1](REV2-N26-N31-CONSUMER-REVIEW.md) · [Handoff](REV2-N26-N31-CONSUMER-HANDOFF.md)

- Std `50609bb850c64080aedd74c00c9865dcae1ce74b`, tree `c2e93c566512c45179ab015b55835167eefc6191`.
- Control `a02a710c0c1206459d924c7467c9092b6921c674`. Локальный review-trigger `1d33084054113a4f1f319788e88ba4eda9d04047` подтверждает тот же tree.
- Trigger tree `7a92427bc3e81e99016536ee6ef87dd761eb7f3a`, единственный parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. Actions variable `CH8_REV2_N26_N31_CONSUMER_TRIGGER_TREE=7a92427bc3e81e99016536ee6ef87dd761eb7f3a`.
- SHA-256 request `6ab5d9e821fa55710be3cda6202bf147aed7d6c2db364ee9cef5688665fa8e02`, roster `b6709c5d920e4ac4621fc10e6a4a3056a7fa7c52ca6b9ff8d399eb04e45129dc`, bundle `d7c197c2e3c2fda043720970fc37a57fb249fb2bb6df4c48eb3416115b683ff6`, source bindings `e808404160a4d5451d0b2ab52775abc4e8d77d18dd64d7ce47f4b6192e63c5e6`.

Пины и хэши сверены с Git-объектами. Расширенный `not targets` принимает все 78 исторических записей discovery из `45861423438` и синтетическую дельту из 12 новых записей. Нативная дельта проверяется в CI. При допуске сохранить фактическую привязку оракула и контроля к `check_nN` из R1.
