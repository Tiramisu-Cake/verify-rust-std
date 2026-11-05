# CITRIM — этап завершён; цель частично достигнута: 4/9, пять blocker сохранены
Library `f1ce831c2c9b7a3307a652248c467fb086b94ea5`; base `4fa6151b6a`.
G1 `76b1664d-a0bf-4268-92fc-3b69220d556f`, source `bc4b5c7ec7b41a317548c21bc8dabeebfb062e5a`.
G2 `bd623a0c-935a-4bcd-a5c1-5d6f148c6bec`, source `9cc449ccce74c6b3b8f96554b86308ff39a2b71f`.
Обе COMPLETE/Cloud FAILURE, gate false/Kani exit1; standard4, jobs1, controls=false, 5мин/часть.
Pin `cd355b0bccd32300713bc2ce4f765dafa1510607`; tooling `59893bff1f`, pool/SHA/request bindings PASS.
Requests citrim-g1-20261105-01 / citrim-g2-20261105-02; hashes и bounded rows сохранены в evidence.
До — исходные Actions Ubuntu/macOS из TASK; после — GCB частей, сравнимого исходного GCB замера нет.

| Исходный verify:: корень | До U/M, с | Итоговые части, с каждой; Σ | Исходный домен = ∪ частей / решение |
| --- | ---: | --- | --- |
| merge::general_direct_u64_n9 | 374.0/211.6 | исходный восстановлен; G2 4 TIMEOUT; исходный GCB не измерен | тождество: исходный корень |
| merge::stable_direct_u64_n9 | 237.5/172.5 | исходный восстановлен; G2 4 TIMEOUT; исходный GCB не измерен | тождество: исходный корень |
| network::dispatch_safety_stable_unstable_bytes16_n15_16_17 | 154.3/218.1 | 57.527676 / 63.919994 / 64.92339; Σ186.371060 | {15,16,17}×обе ветви |
| network::dispatch_safety_stable_unstable_bytes16_n32 | 160.1/306.1 | 108.72484 / 118.51086; Σ227.23570 | N32×{stable,unstable} |
| network::dispatch_safety_stable_unstable_bytes17_n15_16_17 | 147.7/265.5 | 62.401028 / 70.84245 / 95.44369; Σ228.687168 | {15,16,17}×обе ветви |
| network::insert_tail_contract_u64_start1_tail2_to8 | 185.1/281.5 | исходный восстановлен; G2 2 TIMEOUT; исходный GCB не измерен | тождество: исходный корень |
| network::insert_tail_contract_u64_start1_tail9_to12 | 174.6/227.8 | исходный восстановлен; G2 2 TIMEOUT; исходный GCB не измерен | тождество: исходный корень |
| network::insert_tail_contract_u64_start1_tail13_to14 | 161.7/207.4 | исходный восстановлен; G2 tail13=299.7872, tail14 TIMEOUT; исходный GCB не измерен | тождество: исходный корень |
| network::network_safety_unstable_u64_n30_to32 | 209.5/235.5 | 112.93425 / 116.823906 / 117.06356; Σ346.821716 | {30,31,32} |

Ordinary **226=219−4+11 (+7)**; cfg-on **260=226+34**; [точные имена](citrim/final-ordinary-expected.txt).
215 исходных ordinary (включая пять восстановленных) и 34 opt-in token-identical; merge.rs byte-identical base.
Сохранены 10 частей G1 +1 часть G2: SUCCESS, 0 failed checks, <=120с, **31/31 covers**; bodies/dependencies совпали.
Равенство всех девяти финальных доменов: [check_final.py](citrim/check_final.py), [отчёт](citrim/final-check-report.json).
G1: 18 SUCCESS/7 TIMEOUT, 57/57 completed covers; G2: 2 SUCCESS/13 TIMEOUT, 5/5 completed covers; остальные неизвестны.
Оба merge N9 и все три исходных tail-корня восстановлены без изменений; исходные проверки/домены не потеряны.
G2 tail-рамка через checked PFC modifies была эквивалентна: [1,tail], рамка={0}∪[tail+1,16] — дополнение в backing17.
Modifies проверяется proof_for_contract; doc корней в G2 и [обоснование](citrim/CLOSEOUT-CITRIM.md) сохранены в истории.
Вариант frame+Kissat/unwind18 не достиг120с; вклад frame отдельно не измерен; финальные tail-рамки исходные.
TAILDIAG 59ada14d0a, 183→31с — сообщение координатора, не наш замер; соседний код/diff не читался.
Итоговый unstable bytes16N32: Kissat/unwind33, 118.51086с против126.870476с G1; два изменения не разделены.
Сумма 11 итоговых частей **989.115644с**; полные before/after неизвестны. Исходные Actions девяти: Σ1804.5/2126.0с.
Остальные 215 корней в CITRIM не перепроверялись; общего proof/full-suite PASS нет.
Пар исходных GCB/Actions нет, коэффициент не измерен; эвристика2×: max118.51с→237.02с, гарантии Actions<=200с нет.
Запас max до120с **1.48914с**; network N30/N31/N32 также близки к границе. Оставшиеся пять >200с blocker открыты.
Статика/rustfmt/diff-check PASS; оба tooling8/8 и targeted warning scan PASS; таймауты не засчитаны как proof.
Compiler inventory не получен: передан координатору отдельно для финальных226 имён; исторические235 не финальны.
Расход G1 $1.1880 +G2 $1.0935 =**$2.2815/$3**; резерв0, остаток$0.7185; builds2/2, repairs/retries0.
Дальше: пять исходных roots сохранять до новой авторизованной оптимизации; G3 не запускать, coverage не сужать.
RUN-REQUEST — исполненный исторический G2; итоговый inventory требует отдельного request/budget координатора.
Все Builds до16:00Z; [ledger](citrim/RUN-LEDGER.json), [closeout/inventory handoff](citrim/CLOSEOUT-CITRIM.md).
