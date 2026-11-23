# Diagnostics runner fix 2: goto-cc first-line check

Repository: /root/kani-ch8-kani5196-diag-control-20261123, branch ch8-kani5196-diag-control, head ccfcecba64.
Author for commits: Tiramisu-Cake <igkharin@gmail.com>, message ends with [skip ci]. No pushes.
No cargo, rustc, Kani, CBMC or Miri locally; Python unit tests of the control are allowed.

## Observed

Run 45158321038 (trigger 57c4eeb7a9) stopped again in "Build and attest the pinned tool once in runner temp",
before any root. Message:

    diagnostic control: goto-cc version mismatch: pin 6.11.0, first line 'gcc (goto-cc 6.11.0 (cbmc-6.11.0)) 13.3.0'

The setup receipt in the artifact recorded these real first lines (runner ubuntu-24.04, Kani head bcdc1a0f8d):

    cbmc:            6.11.0 (cbmc-6.11.0)
    goto_instrument: 6.11.0 (cbmc-6.11.0)
    goto_cc:         gcc (goto-cc 6.11.0 (cbmc-6.11.0)) 13.3.0
    kissat:          4.0.1
    launcher:        Kani Rust Verifier 0.68.0 (bcdc1a0) (standalone)
    rustc:           rustc 1.102.0-nightly (65ce8611f 2026-11-18)

Cause: _require_release in ch8-kani5196-control/tool_attestation.py requires the set of all release tokens on the
first line to equal the pin. goto-cc emulates gcc and appends the emulated gcc version (13.3.0), so the set is
{6.11.0, 13.3.0}.

## Required

1. Make the goto-cc check accept exactly this real line while keeping it strict: the CBMC release must be the one
   attached to goto-cc / cbmc-, every goto-cc or cbmc- release token on the line must equal the pin, and at least one
   must be present. The trailing gcc emulation version must not be compared to the CBMC pin. Do not loosen the cbmc
   and goto-instrument checks.
2. Unit tests: the exact real line above passes; variants fail, at least: goto-cc 6.11.1 with cbmc-6.11.0;
   goto-cc 6.11.0 with cbmc-6.11.1; a line with only "gcc ... 13.3.0" and no goto-cc/cbmc release; empty output;
   a release only on the second line. Keep the existing tests passing, and use the six real first lines above as the
   default fixture outputs where the tests mock tool output.
3. Run the control's synthetic tests the same way the workflow step "Validate frozen control and run synthetic tests"
   does, and report the command and result.
4. Build a new trigger commit: git commit-tree <new control tree> -p 467af9cb8d, author as above, message without
   any '#' followed by a number. Create local branch ch8-kani5196-diag-trigger2 at it. Do not push.
5. Write DIAG-FIX2-HANDOFF.md next to this file (g0 worktree, commit with [skip ci], no '#'+number in the message):
   diff summary, test command and result, new control head, tree, trigger SHA.

Stop after the handoff.
