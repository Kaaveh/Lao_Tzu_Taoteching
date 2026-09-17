# taoteching-farsi automation recipes

# Run all linters and checkers
check:
    @.venv/bin/python -m tools.check_parity
    @.venv/bin/python -m tools.normalize --check
    @.venv/bin/python tools/apparatus.py --check
    @.venv/bin/python -m unittest discover tools/tests

# Auto-correct orthography across fa/
fix:
    @.venv/bin/python -m tools.normalize --fix

# Run roundtrip tests across source files
test-roundtrip:
    @.venv/bin/python tools/apparatus.py roundtrip-test source/01.md source/38.md

# Regenerate missing stubs in fa/
stubs:
    @.venv/bin/python -m tools.make_stubs
