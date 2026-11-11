# KANI3300 T1b-R — полный static compile sweep — Candidate 989f72351c2b5c5f3b5117315fc84f502e66d904; delta от CMP2 b1f0105c0390fb55081e3d186fa286d23867b585, все 9 файлов; compiler/-D warnings NOT_RUN.
1. compiler_interface.rs:117: `instances: Vec<Instance>` фиксирует E0282 до `.iter()`; global-pass signature принимает именно Vec<Instance>.
2. compiler_interface.rs:130–156: root_name String, len_instances Vec<Value>, absent bool; slice pattern/iterator &&Instance autoderef; JSON заимствует имена/коллекцию.
3. compiler_interface.rs:382,448–490: InvocationGuard используется Drop; units.iter() → &CodegenUnit, enumerate → usize; harness/stub names имеют CrateDef/Instance API.
4. codegen_order.rs:66–73: closure harness заимствован, name temporary живёт в вызове; rated Vec<(&Harness,usize)> уже аннотирован, порядок сохранён.
5. kani_middle/mod.rs:81: trace зарегистрирован; все pub(crate) helpers имеют call sites, лишних module imports нет.
6. trace.rs:80–122: guard MutexGuard<Option<Trace>>, filters Vec<String>, directory OsString, trace_id Option<String>, stage String.
7. trace.rs:93–94: единственные новые `?` находятся в Config::from_env -> Option<Self>; write methods возвращают io::Result, ошибки записи поглощаются явно.
8. trace.rs:127–180: pid u32, slot выведен как Option<(File,String)> из присваивания, index 0..4 допускает integer fallback; path PathBuf, trace Self.
9. trace.rs:183–250: value Value; sink RecordSink; encoded Vec<u8> из поля, footer_reserve usize по константе; json! заимствует self.* без move.
10. trace.rs:253–311: omitted usize, state &str, marker Value, bytes Vec<u8>; flush/write results используются; Write imports нужны обоим sinks.
11. trace.rs:314–375: OnceLock/Mutex/atomic closures имеют concrete types; Option<&Config>, Option<&mut Trace>, guards не выходят за lock scope.
12. trace.rs:380–425: sink DumpSink, dump_ok bool, omitted usize; prefix/suffix borrow до drop Value; collect::<Vec<_>>() задаёт u8 и String.
13. trace.rs:438–505: line String, end/remaining usize; Vec/VecDeque элемент u8 задан struct fields; Debug sink использует отдельный std::fmt::Write.
14. delayed_ub/initial_target_visitor.rs:32–93: Instance Copy, instance_name Option<String>, selected bool; place/static borrowed для debug, затем clone/Copy в targets.
15. initial_target_visitor.rs:115–159: новые push_operand call sites передают Location (Copy), reason &str; MirVisitor signatures сохранены.
16. delayed_ub/instrumentation_visitor.rs:161–274: resolved HashSet<MemLoc>, witness Option<&MemLoc>, get/set_witness Option<String>; references не выходят из block.
17. instrumentation_visitor.rs:212–232: visited_pairs Vec<(HashSet<MemLoc>,HashSet<MemLoc>)> связан push/contains; state move после ancestors borrows, решения не изменены.
18. delayed_ub/mod.rs:73–108: initial_targets Vec<AnalysisTarget> из into_targets; witness String; inner move closure захватывает Copy &Instance/TyCtxt, не перемещает instances.
19. delayed_ub/mod.rs:113–208: targets HashSet<MemLoc>, analysis_targets выведен extend(successors); instance_name Option<String> не move; body move только после snapshots.
20. check_uninit/mod.rs:130–208: instructions Vec<InitRelevantInstruction> из find_all; before/after Vec<&str> по AsRefStr; borrowed ops до instructions.into_iter().rev().
21. transform/mod.rs:153–226: name Option<String>, traced/cache_hit bool, transformed &mut TransformationResult; closure использует раздельные поля self; body/result move соответствуют прежнему pass loop.
22. Пин API: все 11 source hashes из ../t1b/API-SOURCES.json проверены, Rust7189d39d9ce936881b8132c6addeaf3e295cd455 (nightly-2026-10-23): Instance::{body,name,mangled_name,has_body}, Body::dump<W:io::Write>, CrateDef::name, Location Copy.
23. G1 E0308: target::MachineSize::{bytes,bits}->usize; LayoutShape.size есть MachineSize, diagnostic delta не вводит size/layout arithmetic или преобразований в usize.
24. Imports/variables/fields/trait methods просмотрены под -D warnings; rustfmt всех 9 файлов, source/text diff --check и patch apply --whitespace=error PASS (context-пробелы .patch исключены); независимое review PASS (REVIEW-KANI.md), compiler acceptance не установлено.
