from __future__ import annotations

import argparse
import csv
import sys
import zipfile
from pathlib import Path


DEFAULT_ROOT = Path("data_raw/RDD2022_extracted/RDD2022")
DEFAULT_SUMMARY = Path("outputs/rdd2022_nested_zip_summary.md")
DEFAULT_MEMBERS = Path("data_processed/rdd2022_nested_zip_members.csv")


def safe_member_target(base: Path, member_name: str) -> Path:
    if member_name.startswith(("/", "\\")):
        raise ValueError(f"Archive member has absolute path: {member_name}")
    member_path = Path(member_name)
    if any(part == ".." for part in member_path.parts):
        raise ValueError(f"Archive member escapes extraction directory: {member_name}")
    target = (base / member_path).resolve()
    target.relative_to(base.resolve())
    return target


def infer_extract_base(root: Path, zip_path: Path, member_names: list[str]) -> Path:
    domain = zip_path.stem
    normalized_domain = "Czech" if domain == "Czech_Republic" else domain
    first_parts = []
    for name in member_names:
        parts = [part for part in Path(name).parts if part not in {"", "."}]
        if parts:
            first_parts.append(parts[0])
    first_set = {part.replace("\\", "/") for part in first_parts}
    if domain in first_set or normalized_domain in first_set or "RDD2022" in first_set:
        return root
    return root / domain


def inspect_zip(root: Path, zip_path: Path) -> tuple[list[dict[str, str | int]], list[str], Path | None]:
    rows: list[dict[str, str | int]] = []
    notes: list[str] = []
    extract_base: Path | None = None
    try:
        with zipfile.ZipFile(zip_path) as zf:
            infos = zf.infolist()
            names = [info.filename for info in infos]
            extract_base = infer_extract_base(root, zip_path, names)
            for info in infos:
                rows.append(
                    {
                        "zip_path": str(zip_path),
                        "extract_base": str(extract_base),
                        "filename": info.filename,
                        "file_size": info.file_size,
                        "compress_size": info.compress_size,
                        "is_dir": "true" if info.is_dir() else "false",
                    }
                )
    except zipfile.BadZipFile as exc:
        notes.append(f"{zip_path}: BadZipFile: {exc}")
    except OSError as exc:
        notes.append(f"{zip_path}: OSError: {exc}")
    return rows, notes, extract_base


def extract_zip(zip_path: Path, extract_base: Path, allow_existing: bool) -> None:
    extract_base.mkdir(parents=True, exist_ok=True)
    if any(extract_base.iterdir()) and not allow_existing:
        expected_nested_zip_only = extract_base == zip_path.parent
        if not expected_nested_zip_only:
            raise RuntimeError(
                f"Extraction directory is not empty: {extract_base}. "
                "Use --allow-existing-extract-dir only if intentional."
            )
    base = extract_base.resolve()
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            safe_member_target(base, info.filename)
        zf.extractall(base)


def write_members(rows: list[dict[str, str | int]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["zip_path", "extract_base", "filename", "file_size", "compress_size", "is_dir"]
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(
    output: Path,
    root: Path,
    zip_paths: list[Path],
    rows: list[dict[str, str | int]],
    notes: list[str],
    extracted: bool,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    by_zip: dict[str, dict[str, int]] = {}
    for row in rows:
        key = str(row["zip_path"])
        bucket = by_zip.setdefault(key, {"members": 0, "uncompressed": 0, "compressed": 0})
        bucket["members"] += 1
        bucket["uncompressed"] += int(row["file_size"])
        bucket["compressed"] += int(row["compress_size"])
    lines = [
        "# RDD2022 Nested ZIP Summary",
        "",
        f"- Root: `{root}`",
        f"- Nested ZIPs found: `{len(zip_paths)}`",
        f"- Members listed: `{len(rows)}`",
        f"- Extracted this run: `{extracted}`",
        "",
        "## Nested ZIPs",
        "",
    ]
    for path in zip_paths:
        stats = by_zip.get(str(path), {"members": 0, "uncompressed": 0, "compressed": 0})
        lines.append(
            f"- `{path}`: {stats['members']} members, "
            f"{stats['uncompressed']} uncompressed bytes, {stats['compressed']} compressed bytes"
        )
    if notes:
        lines.extend(["", "## Notes", ""])
        for note in notes:
            lines.append(f"- {note}")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect and optionally extract nested RDD2022 domain ZIPs.")
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="RDD2022 folder containing nested domain ZIPs.")
    parser.add_argument("--members-csv", default=str(DEFAULT_MEMBERS))
    parser.add_argument("--summary", default=str(DEFAULT_SUMMARY))
    parser.add_argument("--extract", action="store_true")
    parser.add_argument("--allow-existing-extract-dir", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"Root does not exist: {root}", file=sys.stderr)
        write_summary(Path(args.summary), root, [], [], ["Root does not exist."], False)
        return 2

    zip_paths = sorted(root.glob("*.zip"))
    all_rows: list[dict[str, str | int]] = []
    all_notes: list[str] = []
    extract_bases: dict[Path, Path] = {}
    for zip_path in zip_paths:
        rows, notes, extract_base = inspect_zip(root, zip_path)
        all_rows.extend(rows)
        all_notes.extend(notes)
        if extract_base is not None:
            extract_bases[zip_path] = extract_base
    if all_rows:
        write_members(all_rows, Path(args.members_csv))

    extracted = False
    if args.extract:
        for zip_path in zip_paths:
            extract_base = extract_bases.get(zip_path)
            if extract_base is None:
                raise SystemExit(f"Cannot extract {zip_path}; inspection failed.")
            extract_zip(zip_path, extract_base, args.allow_existing_extract_dir)
        extracted = True

    write_summary(Path(args.summary), root, zip_paths, all_rows, all_notes, extracted)
    print(f"Nested ZIPs: {len(zip_paths)}; members: {len(all_rows)}; extracted: {extracted}")
    return 0 if zip_paths and not all_notes else 3


if __name__ == "__main__":
    raise SystemExit(main())
