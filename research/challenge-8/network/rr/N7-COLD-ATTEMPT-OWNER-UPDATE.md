# Cold-попытки: уточнение владельца, 2026-10-24

Основание — прямое указание владельца после завершения Network N7:
«считать за cold-попытки те, что достигли запуска, а не те, которые решали его инфраструктурные вопросы».

Cold-попытка расходуется при подтверждённом начале выполнения Dockerfile
целевого образа RefinedRust. Submit/admission, очередь, запуск Cloud wrapper,
передача Docker context и вызов `docker build` сами по себе этого не устанавливают.
Нужен привязанный к Build факт начала выполнения Dockerfile через Evidence Brief.
Если подтверждения недостаточно, состояние запуска UNKNOWN; исчерпание лимита
по одному submit не выводить. Cold image build и warm G1 учитывать отдельно:
для cold не требуется дойти до запуска RR frontend или получить успешный образ.
Отказ или timeout после подтверждённого начала Dockerfile расходует cold-попытку.

Отказы до этого запуска относятся к infrastructure/setup и не расходуют число
cold-попыток. Их Build IDs, расходы, ошибки и repair-история сохраняются.
Setup repairs ограничены выданными Cloud budget и окном; неизменённую ошибочную
конфигурацию не повторять, исправления проверять статически и по действующим
review/admission rules. Отдельный дополнительный числовой лимит infrastructure
submits из cold-лимита не выводить.

## Пересчёт N7

| Build | Достигнутый этап | Cold-попытка | Infrastructure/setup |
| --- | --- | ---: | ---: |
| `efd32c5f-83e5-4cae-8b4a-a83dc7bc072a` | EXPIRED до исполнения, execution 0s | 0 | 1 |
| `3e604123-0d22-415d-b629-5ce2bf05aca7` | Docker API 1.52 отвергнут daemon 1.41 до выполнения Dockerfile | 0 | 1 |

Итого: **0 cold-попыток, 2 infrastructure/setup Builds**. Основания:
[metadata observation](N7-COLD-EXPIRED-OBSERVATION.json) (причина expiry UNKNOWN,
Brief HTTP404) и [Brief failure observation](N7-COLD-FAILURE-EVIDENCE.json)
(вывод о границе запуска из точной диагностики, статуса и выбранного скрипта;
SOURCE_REPORTED, не независимое proof evidence).

Прежнее толкование «две cold admissions исчерпали лимит» отменено этим указанием.
Исходный closeout сохранён в commit `570f0a8e`; observations, result identities,
исторические verdicts и ledger не переписываются. Текущие checkpoint views
отражают новое толкование с отдельной ссылкой на это решение.

Закрытый N7 account сохраняет 391s spent, 5009s retired, carry0. Новый критерий
не возобновляет закрытый ledger и не переносит retired budget: продолжение
использует новое задание/account по действующим правилам с этим критерием.
Image digest отсутствует; warm G1 NOT_RUN, verdict INCONCLUSIVE, proof credit 0.
