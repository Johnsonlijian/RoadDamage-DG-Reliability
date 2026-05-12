from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


FIGSHARE_API = "https://api.figshare.com/v2/articles/{article_id}"


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "IMUT-RoadDamage-DG/0.1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def write_files_csv(article: dict, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "article_id",
        "title",
        "file_id",
        "file_name",
        "size_bytes",
        "download_url",
        "computed_md5",
    ]
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for item in article.get("files", []):
            writer.writerow(
                {
                    "article_id": article.get("id", ""),
                    "title": article.get("title", ""),
                    "file_id": item.get("id", ""),
                    "file_name": item.get("name", ""),
                    "size_bytes": item.get("size", ""),
                    "download_url": item.get("download_url", ""),
                    "computed_md5": item.get("computed_md5", ""),
                }
            )


def write_summary(article: dict, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    files = article.get("files", [])
    total_size = sum(int(item.get("size") or 0) for item in files)
    lines = [
        "# Figshare Article Metadata",
        "",
        f"- Article ID: {article.get('id', '')}",
        f"- Title: {article.get('title', '')}",
        f"- DOI: {article.get('doi', '')}",
        f"- URL: {article.get('url_public_html', '')}",
        f"- License: {article.get('license', {}).get('name', '')}",
        f"- Version: {article.get('version', '')}",
        f"- Published date: {article.get('published_date', '')}",
        f"- Files: {len(files)}",
        f"- Total file size bytes: {total_size}",
        "",
        "## Files",
        "",
        "| File | Size bytes | MD5 |",
        "| --- | ---: | --- |",
    ]
    for item in files:
        lines.append(
            f"| {item.get('name', '')} | {item.get('size', '')} | {item.get('computed_md5', '')} |"
        )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_download_script(files_csv: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    text = f"""# Download RDD2022 files listed in {files_csv.name}
# Review file sizes before running. This script can download large files.

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$CsvPath = Join-Path $ProjectRoot "data_processed\\rdd2022_figshare_files.csv"
$OutDir = Join-Path $ProjectRoot "data_raw\\RDD2022"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Import-Csv -LiteralPath $CsvPath | ForEach-Object {{
  $target = Join-Path $OutDir $_.file_name
  if (Test-Path -LiteralPath $target) {{
    Write-Host "exists: $target"
  }} else {{
    Write-Host "downloading: $($_.file_name)"
    Invoke-WebRequest -Uri $_.download_url -OutFile $target
  }}
}}
"""
    output.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch RDD2022 figshare article metadata.")
    parser.add_argument("--article-id", default="21431547", help="Figshare article id.")
    parser.add_argument("--json", required=True, help="Output JSON path.")
    parser.add_argument("--files-csv", required=True, help="Output files CSV path.")
    parser.add_argument("--summary", required=True, help="Output Markdown summary path.")
    parser.add_argument("--download-script", required=True, help="Output PowerShell download script path.")
    args = parser.parse_args()

    url = FIGSHARE_API.format(article_id=args.article_id)
    try:
        article = fetch_json(url)
    except urllib.error.URLError as exc:
        print(f"Could not fetch figshare metadata from {url}: {exc}", file=sys.stderr)
        return 2

    json_path = Path(args.json)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(article, indent=2, ensure_ascii=False), encoding="utf-8")
    files_csv = Path(args.files_csv)
    write_files_csv(article, files_csv)
    write_summary(article, Path(args.summary))
    write_download_script(files_csv, Path(args.download_script))
    print(f"Fetched figshare metadata for article {args.article_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

