set dotenv-load := false

# Copy Stage 0 into a target repo
apply target answers:
    python3 scripts/apply.py --target {{target}} --answers {{answers}}

test:
    python3 scripts/test_apply.py
    python3 padf/harness/scripts/test_evidence_check.py
    python3 padf/harness/scripts/test_utv_close.py
    python3 padf/harness/scripts/evidence_check.py --selftest
