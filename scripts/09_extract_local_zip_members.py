"""Extract RDD2022 outer ZIP members by scanning local file headers.

The Figshare RDD2022 archive has been observed to match the official MD5 while
failing central-directory based ZIP readers. Its payload is a sequence of
stored inner ZIP files. This script reads local file headers directly and
extracts those inner ZIP members without relying on the central directory.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
from pathlib import Path, PurePosixPath
import struct
from typing import BinaryIO


LOCAL_SIG = b"PK\x03\x04"
CENTRAL_SIG = b"PK\x01\x02"
END_SIG = b"PK\x05\x06"
LOCAL_HEADER = struct.Struct("<4s5H3I2H")


def zip64_sizes(extra: bytes, need_uncompressed: bool, need_compressed: bool) -> tuple[int | None, int | None]:
    """Return uncompressed/compressed ZIP64 sizes from a local-header extra field."""
    cursor = 0
    while cursor + 4 <= len(extra):
        header_id, data_size = struct.unpack_from("<HH", extra, cursor)
        cursor += 4
        data = extra[cursor : cursor + data_size]
        cursor += data_size
        if header_id != 0x0001:
            continue
        pos = 0
        uncomp = comp = None
        if need_uncompressed:
            if pos + 8 > len(data):
                raise ValueError("truncated ZIP64 uncompressed size")
            uncomp = struct.unpack_from("<Q", data, pos)[0]
            pos += 8
        if need_compressed:
            if pos + 8 > len(data):
                raise ValueError("truncated ZIP64 compressed size")
            comp = struct.unpack_from("<Q", data, pos)[0]
        return uncomp, comp
    return None, None


def safe_member_path(name: str) -> Path:
    posix = PurePosixPath(name)
    if posix.is_absolute() or ".." in posix.parts:
        raise ValueError(f"unsafe member path: {name!r}")
    return Path(*posix.parts)


def iter_local_members(handle: BinaryIO):
    index = 0
    while True:
        offset = handle.tell()
        sig = handle.read(4)
        if not sig:
            return
        if sig in {CENTRAL_SIG, END_SIG}:
            return
        if sig != LOCAL_SIG:
            raise ValueError(f"unexpected signature at offset {offset}: {sig!r}")
        rest = handle.read(LOCAL_HEADER.size - 4)
        if len(rest) != LOCAL_HEADER.size - 4:
            raise ValueError(f"truncated local header at offset {offset}")
        fields = LOCAL_HEADER.unpack(sig + rest)
        (
            _signature,
            _version_needed,
            flags,
            method,
            _mtime,
            _mdate,
            crc32,
            compressed_size,
            uncompressed_size,
            name_len,
            extra_len,
        ) = fields
        name_bytes = handle.read(name_len)
        extra = handle.read(extra_len)
        if len(name_bytes) != name_len or len(extra) != extra_len:
            raise ValueError(f"truncated name/extra at offset {offset}")
        name = name_bytes.decode("utf-8", errors="replace")
        need_uncomp64 = uncompressed_size == 0xFFFFFFFF
        need_comp64 = compressed_size == 0xFFFFFFFF
        if need_uncomp64 or need_comp64:
            uncomp64, comp64 = zip64_sizes(extra, need_uncomp64, need_comp64)
            if need_uncomp64:
                if uncomp64 is None:
                    raise ValueError(f"missing ZIP64 uncompressed size for {name}")
                uncompressed_size = uncomp64
            if need_comp64:
                if comp64 is None:
                    raise ValueError(f"missing ZIP64 compressed size for {name}")
                compressed_size = comp64
        data_offset = handle.tell()
        yield {
            "index": index,
            "offset": offset,
            "name": name,
            "flags": flags,
            "method": method,
            "crc32_header": f"{crc32:08x}",
            "compressed_size": compressed_size,
            "uncompressed_size": uncompressed_size,
            "data_offset": data_offset,
        }
        handle.seek(data_offset + compressed_size, os.SEEK_SET)
        index += 1


def copy_member(source: BinaryIO, member: dict, out_path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    source.seek(member["data_offset"])
    remaining = int(member["compressed_size"])
    md5 = hashlib.md5()
    with out_path.open("wb") as out:
        while remaining:
            chunk = source.read(min(chunk_size, remaining))
            if not chunk:
                raise ValueError(f"unexpected EOF while extracting {member['name']}")
            out.write(chunk)
            md5.update(chunk)
            remaining -= len(chunk)
    return md5.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract local-header ZIP members from the RDD2022 outer archive.")
    parser.add_argument("--zip", required=True, help="Path to the RDD2022 outer archive.")
    parser.add_argument("--out", required=True, help="Directory for extracted inner members.")
    parser.add_argument("--manifest", required=True, help="CSV manifest output path.")
    parser.add_argument("--extract", action="store_true", help="Write member payloads to --out.")
    args = parser.parse_args()

    zip_path = Path(args.zip)
    out_dir = Path(args.out)
    manifest_path = Path(args.manifest)
    rows: list[dict] = []

    with zip_path.open("rb") as handle:
        for member in iter_local_members(handle):
            if member["flags"] & 0x08:
                raise ValueError(f"data-descriptor members are not supported: {member['name']}")
            if member["method"] != 0:
                raise ValueError(f"compressed members are not supported yet: {member['name']} method={member['method']}")
            relative = safe_member_path(member["name"])
            out_path = out_dir / relative
            row = dict(member)
            row["extracted_path"] = str(out_path) if args.extract else ""
            row["payload_md5"] = ""
            if args.extract and not member["name"].endswith("/"):
                row["payload_md5"] = copy_member(handle, member, out_path)
            rows.append(row)

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "index",
        "offset",
        "name",
        "flags",
        "method",
        "crc32_header",
        "compressed_size",
        "uncompressed_size",
        "data_offset",
        "extracted_path",
        "payload_md5",
    ]
    with manifest_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    total = sum(int(r["compressed_size"]) for r in rows)
    print(f"members={len(rows)} payload_bytes={total} extract={args.extract}")
    for row in rows:
        print(f"{row['index']}: {row['name']} bytes={row['compressed_size']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
