from __future__ import annotations

import argparse
import csv
import hashlib
import sys
import zipfile
from pathlib import Path


DEFAULT_ZIP = Path("data_raw/RDD2022_archive/RDD2022_released_through_CRDDC2022.zip")
DEFAULT_MANIFEST = Path("data_processed/rdd2022_figshare_files.csv")
DEFAULT_MEMBERS = Path("data_processed/rdd2022_zip_members.csv")
DEFAULT_SUMMARY = Path("outputs/rdd2022_archive_validation_summary.md")
DEFAULT_EXTRACT_DIR = Path("data_raw/RDD2022_extracted")
EXPECTED_FILE = "RDD2022_released_through_CRDDC2022.zip"


def load_manifest_record(manifest_path: Path, file_name: str) -> dict[str, str] | None:
    if not manifest_path.exists():
        return None
    with manifest_path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("file_name") == file_name:
                return row
    return None


def md5_file(path: Path, chunk_size: int = 1024 * 1024 * 16) -> str:
    digest = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_member_target(base: Path, member_name: str) -> Path:
    if member_name.startswith(("/", "\\")):
        raise ValueError(f"Archive member has absolute path: {member_name}")
    member_path = Path(member_name)
    if any(part == ".." for part in member_path.parts):
        raise ValueError(f"Archive member escapes extraction directory: {member_name}")
    target = (base / member_path).resolve()
    target.relative_to(base.resolve())
    return target


def write_members_csv(rows: list[dict[str, str | int]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["filename", "file_size", "compress_size", "is_dir"]
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(
    output: Path,
    zip_path: Path,
    manifest_record: dict[str, str] | None,
    size_ok: bool | None,
    md5_value: str | None,
    md5_ok: bool | None,
    zip_ok: bool | None,
    member_rows: list[dict[str, str | int]],
    extract_dir: Path | None,
    extracted: bool,
    notes: list[str],
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# RDD2022 Archive Validation Summary",
        "",
        f"- Archive path: `{zip_path}`",
        f"- Archive exists: `{zip_path.exists()}`",
    ]
    if zip_path.exists():
        lines.append(f"- Local size bytes: `{zip_path.stat().st_size}`")
    if manifest_record:
        lines.extend(
            [
                f"- Manifest expected size bytes: `{manifest_record.get('size_bytes', '')}`",
                f"- Manifest expected MD5: `{manifest_record.get('computed_md5', '')}`",
            ]
        )
    lines.extend(
        [
            f"- Size check: `{size_ok}`",
            f"- MD5 computed: `{md5_value or '[not computed]'}`",
            f"- MD5 check: `{md5_ok}`",
            f"- ZIP open/list check: `{zip_ok}`",
            f"- ZIP members listed: `{len(member_rows)}`",
            f"- Extracted this run: `{extracted}`",
        ]
    )
    if extract_dir:
        lines.append(f"- Extract directory: `{extract_dir}`")
    if member_rows:
        total_uncompressed = sum(int(row["file_size"]) for row in member_rows)
        total_compressed = sum(int(row["compress_size"]) for row in member_rows)
        lines.extend(
            [
                f"- Member uncompressed bytes: `{total_uncompressed}`",
                f"- Member compressed bytes: `{total_compressed}`",
                "",
                "## First Members",
                "",
            ]
        )
        for row in member_rows[:20]:
            lines.append(f"- `{row['filename']}` ({row['file_size']} bytes)")
    if notes:
        lines.extend(["", "## Notes", ""])
        for note in notes:
            lines.append(f"- {note}")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def list_zip_members(zip_path: Path) -> tuple[bool, list[dict[str, str | int]], list[str]]:
    notes: list[str] = []
    rows: list[dict[str, str | int]] = []
    try:
        with zipfile.ZipFile(zip_path) as zf:
            for info in zf.infolist():
                rows.append(
                    {
                        "filename": info.filename,
                        "file_size": info.file_size,
                        "compress_size": info.compress_size,
                        "is_dir": "true" if info.is_dir() else "false",
                    }
                )
    except zipfile.BadZipFile as exc:
        notes.append(f"BadZipFile: {exc}")
        return False, rows, notes
    except OSError as exc:
        notes.append(f"OSError while opening ZIP: {exc}")
        return False, rows, notes
    return True, rows, notes


def extract_zip(zip_path: Path, extract_dir: Path, allow_existing: bool) -> None:
    extract_dir.mkdir(parents=True, exist_ok=True)
    existing = list(extract_dir.iterdir())
    if existing and not allow_existing:
        raise RuntimeError(
            f"Extraction directory is not empty: {extract_dir}. "
            "Use --allow-existing-extract-dir only if this is intentional."
        )
    base = extract_dir.resolve()
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            safe_member_target(base, info.filename)
        zf.extractall(base)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and optionally extract the RDD2022 main ZIP.")
    parser.add_argument("--zip", default=str(DEFAULT_ZIP), help="Path to RDD2022 main ZIP.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="Figshare files CSV.")
    parser.add_argument("--members-csv", default=str(DEFAULT_MEMBERS), help="Output ZIP member inventory CSV.")
    parser.add_argument("--summary", default=str(DEFAULT_SUMMARY), help="Output validation summary Markdown.")
    parser.add_argument("--extract-dir", default=str(DEFAULT_EXTRACT_DIR), help="Directory for extraction.")
    parser.add_argument("--md5", action="store_true", help="Compute MD5. This can take several minutes for 13 GB.")
    parser.add_argument("--extract", action="store_true", help="Extract after validation.")
    parser.add_argument("--allow-existing-extract-dir", action="store_true", help="Allow extracting into a non-empty dir.")
    args = parser.parse_args()

    zip_path = Path(args.zip)
    manifest_path = Path(args.manifest)
    members_csv = Path(args.members_csv)
    summary_path = Path(args.summary)
    extract_dir = Path(args.extract_dir)
    notes: list[str] = []

    record = load_manifest_record(manifest_path, EXPECTED_FILE)
    if record is None:
        notes.append(f"Manifest record not found for {EXPECTED_FILE}.")

    if not zip_path.exists():
        notes.append("Archive is not present yet.")
        write_summary(summary_path, zip_path, record, None, None, None, None, [], extract_dir, False, notes)
        print(f"Archive not found: {zip_path}", file=sys.stderr)
        return 2

    size_ok: bool | None = None
    if record and record.get("size_bytes"):
        size_ok = zip_path.stat().st_size == int(record["size_bytes"])
        if not size_ok:
            notes.append("Local archive size does not match Figshare manifest.")

    md5_value: str | None = None
    md5_ok: bool | None = None
    if args.md5:
        md5_value = md5_file(zip_path)
        if record and record.get("computed_md5"):
            md5_ok = md5_value.lower() == record["computed_md5"].lower()
            if not md5_ok:
                notes.append("Local archive MD5 does not match Figshare manifest.")

    zip_ok, member_rows, zip_notes = list_zip_members(zip_path)
    notes.extend(zip_notes)
    if member_rows:
        write_members_csv(member_rows, members_csv)

    extracted = False
    if args.extract:
        if size_ok is False:
            raise SystemExit("Refusing to extract because the size check failed.")
        if md5_ok is False:
            raise SystemExit("Refusing to extract because the MD5 check failed.")
        if not zip_ok:
            raise SystemExit("Refusing to extract because ZIP listing failed.")
        extract_zip(zip_path, extract_dir, args.allow_existing_extract_dir)
        extracted = True

    write_summary(
        summary_path,
        zip_path,
        record,
        size_ok,
        md5_value,
        md5_ok,
        zip_ok,
        member_rows,
        extract_dir,
        extracted,
        notes,
    )
    print(f"ZIP open/list check: {zip_ok}; members: {len(member_rows)}; extracted: {extracted}")
    return 0 if zip_ok and size_ok is not False and md5_ok is not False else 3


if __name__ == "__main__":
    raise SystemExit(main())
