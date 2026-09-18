# taoteching-farsi automation recipes

py := if path_exists(".venv/bin/python") == "true" { ".venv/bin/python" } else { "python3" }

# Run all linters and checkers
check:
    @{{py}} -m tools.check_parity
    @{{py}} -m tools.normalize --check
    @{{py}} -m tools.check_terms --check
    @{{py}} tools/apparatus.py --check
    @{{py}} -m unittest discover tools/tests

# Auto-correct orthography across fa/
fix:
    @{{py}} -m tools.normalize --fix
    @{{py}} -m tools.check_terms --fix

# Run roundtrip tests across source files
test-roundtrip:
    @{{py}} tools/apparatus.py roundtrip-test source/01.md source/38.md

# Regenerate missing stubs in fa/
stubs:
    @{{py}} -m tools.make_stubs

# HTML, PDF and EPUB via Quarto
build:
    quarto render

# Render PDF with LuaLaTeX
pdf:
    quarto render --to pdf

# Render Mobile PDF
pdf-mobile:
    quarto render --profile mobile --to pdf

# Render HTML website edition
html:
    quarto render --to html

# Render EPUB edition
epub:
    quarto render --to epub

# Live preview server
serve:
    quarto preview --port 4200

# Clean build artifacts
clean:
    rm -rf _book _book-mobile .quarto
