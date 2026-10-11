(* Cloud-only regression for the numeric scalar equality used by AST transport. *)
let () =
  let large = "12345678901234567890123456789012345678901234567890" in
  let left = Big_int.big_int_of_string large in
  let equal = Big_int.big_int_of_string large in
  let different = Big_int.succ_big_int equal in
  assert (Big_int.eq_big_int left equal);
  assert (not (Big_int.eq_big_int left different));
  assert (not (Big_int.eq_big_int left (Big_int.minus_big_int equal)));
  let third = Num.num_of_string "1/3" in
  let same = Num.num_of_string "2/6" in
  let other = Num.num_of_string "1/4" in
  assert (Num.eq_num third same);
  assert (not (Num.eq_num third other));
  assert (not (Num.eq_num third (Num.minus_num same)));
  print_endline "NUMERIC_TRANSPORT_CHECK: equal/different large integers and rational values PASS"
