#!/usr/bin/env python3
"""Build the EduAgent RAG vector database (incremental, crash-safe).

Two modes:

``process`` — per-file
    Read each NDJSON source file, chunk, embed, and write a pair of
    intermediate cache files (``.meta.json`` + ``.vecs.bin``) atomically.
    Files already present in the cache are **skipped** (crash-safe resume).

``assemble`` — cache-only
    Read all intermediate cache files and build the final FAISS +
    LlamaIndex database.  No embedding model is loaded — pure I/O.

Usage::

    # Process source files into cache (embedding model required)
    python scripts/build_rag_db.py process \\
        --source-dir ../2_WikiDataLib/testdata \\
        --cache-dir ../2_WikiDataLib/cache

    # Assemble final database from cache (no embedding model needed)
    python scripts/build_rag_db.py assemble \\
        --cache-dir ../2_WikiDataLib/cache \\
        --output-dir ./data/faiss

    # Legacy convenience: process with defaults
    python scripts/build_rag_db.py
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

# Ensure the backend package is importable
_BACKEND = Path(__file__).resolve().parents[1]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("build_rag_db")


# ── CLI ─────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build EduAgent RAG vector database (incremental, crash-safe).",
    )
    sub = parser.add_subparsers(dest="mode", help="Operation mode")

    # ── process ────────────────────────────────────────────────────
    p_proc = sub.add_parser("process", help="Process NDJSON files into cache")
    p_proc.add_argument(
        "--source-dir", required=True,
        help="Root dir containing AA/, AB/, … wiki_* NDJSON files.",
    )
    p_proc.add_argument(
        "--cache-dir", required=True,
        help="Root dir for intermediate .meta.json + .vecs.bin (mirrors source structure).",
    )
    p_proc.add_argument(
        "--max-files", type=int, default=0,
        help="Cap number of files to process (0 = all).",
    )

    # ── assemble ───────────────────────────────────────────────────
    p_asm = sub.add_parser("assemble", help="Assemble cache into final database")
    p_asm.add_argument(
        "--cache-dir", required=True,
        help="Root dir containing intermediate .meta.json + .vecs.bin.",
    )
    p_asm.add_argument(
        "--output-dir", default=None,
        help="Where to persist the final FAISS index (default: ./data/faiss/).",
    )

    args = parser.parse_args()

    if args.mode is None:
        # Legacy: no subcommand given — run 'process' with defaults
        logger.info("No mode specified — running 'process' with defaults")
        args.mode = "process"
        args.source_dir = None
        args.cache_dir = None
        args.max_files = 0

    if args.mode == "process":
        _cmd_process(args)
    elif args.mode == "assemble":
        _cmd_assemble(args)


# ── Command implementations ─────────────────────────────────────────────


def _cmd_process(args: argparse.Namespace) -> None:
    """Process NDJSON files → cache (per-file, resumable)."""
    from app.rag.config import rag_config
    from app.rag.embedder import create_embedding_model
    from app.rag.processor import process_file

    source_dir = args.source_dir or rag_config.data_path
    cache_dir = args.cache_dir or rag_config.cache_dir

    logger.info("Mode:       process (per-file)")
    logger.info("Source dir: %s", source_dir)
    logger.info("Cache dir:  %s", cache_dir)
    logger.info("Embedding:  %s", rag_config.embedding_model)

    # Discover source files
    files = _discover_source_files(source_dir)
    if not files:
        logger.error("No wiki_* files found under %s", source_dir)
        sys.exit(1)

    if args.max_files and args.max_files > 0:
        files = files[:args.max_files]
        logger.info("Capped at %d file(s)", args.max_files)

    logger.info("Found %d source file(s) to process", len(files))

    # Load embedding model (expensive — do it once)
    embed_model = create_embedding_model(rag_config)

    # Process each file
    t0 = time.monotonic()
    processed = 0
    skipped = 0
    errors = 0
    total_records = 0
    total_chunks = 0

    for fp in files:
        # Mirror source structure under cache_dir
        rel = fp.relative_to(Path(source_dir).resolve())
        cache_subdir = Path(cache_dir).resolve() / rel.parent

        result = process_file(fp, cache_subdir, rag_config, embed_model)

        if result.error:
            errors += 1
        elif result.skipped:
            skipped += 1
        else:
            processed += 1
            total_records += result.record_count
            total_chunks += result.chunk_count

    elapsed = time.monotonic() - t0

    # Summary
    print("\n" + "=" * 56)
    print("  Process Summary")
    print("=" * 56)
    print(f"  Files processed : {processed:>6,d}")
    print(f"  Files skipped   : {skipped:>6,d}")
    print(f"  Files with error: {errors:>6,d}")
    print(f"  Total records   : {total_records:>6,d}")
    print(f"  Total chunks    : {total_chunks:>6,d}")
    print(f"  Elapsed time    : {elapsed:>6.1f} s")
    print("=" * 56)

    if errors > 0:
        sys.exit(1)


def _cmd_assemble(args: argparse.Namespace) -> None:
    """Assemble cache files → final FAISS database."""
    from app.rag.assembler import assemble_index
    from app.rag.config import rag_config

    cache_dir = args.cache_dir or rag_config.cache_dir
    output_dir = args.output_dir

    logger.info("Mode:       assemble (cache → DB)")
    logger.info("Cache dir:  %s", cache_dir)
    logger.info("Output dir: %s", output_dir or "(default)")

    result = assemble_index(rag_config, cache_dir, output_dir)

    if result.errors:
        for err in result.errors:
            logger.error("ASSEMBLY ERROR: %s", err)

    print("\n" + "=" * 56)
    print("  Assembly Summary")
    print("=" * 56)
    print(f"  Files loaded    : {result.files_loaded:>6,d}")
    print(f"  Files skipped   : {result.files_skipped:>6,d}")
    print(f"  Total chunks    : {result.total_chunks:>6,d}")
    print(f"  Total vectors   : {result.total_vectors:>6,d}")
    print(f"  Collection      : {result.collection}")
    print(f"  Elapsed time    : {result.elapsed_seconds:>6.1f} s")
    print("=" * 56)

    if result.errors and result.total_vectors == 0:
        sys.exit(1)


# ── Helpers ─────────────────────────────────────────────────────────────


def _discover_source_files(source_dir: str) -> list[Path]:
    """Find all ``wiki_*`` NDJSON files under *source_dir*."""
    root = Path(source_dir).resolve()
    if not root.exists():
        logger.error("Source directory not found: %s", root)
        return []

    files: list[Path] = []
    for sub in sorted(root.iterdir()):
        if sub.is_dir():
            for entry in sorted(sub.iterdir()):
                if entry.is_file() and entry.name.startswith("wiki_"):
                    files.append(entry)
    return files


if __name__ == "__main__":
    main()
