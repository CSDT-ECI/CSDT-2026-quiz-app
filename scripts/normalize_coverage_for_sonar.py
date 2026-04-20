#!/usr/bin/env python3
"""
Rewrite coverage.xml so paths match SonarCloud's file keys.

pytest-cov emits Cobertura with <source></source>, <source>app</source>, and
filenames like api/quiz.py or server.py under package ".". Sonar often fails to
map server.py (repo root) to coverage lines. This script uses a single source
"." and paths relative to the repo root (app/..., server.py).
"""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET


def normalize_coverage_xml(path: str) -> None:
    tree = ET.parse(path)
    root = tree.getroot()

    sources_el = root.find("sources")
    if sources_el is None:
        print("No <sources> in coverage.xml; leaving unchanged.", file=sys.stderr)
        return

    sources_el.clear()
    ET.SubElement(sources_el, "source").text = "."

    for package in root.findall(".//package"):
        pkg_name = package.get("name", "")
        # Cobertura nests <class> under <classes>, not directly under <package>
        for cls in package.findall(".//class"):
            fn = cls.get("filename")
            if not fn:
                continue
            if fn == "server.py":
                new_fn = "server.py"
            elif pkg_name == ".":
                new_fn = f"app/{fn}"
            else:
                new_fn = f"app/{fn}"
            cls.set("filename", new_fn)

    tree.write(path, encoding="UTF-8", xml_declaration=True)


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "coverage.xml"
    normalize_coverage_xml(target)
    print(f"Normalized {target} for SonarCloud path matching.")
