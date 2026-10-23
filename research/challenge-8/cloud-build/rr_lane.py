"""Pure admission rules for the branch-local Network N7 diagnostic lane."""
import re

PHASE = 'NETWORK-RR-G1-2026-10-24-N7'
LANE = 'network-rr-g1'
REPOSITORY = 'us-central1-docker.pkg.dev/smallsort-ci/smallsort-tools/refinedrust-g1'
COLD_EXECUTOR = 'ubuntu@sha256:5ec03bb3441e8b0bf3b4f9cd4629a1ae763010dc3035bb8da3ae6cf026486401'
TIMEOUTS = {'cold-image': 1740, 'warm-g1': 1200}
PROFILE = 'research/challenge-8/cloud-build/network-rr/RR-G1-EXECUTION-PROFILE-20261024-N7.json'
LEDGER = 'research/challenge-8/cloud-build/network-rr/BUDGET-RR-G1-20261024-N7.json'
RECIPE = 'research/challenge-8/cloud-build/recipes/network-rr-g1.json'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def image_digest(value):
    require(isinstance(value, str) and re.fullmatch(re.escape(REPOSITORY) + r'@sha256:[0-9a-f]{64}', value),
            'RR warm image must be the assigned repository at an exact sha256 digest')
    return value


def profile_gate(profile, stage, seconds):
    require(stage in TIMEOUTS and type(seconds) is int and seconds == TIMEOUTS[stage],
            'RR stage requires its full exact timeout')
    require(isinstance(profile, dict), 'RR profile must be an object')
    require(profile.get('owner') == 'network' and profile.get('lane') == LANE and
            profile.get('authorization_phase_id') == PHASE, 'RR profile owner/lane/phase mismatch')
    tool, compiler, source = (profile.get(k) for k in ('tool', 'compiler', 'std_source'))
    require(isinstance(tool, dict) and tool.get('source_commit') == '332d945fafa14bf55c0c8390cb35ec4b0c012cff' and
            tool.get('source_tree') == 'b33bcccbbbd6168ac73e0c7238a1edddbe34057c' and
            tool.get('patched') is False and tool.get('frontend_patches_allowed') is False,
            'RR tool pin or unpatched boundary mismatch')
    require(isinstance(compiler, dict) and compiler.get('channel') == 'nightly-2026-08-28' and
            compiler.get('rustc_commit') == 'e457a7b0d326d67b4322ef0d11bd715cfaeda48f', 'RR compiler pin mismatch')
    require(isinstance(source, dict) and source.get('selected_baseline') == 'cd371e035c7e573760c43bf934d53e8118ee3e7d',
            'RR source baseline mismatch')
    build = profile.get('image_build')
    require(isinstance(build, dict) and build.get('cold_executor') == COLD_EXECUTOR, 'RR cold executor digest mismatch')
    require(profile.get('proof_credit') is False and profile.get('independent_credit') is False and
            profile.get('profile_accepted') is False, 'RR diagnostic cannot carry proof acceptance')
    if stage == 'cold-image':
        return COLD_EXECUTOR
    image = image_digest(build.get('image_digest'))
    require(isinstance(build.get('image_receipt_sha256'), str) and
            re.fullmatch(r'[0-9a-f]{64}', build['image_receipt_sha256']) and
            isinstance(build.get('cold_build_id'), str) and
            re.fullmatch(r'[0-9a-f-]{36}', build['cold_build_id']), 'RR warm image lacks a frozen cold receipt')
    return image


def attempts_gate(ledger, stage, candidate, profile):
    require(isinstance(ledger, dict) and isinstance(ledger.get('builds'), list), 'RR build ledger malformed')
    builds = ledger['builds']
    require(all(isinstance(b, dict) and b.get('accounted') is True for b in builds),
            'RR prior Build must be terminal and accounted')
    terminal = {'SUCCESS', 'FAILURE', 'INTERNAL_ERROR', 'TIMEOUT', 'CANCELLED', 'EXPIRED', 'NOT_CREATED_INVALID_ARGUMENT'}
    require(all(b.get('stage') in TIMEOUTS and b.get('status') in terminal for b in builds),
            'RR prior Build stage/status mismatch')
    prior = [b for b in builds if b.get('stage') == stage and b.get('status') != 'NOT_CREATED_INVALID_ARGUMENT']
    require(len(prior) < 2, 'RR stage attempt limit reached')
    require(not any(b.get('stage') == stage and b.get('infra_sha') == candidate for b in builds),
            'RR unchanged configuration must not be repeated')
    if prior:
        repair = ledger.get('setup_repair' if stage == 'cold-image' else 'warm_repair')
        require(isinstance(repair, dict) and repair.get('prior_build_id') == prior[-1].get('build_id') and
                repair.get('candidate_sha') == candidate and isinstance(repair.get('evidence'), str) and
                bool(repair['evidence'].strip()), 'RR retry requires a recorded evidence-driven repair')
        if stage == 'cold-image':
            require(prior[-1].get('status') != 'SUCCESS', 'RR successful cold image cannot be repeated')
    if stage == 'warm-g1':
        cold_id = profile['image_build']['cold_build_id']
        require(any(b.get('stage') == 'cold-image' and b.get('build_id') == cold_id and
                    b.get('status') == 'SUCCESS' for b in builds), 'RR warm stage requires the reconciled successful cold Build')


def time_budget(seconds, stage):
    require(stage in TIMEOUTS and type(seconds) is int and seconds == TIMEOUTS[stage], 'RR timeout shortened or stage mismatch')
    return {'package_reserve': 240, 'work_seconds': seconds - 240, 'soft_margin': 15}
