# S1 — утверждённый уровень приёмки, 2026-11-17

Владелец через координатора утвердил: U по per-site аргументам, PFC на source-reported уровне Profiles v4,
role labels и S1-08 после независимого review. Эта запись фиксирует решение; не меняет исторические receipts.

- **U:** каждый generated arithmetic/bounds check разбирается по exact ID/site/function/description, pinned
  source и проверенным premises. SAT covers после вызова не заменяют такой разбор. Нельзя разрешить все
  std/helper checks одним исключением, менять UNREACHABLE на SUCCESS или засчитать недостижимую обязательную
  post/frame/relation assertion. Все прежние проверки и точные исходные статусы сохраняются.
- **PFC:** применяется тот же bounded source-reported метод, что у Profiles v4: pinned stock producer semantics,
  exact manual target/native metadata, full concrete instance/type/trait/impl/source clauses,
  checked_with/modifies-wrapper raw-symbol/property links и variant-specific oracles. Это actual PFC,
  не caller-only подмена. Независимый compiler/AST/MIR-provenance trace не является дополнительным gate
  этого уровня и не объявляется установленным. Independent B1/B2/general proof credit не присваивается.
- **Role labels:** неоднозначные положительные проверки получают константные kani::assert root::role labels;
  expressions/guards/assumptions/domain/negatives/covers остаются прежними. Старые properties нельзя
  привязать к новым сообщениям задним числом. Для новых messages требуется compatible S1-08 evidence.
- **Порядок:** отдельные replayable U/PFC components → новый S1-07 receipt → independent review готовых
  кандидатов/композиции → пакет координатору к GO на S1-08. Source/control/request должны быть exact frozen pins.
  Утверждение политики и preparation/review сами по себе не разрешают push/dispatch или запись reservation.

Домен S1 — прежний smoke N0..3 и точная fixture geometry. Полный threshold16/32, общий sorting theorem,
независимая корректность компилятора и дополнительные uninit/valid-value claims этим решением не закрываются.
