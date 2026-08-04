VENV ?= .venv
PYTHON ?= $(VENV)/bin/python
FLATPAK_BUILD_DIR ?= .flatpak-build
APP_ID := ru.brewdoro.timer
LEGACY_APP_ID := ru.pomidor.timer

.PHONY: run test check install-editable install-user uninstall-user flatpak flatpak-run

run:
	PYTHONPATH=src $(PYTHON) -m brewdoro

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

check: test
	$(PYTHON) -m compileall -q src tests
	ruff check src tests
	ruff format --check src tests
	desktop-file-validate data/$(APP_ID).desktop
	appstreamcli validate --no-net --override=url-homepage-missing=info \
		data/$(APP_ID).metainfo.xml

install-editable:
	-uv pip uninstall --python $(PYTHON) pomidor
	uv pip install --python $(PYTHON) --editable .

install-user: install-editable
	mkdir -p $(HOME)/.local/share/applications
	mkdir -p $(HOME)/.local/share/icons/hicolor/scalable/apps
	mkdir -p $(HOME)/.local/share/metainfo
	sed 's|^Exec=.*|Exec=$(CURDIR)/$(VENV)/bin/brewdoro|' \
		data/$(APP_ID).desktop > $(HOME)/.local/share/applications/$(APP_ID).desktop
	install -m 0644 data/icons/hicolor/scalable/apps/$(APP_ID).svg \
		$(HOME)/.local/share/icons/hicolor/scalable/apps/$(APP_ID).svg
	install -m 0644 data/$(APP_ID).metainfo.xml \
		$(HOME)/.local/share/metainfo/$(APP_ID).metainfo.xml
	-rm -f $(HOME)/.local/share/applications/$(LEGACY_APP_ID).desktop
	-rm -f $(HOME)/.local/share/icons/hicolor/scalable/apps/$(LEGACY_APP_ID).svg
	-rm -f $(HOME)/.local/share/metainfo/$(LEGACY_APP_ID).metainfo.xml
	-update-desktop-database $(HOME)/.local/share/applications

uninstall-user:
	rm -f $(HOME)/.local/share/applications/$(APP_ID).desktop
	rm -f $(HOME)/.local/share/icons/hicolor/scalable/apps/$(APP_ID).svg
	rm -f $(HOME)/.local/share/metainfo/$(APP_ID).metainfo.xml
	-rm -f $(HOME)/.local/share/applications/$(LEGACY_APP_ID).desktop
	-rm -f $(HOME)/.local/share/icons/hicolor/scalable/apps/$(LEGACY_APP_ID).svg
	-rm -f $(HOME)/.local/share/metainfo/$(LEGACY_APP_ID).metainfo.xml
	-update-desktop-database $(HOME)/.local/share/applications

flatpak:
	flatpak-builder --force-clean $(FLATPAK_BUILD_DIR) flatpak/$(APP_ID).yml

flatpak-run:
	flatpak-builder --run $(FLATPAK_BUILD_DIR) flatpak/$(APP_ID).yml brewdoro
