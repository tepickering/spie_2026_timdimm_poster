# timDIMM SPIE 2026 poster build
#   make            render the PDF, check it is A0, and build the preview
#   make poster     render timdimm_poster.pdf and verify the page box is A0
#   make preview    build preview.png (override size: make preview SIZE=2400)
#   make check      assert timdimm_poster.pdf has an A0 page box
#   make plots      regenerate result figures from the CSVs
#   make assets     stage logos + photos into assets/
#   make open       open the rendered PDF
#   make clean      remove generated artifacts

PYTHON ?= /Users/tim/conda/envs/timdimm/bin/python
SIZE   ?= 1600

ASSETS  := $(wildcard assets/figures/*) $(wildcard assets/logos/*)
SOURCES := index.html styles.css palette.css $(ASSETS)

.PHONY: all poster render check preview plots assets open clean

all: poster preview

poster: render check

render: timdimm_poster.pdf

timdimm_poster.pdf: $(SOURCES)
	bash scripts/render.sh

check: timdimm_poster.pdf
	$(PYTHON) scripts/check_pdf.py

preview: preview.png

preview.png: $(SOURCES)
	bash scripts/preview.sh $(SIZE)

plots:
	$(PYTHON) scripts/make_plots.py

assets:
	bash scripts/prepare_assets.sh

open: timdimm_poster.pdf
	open timdimm_poster.pdf

clean:
	rm -f timdimm_poster.pdf preview.png preview_full.png
