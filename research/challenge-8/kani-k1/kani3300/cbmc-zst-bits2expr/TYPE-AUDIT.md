# C++ type/signature audit (source inspection; no compiler)

| Site / API | Checked source declaration and implication |
| --- | --- |
| pointer_offset_bits | pointer_offset_size.h returns std::optional<bitst>; no comparison of optional itself with an integer. Short-circuit has_value precedes dereference. |
| bitst | mp_arith.h aliases named_mp_integert<bits_tagt>. operator>=(const named_mp_integert&) const returns bool; bitst{0} uses its explicit mp_integer constructor. Same form already used in struct branch. |
| Element conversion | arith_tools.h numeric_cast_v<Target>(const named_mp_integert<Tag>&) checks conversion of arg.get(). Element width is checked present/nonnegative before size_t conversion. No premature cast introduced. |
| Count conversion | array size is exprt; PRECONDITION(size_expr.is_constant()) and to_constant_expr precede numeric_cast_v<size_t>. Constant count must fit size_t, including nonnegativity. Neither symbolic nor invalid negative counts become supported. |
| Count/reserve | expr.h reserve_operands(operandst::size_type); array_exprt({}, array_type) takes operandst and array_typet by value. Count and loop index remain size_t; exactly N moves are appended for successful recursion. |
| Zero slice | std::string(bits, i*el_size, el_size) is the existing const string&, size_type pos/count overload. With el_size0 multiplication yields0 without overflow; empty source has valid pos0/count0. No division occurs. Existing nonzero-width code is unchanged. |
| Recursive return | simplify_utils.h: optional<exprt> bits2expr(const string&, const typet&, bool, const namespacet&). The optional is checked before std::move(*el); failures propagate unchanged. |
| Empty reconstruction | struct_exprt(operandst, typet) permits empty operands with the declared struct or tag type. Empty structs terminate immediately; nested arrays descend subtype depth and finite counts. No count-based division/recursion cycle is introduced. |
| Type/tag | std_types.h array_typet(typet, exprt), element_type() returns typet&/const typet&. Struct-tag recursion follows ns then restores val->type() to requested type. Unit equality checks E tag and complete wrapper/union expression types. |
| Struct components | struct_typet(componentst) and componentt(name, type) support the new initializer lists. width0 does not advance offset; later scalar component bits are retained. Tests use no implicit layout padding in manually built util types. |
| Union | union_typet is declared in c_types.h (explicitly included), constructor takes componentst. std_expr.h union_exprt(const irep_idt&, exprt, typet). Unit small arm is rejected by width consistency; suitable full W arm retains nonzero fields. |
| Symbol namespace | symbol.h symbolt(const irep_idt&, typet, const irep_idt&); symbol_table.h add returns bool (false on successful insertion). is_type is set. namespacet(const symbol_table_baset&) follows tag-E. |
| Unit assertions | Existing Catch wrapper includes variadic REQUIRE in unit/catch/catch.hpp, so braced constructors with commas are supported (also used by existing tests). C++17 optional<string> comparisons with string literals/other optionals are valid; optional values are checked before dereference. |
| Endianness | bool little_endian is forwarded unchanged at every recursion. Scalars retain endianness_mapt(type,bool,ns); expr2bits returns optional<string> and concatenates empty operands. Public unit data uses 0x5a / 0x12345678 / 0xa5 under both flags. |
| Unknown/negative widths | Whole-type check still returns optional failure for unknown width or inconsistent non-union bit count. Array guard still rejects unknown/negative element width. An unsupported known-width subtype can still return nullopt recursively; no supported domain is enlarged beyond width0 arrays with reconstructible elements. |
| Bounds/resource risk | N0/N1/N2 and small nested shapes are bounded. Large zero-extent N retains existing O(N) allocation/IR costs and may exhaust resources; no compression or arbitrary symbolic-size support is claimed. |

The source API declarations, existing examples and definitions were checked directly;
no local compiler, parser-based type checker, formatter or verifier was used.

Review disposition: the Low finding about negative constant array count is a
pre-existing invalid-type precondition, not a new valid-source failure. The count
cast occurs before the edited guard in BOTH develop and candidate; for an element
of width0 the total width is0 even with negative count, and the same checked cast
already rejects that count. Retain this rejection and the existing size_t-domain
requirement. No new count/optional-failure guarantee is promised and no adjacent
utility domain redesign is included. This explicitly documents the review's
suggested precondition option. SOURCE_READY does not establish COMPILED/PASS.
