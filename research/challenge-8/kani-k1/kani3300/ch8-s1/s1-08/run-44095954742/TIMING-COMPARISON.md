# S1-07 → S1-08 timings

Field: `harness.resources.verification_time_s`; source5be→99e is the reviewed label delta. All other domain/config, variant, flags, tool and measured binary dimensions are checked per pair. These are descriptive producer measurements, not pure solver time. No causal claim for labels/kani::assert. Cell values come only from immutable diagnostic refs; the failed group stays unadmitted. Retry1200s excluded.

| Row / variant | Outcomes 07 → 08 | seconds 07 | seconds 08 | Δ s | completed ratio | cohort | compatible |
|---|---|---:|---:|---:|---:|---|---|
| stable_default_cell / production | SUCCESS → TIMEOUT | 367.259888 | 600.031112 | UNKNOWN | UNKNOWN | TIMEOUT_CENSORED | True |
| unstable_default_cell / production | SUCCESS → SUCCESS | 368.802324 | 594.575885 | 225.773561 | 1.61218042 | SUCCESS_SUCCESS | True |
| model_u8_n0_3 / production | SUCCESS → SUCCESS | 1.96557078 | 2.01006714 | 0.044496361 | 1.02263788 | SUCCESS_SUCCESS | True |
| model_cell_n0_3 / production | SUCCESS → SUCCESS | 2.17072745 | 2.12965563 | -0.041071822 | 0.981079236 | SUCCESS_SUCCESS | True |
| model_noncopy_n0_3 / production | SUCCESS → SUCCESS | 2.128976 | 1.99812522 | -0.130850782 | 0.93853816 | SUCCESS_SUCCESS | True |
| inactive_pairs_read_free / production | SUCCESS → SUCCESS | 0.067437097 | 0.066272916 | -0.001164181 | 0.982736787 | SUCCESS_SUCCESS | True |
| activation_descending_rejected / production | FAILURE → FAILURE | 0.015098755 | 0.014841749 | -0.000257006 | 0.982978332 | INTENDED_FAILURE_FAILURE | True |
| activation_effectful_rejected / production | FAILURE → FAILURE | 0.015210069 | 0.015233353 | 2.3284e-05 | 1.00153083 | INTENDED_FAILURE_FAILURE | True |
| activation_unsupported_type_rejected / production | FAILURE → FAILURE | 0.017260671 | 0.016748361 | -0.00051231 | 0.97031923 | INTENDED_FAILURE_FAILURE | True |
| corruption_companion / production | SUCCESS → SUCCESS | 0.161020599 | 0.218854916 | 0.057834317 | 1.35917341 | SUCCESS_SUCCESS | True |
| order_corruption_rejected / production | FAILURE → FAILURE | 0.064083404 | 0.099754589 | 0.035671185 | 1.55663686 | INTENDED_FAILURE_FAILURE | True |
| count_corruption_rejected / production | FAILURE → FAILURE | 0.093102512 | 0.141215236 | 0.048112724 | 1.51677149 | INTENDED_FAILURE_FAILURE | True |
| snapshot_guards_companion / production | SUCCESS → SUCCESS | 5.25243431 | 5.25778214 | 0.005347828 | 1.00101816 | SUCCESS_SUCCESS | True |
| invalid_snapshot_rejected / production | FAILURE → FAILURE | 0.028737654 | 0.027386524 | -0.00135113 | 0.952983984 | INTENDED_FAILURE_FAILURE | True |
| stable_default_activation-legal / production | SUCCESS → SUCCESS | 6.17814732 | 6.18915177 | 0.011004451 | 1.00178119 | SUCCESS_SUCCESS | True |
| stable_freeze_activation-legal / production | SUCCESS → SUCCESS | 35.1765881 | 35.1539214 | -0.022666705 | 0.999355631 | SUCCESS_SUCCESS | True |
| activation-default / activation-default | FAILURE → FAILURE | 1.45560591 | 1.83100115 | 0.375395235 | 1.2578962 | INTENDED_FAILURE_FAILURE | True |
| activation-override / activation-override | FAILURE → FAILURE | 14.4470886 | 9.95264995 | -4.49443868 | 0.688903502 | INTENDED_FAILURE_FAILURE | True |
| ordinary-bridge / production | SUCCESS → SUCCESS | 0.049704996 | 0.050500572 | 0.000795576 | 1.01600596 | SUCCESS_SUCCESS | True |
| freeze_copy_u8_n0 / production | SUCCESS → SUCCESS | 0.99423352 | 1.29751496 | 0.303281443 | 1.30504045 | SUCCESS_SUCCESS | True |
| freeze_copy_u8_n1 / production | SUCCESS → SUCCESS | 1.2017655 | 1.54153267 | 0.339767169 | 1.28272335 | SUCCESS_SUCCESS | True |
| freeze_copy_u8_n2 / production | SUCCESS → SUCCESS | 14.2061708 | 15.8720305 | 1.66585962 | 1.1172631 | SUCCESS_SUCCESS | True |
| freeze_copy_u8_n3 / production | SUCCESS → SUCCESS | 37.8957094 | 37.7614523 | -0.134257121 | 0.996457195 | SUCCESS_SUCCESS | True |
| freeze_default_noncopy_n0 / production | SUCCESS → SUCCESS | 0.954558841 | 1.04155184 | 0.086993002 | 1.09113425 | SUCCESS_SUCCESS | True |
| freeze_default_noncopy_n1 / production | SUCCESS → SUCCESS | 1.06518151 | 1.25683917 | 0.191657654 | 1.17992957 | SUCCESS_SUCCESS | True |
| freeze_default_noncopy_n2 / production | SUCCESS → SUCCESS | 94.4816822 | 59.4542216 | -35.0274606 | 0.629267179 | SUCCESS_SUCCESS | True |
| freeze_default_noncopy_n3 / production | SUCCESS → SUCCESS | 169.525288 | 99.336411 | -70.1888769 | 0.585968101 | SUCCESS_SUCCESS | True |
| stable_freeze_u8_n0 / production | SUCCESS → SUCCESS | 0.971449037 | 1.36008288 | 0.38863384 | 1.40005582 | SUCCESS_SUCCESS | True |
| stable_freeze_u8_n1 / production | SUCCESS → SUCCESS | 1.09978688 | 1.57340841 | 0.473621537 | 1.43064847 | SUCCESS_SUCCESS | True |
| stable_freeze_u8_n2 / production | SUCCESS → SUCCESS | 79.1060907 | 75.0452853 | -4.06080539 | 0.948666337 | SUCCESS_SUCCESS | True |
| stable_freeze_u8_n3 / production | SUCCESS → SUCCESS | 140.914022 | 135.014683 | -5.89933961 | 0.958135184 | SUCCESS_SUCCESS | True |
| unstable_freeze_u8_n0 / production | SUCCESS → SUCCESS | 1.18500074 | 1.47176684 | 0.286766104 | 1.24199656 | SUCCESS_SUCCESS | True |
| unstable_freeze_u8_n1 / production | SUCCESS → SUCCESS | 1.30252318 | 1.30103501 | -0.001488168 | 0.998857473 | SUCCESS_SUCCESS | True |
| unstable_freeze_u8_n2 / production | SUCCESS → SUCCESS | 15.4345026 | 16.9785572 | 1.54405453 | 1.10003915 | SUCCESS_SUCCESS | True |
| unstable_freeze_u8_n3 / production | SUCCESS → SUCCESS | 40.5961212 | 39.9881089 | -0.608012297 | 0.985022897 | SUCCESS_SUCCESS | True |

Cohorts (kept separate):

```json
{
  "INTENDED_FAILURE_FAILURE": {
    "rows": 8,
    "comparable_completed_pairs": 8,
    "known_ratios": 8,
    "ratio_min": 0.6889035018461642,
    "ratio_median": 0.9922545798447753,
    "ratio_max": 1.5566368634225487,
    "ratio_geomean": 1.080848680293382,
    "s107_completed_seconds_sum": 16.136187606,
    "s108_completed_seconds_sum": 12.098830907
  },
  "SUCCESS_SUCCESS": {
    "rows": 26,
    "comparable_completed_pairs": 26,
    "known_ratios": 26,
    "ratio_min": 0.5859681008808685,
    "ratio_median": 1.0088935729512705,
    "ratio_max": 1.612180417934866,
    "ratio_geomean": 1.059286194849347,
    "s107_completed_seconds_sum": 1022.887017342,
    "s108_completed_seconds_sum": 1137.944697993
  },
  "TIMEOUT_CENSORED": {
    "rows": 1,
    "comparable_completed_pairs": 0,
    "known_ratios": 0,
    "ratio_min": null,
    "ratio_median": null,
    "ratio_max": null,
    "ratio_geomean": null,
    "s107_completed_seconds_sum": null,
    "s108_completed_seconds_sum": null
  }
}
```

TIMEOUT is censored: stable_default_cell observed600.031112420s at600s cutoff. The JSON records the conditional completion-time lower bound relative to the completed baseline; it is excluded from completed ratios. Missing inventories and null durations are UNKNOWN, never zero.

Common pairs: 35; incompatible: 0; unpaired: 0. Exact outcomes, limits, join dimensions, expected message differences and evidence hashes are in TIMING-COMPARISON.json.
