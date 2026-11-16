# B-02 intake handoff — одна стадия

Готовы `RESULT.md`, полная 235-row `TABLE.json`, `intake.py` и непубликованный
`ISSUE-DRAFT.md` для existing #3762. Input g0 `4c8ad23a1b`; это новый intake
пакет, прежние CURRENT-TASK/CHECKPOINT и historical NOT_RUN не переписаны.

Результат: COMPLETE235; PASS11; copy Unsupported224. **237 failures: 211 roots
с одним, 13 с двумя**, других failures нет. Все intended-invalid oracles false.
PASS причины и все unreachable property IDs сохранены. Proof credit NONE;
workflow success — полнота diagnostic, group exit1. Binary/source receipts
остаются source-reported; ZIP hash независимо совпал с read-only GitHub API.

Источник ZIP (scratch):
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/b02/a.zip`.
Artifact14192030971/run43788110361, SHA256
`d67f61fbd18549741490e0b96843fd63f21a42eb37c7ba23d33087f6542b61f5`.
TABLE сохраняет member hashes, exact input pins и export identity; не полные
workflow logs. Raw global export runner удаляет; его SHA только source-reported.

Воспроизведение static intake из g0 (вывод в отдельный scratch-файл для сравнения):

```sh
python3 research/challenge-8/kani-k1/kani3300/ch8-b/pprime-batch/run-43788110361/intake.py \
  /tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/b02/a.zip \
  /root/kani-ch8-b-pprime-w14 > /tmp/ch8-b02-table-check.json
cmp research/challenge-8/kani-k1/kani3300/ch8-b/pprime-batch/run-43788110361/TABLE.json /tmp/ch8-b02-table-check.json
```

Следующему владельцу B: отдельный bounded task на integer-only NoConstraints
candidate, audit Unknown/aggregate branches, distinguishing legal/invalid
controls, independent review и coordination with #3762. Не добавлять общий
eager source read. Самый узкий кандидат не закрывает bool/char/NonZero или
алиасированные delayed typed uses. Cap B2/3 использован по поручению; B-03
только после отдельного coordinator GO и готового candidate/envelope. Этот
intake ничего не резервирует и не отправляет.

Accounting этой стадии: push0, CI0, publications0, ledger writes0,
local cargo/rustc/Kani/CBMC0. `/root/kani-ch8-b-census-w14` только прочитан,
HEAD `5ee153ec2b22f1f7a0e174a985369b2280d8d296`, clean. Отдельный Luna HIGH
helper сделал read-only source investigation, без вложенной делегации.
