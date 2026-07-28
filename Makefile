.PHONY: docs docs-serve docs-clean clean

VENV        ?= .venv
UV          ?= uv
SPHINXBUILD  = $(VENV)/bin/sphinx-build
SPHINXAUTO   = $(VENV)/bin/sphinx-autobuild
DOCS_DIR     = docs
DOCS_BUILD   = $(DOCS_DIR)/_build/html
PORT         ?= 8000

docs-serve: docs
	@echo "Serving docs at http://localhost:$(PORT) ..."
	$(SPHINXAUTO) -b html --port $(PORT) --watch $(DOCS_DIR) $(DOCS_DIR) $(DOCS_BUILD)

docs: $(VENV)/bin/sphinx-build
	$(SPHINXBUILD) -b html $(DOCS_DIR) $(DOCS_BUILD)
	@echo "Build finished. Open $(DOCS_BUILD)/index.html"

$(VENV)/bin/sphinx-build:
	@echo "Creating virtualenv in $(VENV) with uv and installing dependencies..."
	$(UV) venv $(VENV)
	$(UV) pip install --python $(VENV)/bin/python -r $(DOCS_DIR)/requirements.txt
	$(UV) pip install --python $(VENV)/bin/python sphinx-autobuild

docs-clean:
	rm -rf $(DOCS_DIR)/_build

clean: docs-clean
	rm -rf $(VENV)
