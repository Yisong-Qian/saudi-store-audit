#!/usr/bin/env python3
"""Validate, install, and package the public skill using the standard library."""

import argparse
import json
from pathlib import Path
import re
import shutil
import sys
import zipfile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = PROJECT_ROOT / "skills" / "saudi-store-audit"
SKILL_NAME = "saudi-store-audit"
PUBLIC_FILES = (
    "SKILL.md",
    "agents/openai.yaml",
    "references/daily-columns.md",
    "references/writeback.md",
    "references/store-config.example.json",
)


def validate_bundle(source=SKILL_ROOT):
    """Check package structure and references without reading private settings."""
    source = Path(source)
    for name in PUBLIC_FILES:
        path = source / name
        if not path.is_file() or path.is_symlink():
            raise ValueError("Missing or symlinked public file: " + name)

    skill = (source / "SKILL.md").read_text(encoding="utf-8")
    parts = skill.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError("SKILL.md requires YAML frontmatter")
    if not re.search(r"^name:\s*saudi-store-audit\s*$", parts[1], re.MULTILINE):
        raise ValueError("Incorrect skill name")
    if not re.search(r"^description:\s*\S", parts[1], re.MULTILINE):
        raise ValueError("Missing skill description")

    for name in PUBLIC_FILES:
        if not name.endswith(".md"):
            continue
        path = source / name
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            target = target.split("#", 1)[0]
            resolved = (path.parent / target).resolve()
            if not resolved.is_relative_to(source.resolve()) or not resolved.is_file():
                raise ValueError("Broken local reference in " + name + ": " + target)

    ui = (source / "agents/openai.yaml").read_text(encoding="utf-8")
    if "$" + SKILL_NAME not in ui:
        raise ValueError("UI default prompt must mention the skill")
    config = json.loads((source / "references/store-config.example.json").read_text(encoding="utf-8"))
    if config.get("spreadsheet_url") != "":
        raise ValueError("Public example must not contain a real spreadsheet URL")
    if not all(config.get("sheets", {}).get(p, {}).get("title") for p in ("noon", "amazon")):
        raise ValueError("Example requires both platform sheet names")
    return [source / name for name in PUBLIC_FILES]


def install_bundle(destination, source=SKILL_ROOT):
    """Install only public files; never replace an existing installation."""
    source, destination = Path(source), Path(destination).expanduser()
    validate_bundle(source)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError("Destination already exists; back it up or choose another: " + str(destination))
    if destination.resolve().is_relative_to(source.resolve()):
        raise ValueError("Destination must be outside the source skill")
    destination.parent.mkdir(parents=True, exist_ok=True)

    def exclude_private(directory, names):
        relative = Path(directory).relative_to(source)
        return [
            name for name in names
            if not any(
                (relative / name).as_posix() == public
                or public.startswith((relative / name).as_posix() + "/")
                for public in PUBLIC_FILES
            )
        ]

    shutil.copytree(source, destination, ignore=exclude_private)
    return destination


def package_bundle(output, source=SKILL_ROOT):
    """Build a deterministic ZIP with an explicit public-file allowlist."""
    source, output = Path(source), Path(output)
    files = validate_bundle(source)
    if output.resolve().is_relative_to(source.resolve()):
        raise ValueError("Archive output must be outside the source skill")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            name = SKILL_NAME + "/" + path.relative_to(source).as_posix()
            info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate", help="Check the public skill structure")
    install = commands.add_parser("install", help="Install without overwriting an existing skill")
    install.add_argument("--destination", type=Path, default=Path.home() / ".agents/skills" / SKILL_NAME)
    package = commands.add_parser("package", help="Create the distributable skill ZIP")
    package.add_argument("--output", type=Path, default=PROJECT_ROOT / "dist" / (SKILL_NAME + ".zip"))
    args = parser.parse_args()
    try:
        if args.command == "validate":
            print("Validated " + str(len(validate_bundle())) + " public skill files.")
        elif args.command == "install":
            print("Installed: " + str(install_bundle(args.destination)))
        else:
            print("Packaged: " + str(package_bundle(args.output)))
    except (ValueError, OSError, json.JSONDecodeError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    main()
