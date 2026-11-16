# Вход w11 — S1-07 run 43923266772

**Intake READY; qualified acceptance PENDING_OFFLINE_W11, proof credit NONE.**
Pins, totals, отличия и измерения — [RESULT.md](RESULT.md).
Машинный вход с SHA256 каждого input — [W11-INPUTS.json](W11-INPUTS.json).
Он ссылается на неизменённый S1-06 accept-v2 как на карту gaps, не как на новое
admission. Source/tool/flags/domain/rows/variants те же; новый evidence не
склеен с прежними after-измерениями.

| MISSING-FOR-S1-07 | Что теперь доступно | Что остаётся UNKNOWN |
|---|---|---|
| 1. After fingerprints | Before/after fixed 3 binaries у всех 14 групп, включая прежние 10 групп / 26 строк; phases/completion/shutdown/errors и original exits сохранены | Per-root process exit/wall/RSS и отдельный compile exit |
| 2. PFC target → wrapper, 22 строки | Exact native selector/crate/attrs/contract symbol, source/export/config/variant/binary manifests | Compilation ID, DefPathHash/FnDef/instance, disambiguator, substitutions, selected impl, checked_with/modifies-wrapper/call/property edges, effective clauses и spans |
| 3. Placeholder assertions | Полный exact stock/rich inventory, исходные placeholders и native harness metadata | Assertion origin/expression, macro expansion chain/instances/substitutions; прежние 111 links / 21 root не закрыты |
| 4. UNREACHABLE | Все 413 checks и 2 covers с теми же ID/статусами; 18 exact location exceptions сохранены | Property→MIR instance/block/statement, path predicates, caller/target/clause origin; прежние 133 applicability + 54 post-binding gaps |
| 5. Covers, negatives, companions, N0..3 | 113 satisfied covers, 8 exact sole failures с same-run source SUCCESS companions; 4 unions × 4 N-member одного run | Expanded cover predicate/arm/assumptions/call-return-post-frame origin; general domain completeness |
| 6. Metadata coherence | 322 exact native JSON / 35 selector-crate refs / 14 invocation namespaces; manifests/argv/cfg/unwind/original exits/source/variant/hashes проверены | Общая compiler compilation/export-instance identity и перечисленные semantic edges |

Каждая `collected.json.rows[]` сохраняет source verdict, stock buckets,
failed/unsupported records, rich inventory pointer, exact exceptions, before/after
snapshots, native refs, measurements и binding_gaps. Ключ включает group/row/variant;
production и mutant с одинаковым selector не объединяются.

`evidence/<group>/export.json`, `properties.json`, `binding-metadata.json` — exact
исходные bytes. Receipt projections удаляют только bounded stdout/stderr previews;
оригинальный compact artifact сохранён в `artifacts/<name>/group-evidence.json.gz`.
Native JSON embedded в `binding-metadata.json#/native_metadata/<index>/text`,
рядом exact path/sha256/bytes; refs указывают metadata_path и JSON pointer внутрь
native document. Manifest связывает export/rich/compile bytes с этим invocation.
UUID и mangled wrapper name не заменяют compiler-instance binding.

Повтор структурной проверки из любой cwd:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/ch8-s1/s1-07/run-43923266772/intake.py
```

Нужны неизменённые `/root/kani-ch8-s1-07-w13` (candidate9208 и siblingb37
в git object store), `/root/verify-rust-std-ch8-s1-04-w13` (std5be), S1-06
evidence и accept-v2/LOCATION-POLICY. Replay использует только Git/static hashes
и structured Python decoder/collector; verifier/compiler не запускается.
ZIP bytes уже не сохранены: replay проверяет download attestation, GitHub digest,
payload/member/native hashes; не заявляет новое вычисление ZIP digest.

Требуется офлайн-приёмка w11 по прежним exact bindings/role/companion gates.
При установлении обязательного UNREACHABLE post/frame/relation действует blocker;
location-only policy не даёт semantic исключения. Baseline counts gaps приведены
для навигации; semantic replay/admission в этом intake не выполнялся.
Новых запусков или exporter/tool patch эта передача не разрешает.
