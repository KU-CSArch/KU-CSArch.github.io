#!/usr/bin/env python3
import os
import argparse
from pathlib import Path

def is_binary_file(filepath, chunk_size=1024):
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(chunk_size)
            return b"\x00" in chunk
    except Exception:
        return True

def replace_in_file(filepath, old_text, new_text, encoding="utf-8", backup=False, dry_run=False):
    try:
        with open(filepath, "r", encoding=encoding) as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"[SKIP] Encoding issue, skipped: {filepath}")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to read file: {filepath} ({e})")
        return False

    if old_text not in content:
        return False

    new_content = content.replace(old_text, new_text)

    if dry_run:
        print(f"[MATCH] Would modify: {filepath}")
        return True

    try:
        if backup:
            backup_path = str(filepath) + ".bak"
            with open(backup_path, "w", encoding=encoding) as bf:
                bf.write(content)

        with open(filepath, "w", encoding=encoding) as f:
            f.write(new_content)

        print(f"[DONE] Modified: {filepath}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to write file: {filepath} ({e})")
        return False

def should_process_file(filepath, exts):
    if not filepath.is_file():
        return False
    if exts:
        return filepath.suffix in exts
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Recursively find and replace text in files under a directory."
    )
    parser.add_argument("old", help="Text to search for")
    parser.add_argument("new", help="Replacement text")
    parser.add_argument(
        "--root",
        default=".",
        help="Root directory to start searching (default: current directory)"
    )
    parser.add_argument(
        "--ext",
        nargs="*",
        default=None,
        help="Target file extensions (e.g., --ext .txt .py .md)"
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="File encoding (default: utf-8)"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create .bak backup files before modification"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show which files would be modified without changing them"
    )

    args = parser.parse_args()

    root = Path(args.root).resolve()
    exts = set(args.ext) if args.ext else None

    changed_count = 0
    checked_count = 0

    for filepath in root.rglob("*"):
        if not should_process_file(filepath, exts):
            continue

        checked_count += 1

        if is_binary_file(filepath):
            print(f"[SKIP] Binary file: {filepath}")
            continue

        changed = replace_in_file(
            filepath=filepath,
            old_text=args.old,
            new_text=args.new,
            encoding=args.encoding,
            backup=args.backup,
            dry_run=args.dry_run
        )

        if changed:
            changed_count += 1

    print("\n=== Summary ===")
    print(f"Files checked: {checked_count}")
    print(f"Files modified: {changed_count}")

if __name__ == "__main__":
    main()
