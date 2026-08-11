from __future__ import annotations

import ast
import unittest
from pathlib import Path
from xml.etree import ElementTree


APP_ID = "io.github.coreharbor.Brewdoro"
ROOT = Path(__file__).resolve().parents[1]


class ApplicationIdTests(unittest.TestCase):
    def test_application_id_matches_packaging_files(self) -> None:
        manifest = ROOT / "flatpak" / f"{APP_ID}.yml"
        desktop = ROOT / "data" / f"{APP_ID}.desktop"
        metainfo = ROOT / "data" / f"{APP_ID}.metainfo.xml"
        icon = (
            ROOT / "data" / "icons" / "hicolor" / "scalable" / "apps" / f"{APP_ID}.svg"
        )

        self.assertTrue(manifest.is_file())
        self.assertTrue(desktop.is_file())
        self.assertTrue(metainfo.is_file())
        self.assertTrue(icon.is_file())
        self.assertIn(f"app-id: {APP_ID}", manifest.read_text(encoding="utf-8"))
        self.assertIn(f"Icon={APP_ID}", desktop.read_text(encoding="utf-8"))

        component = ElementTree.parse(metainfo).getroot()
        self.assertEqual(component.findtext("id"), APP_ID)
        self.assertEqual(
            component.findtext("launchable"),
            f"{APP_ID}.desktop",
        )

    def test_gtk_application_id_matches_flatpak_id(self) -> None:
        source = (ROOT / "src" / "brewdoro" / "application.py").read_text(
            encoding="utf-8",
        )
        module = ast.parse(source)
        application_id = next(
            node.value.value
            for node in module.body
            if isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "APPLICATION_ID"
            and isinstance(node.value, ast.Constant)
        )

        self.assertEqual(application_id, APP_ID)


if __name__ == "__main__":
    unittest.main()
