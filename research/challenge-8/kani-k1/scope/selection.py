"""Reviewable SCOPE policy: dependencies and domains precede timing, no E/K/R edits."""
import re


def select(r):
    mod, macro, name = r["module"], r["macro"], r["name"].split("::")[-1]
    if mod == "correct":
        if macro == "fallback_stub_harness":
            return "correct-fallback", False, "Все insertion-stub callers вместе; u64 base-region и allocation transfer не доказаны"
        if macro in ("scratch_contract_harness", "general_stub_harness"):
            return "correct-scratch-general", False, "Верхний dual-stub домен N14/15 и scratch contract перенесены вместе"
    if mod == "merge":
        if macro == "define_general_sortedness_harness":
            return "merge-general-callers", False, "Вся группа merge-stub callers; exact-N contract не закрывает scratch48 transfer"
        if macro == "define_merge_contract_harness":
            return "merge-contract-upper", False, "Отдельные N5..16: callers уже opt-in; ordinary сохраняет самостоятельные N2..4"
        if macro in ("define_fallback_property_harness", "define_fallback_route_harness"):
            keep = macro == "define_fallback_property_harness" and int(r["args"][1]) <= 6
            return "merge-fallback", keep, "Реальные insertion bodies N0..6; дорогие N7/8 расширяют длины opt-in"
        if macro == "define_drop_route_harness":
            return "merge-drop", name != "drop_general_tag_permutation_n16", "Сохранены normal-return Drop counts до16 и tags до8; дорогой tag N16 opt-in"
        if macro == "define_route_safety_harness":
            return "merge-routes", int(r["args"][2]) in (2, 8, 16), "Срез exact-length real general/noncopy/stable: 2/8/16; остальные три-route группы opt-in целиком"
    if mod == "network":
        if macro == "insert_tail_contract_case":
            return "tail-shifted", False, "Все start1..15 в [u64;17] вместе с insertion-stub callers opt-in"
        if macro == "network_correctness_cases":
            keep = bool(re.search(r"_n(?:0_to2|3_to4|[5679]|13)$", name)) and not name.endswith("u64_n13")
            return "network-correctness", keep, "Сохраняются реальные входы 0..7 и network width9, u8 width13; дорогие/дублирующие верхние длины opt-in"
        if macro == "insertion_permutation_case":
            return "insertion-permutation", bool(re.search(r"_n(?:10|14)$", name)), "Независимые permutation свидетели suffix после width9/13: N10/14; не whole-route theorem"
        if macro in ("insertion_safety_cases", "mutating_insertion_cases"):
            return "insertion-lower", name.endswith("_n1_to5"), "Сохраняются все offsets N1..5; N6..14 opt-in; верхний максимум20 отдельной полной группой"
        if macro == "insertion_offset_group_cases":
            return "insertion-upper", "_n20_" in name, "Сохранены все offsets1..20 plain+mutating; все группы N15..19 opt-in, без утверждения о них"
        if macro in ("unstable_dispatch_network_cases", "unstable_freeze_network_cases"):
            keep = macro == "unstable_freeze_network_cases" or "_n30_to32" in name
            return "network-safety-u64", keep, "Реальный u64 Freeze N0..17 и unstable30..32; промежуточные18..29 opt-in, переход18 есть у u8"
        if macro in ("dispatch_safety_cases", "dispatch_pair_safety_cases"):
            return "dispatch-safety", not name.endswith("_n31"), "Trait/типовые переходы15..17 и максимумы32 сохранены; одиночные31 bytes16/17/85/Drop opt-in"
        if macro == "swap_contract_exact_array_case":
            return "swap-types", "bytes85" not in name and "bytes86" not in name, "Сохраняются u8/u64, bytes16/17, Cell, Drop; дорогие byte widths85/86 opt-in"
        if macro == "swap_contract_arbitrary_indices_case":
            return "swap-indices", False, "Промежуточные exact allocations9/12/13/16 opt-in; отдельные17 и four-positions остаются без transfer claim"
        if macro == "mutating_route_cases":
            return "mutating-routes", "_n9_to12" not in name, "Реальные Cell traits N0..8 и13..16 сохраняются; промежуточные9..12 opt-in"
    if mod in ("types", "smoke"):
        return "c3a", True, "Ценные реальные logical trait входы и type predicate; macOS UNKNOWN, нужна проверка того же SHA"
    return "unchanged", True, "Лёгкое самостоятельное свойство/контракт или положительный witness; без изменения"
