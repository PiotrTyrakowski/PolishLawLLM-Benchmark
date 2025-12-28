import json
import sys
from pathlib import Path
from typing import Dict, Tuple

from src.parsers.utils.text_formatter import TextFormatter

# Fix import path - must be before any other imports
CURRENT_FILE = Path(__file__).resolve()
REPO_ROOT = CURRENT_FILE.parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import typer

from src.parsers.extractors.legal_reference_extractor import LegalReferenceExtractor
from src.parsers.parsers.legal_base_parser import LegalBaseParser

DEFAULT_JUDGMENTS_DIR = REPO_ROOT / "data" / "judgments"


def build_parser_cache(legal_base_dir: Path) -> Dict[str, LegalBaseParser]:
    """
    Preload LegalBaseParser instances for every PDF located in the provided directory.
    """
    parser_cache: Dict[str, LegalBaseParser] = {}

    for pdf_file in sorted(legal_base_dir.rglob("*.pdf")):
        code_name = pdf_file.stem.lower().replace(".", "").replace(" ", "")
        if code_name in parser_cache:
            continue
        parser_cache[code_name] = LegalBaseParser(pdf_file)

    if not parser_cache:
        raise ValueError(f"No PDF files found under {legal_base_dir}")

    return parser_cache


def extract_legal_content(
    legal_basis: str,
    extractor: LegalReferenceExtractor,
    parser_cache: Dict[str, LegalBaseParser],
) -> str:
    legal_reference = extractor.extract(legal_basis)
    if not legal_reference.article or not legal_reference.code:
        raise ValueError(f"Invalid legal basis: {legal_basis}")

    formatted_code = TextFormatter.format_code_abbreviation(legal_reference.code)
    parser = parser_cache.get(formatted_code)
    if not parser:
        raise ValueError(f"No parser available for code '{formatted_code}'")

    paragraph = legal_reference.paragraph
    point = legal_reference.point

    if paragraph and point:
        return parser.get_point(legal_reference.article, point, paragraph)
    if paragraph:
        return parser.get_paragraph(legal_reference.article, paragraph)
    if point:
        return parser.get_point(legal_reference.article, point)
    return parser.get_article(legal_reference.article)


def update_jsonl_file(
    file_path: Path,
    extractor: LegalReferenceExtractor,
    parser_cache: Dict[str, LegalBaseParser],
    dry_run: bool = False,
) -> Tuple[int, int]:
    updated_records = 0
    skipped_records = 0
    output_lines = []
    changed = False

    with file_path.open("r", encoding="utf-8") as src:
        for line_number, raw_line in enumerate(src, 1):
            stripped = raw_line.strip()
            if not stripped:
                output_lines.append(raw_line)
                continue

            try:
                record = json.loads(stripped)
            except json.JSONDecodeError as exc:
                skipped_records += 1
                typer.secho(
                    f"[{file_path.name}:{line_number}] Skipping invalid JSON: {exc}",
                    fg=typer.colors.RED,
                )
                output_lines.append(raw_line)
                continue

            if record.get("legal_basis_content"):
                output_lines.append(json.dumps(record, ensure_ascii=False))
                continue

            legal_basis = record.get("legal_basis")
            if not legal_basis:
                skipped_records += 1
                typer.secho(
                    f"[{file_path.name}:{line_number}] Missing 'legal_basis', skipping.",
                    fg=typer.colors.YELLOW,
                )
                output_lines.append(json.dumps(record, ensure_ascii=False))
                continue

            try:
                content = extract_legal_content(legal_basis, extractor, parser_cache)
                record["legal_basis_content"] = content
                updated_records += 1
                changed = True
            except Exception as exc:
                skipped_records += 1
                typer.secho(
                    f"[{file_path.name}:{line_number}] Failed to extract content: {exc}",
                    fg=typer.colors.RED,
                )

            output_lines.append(json.dumps(record, ensure_ascii=False))

    if changed and not dry_run:
        with file_path.open("w", encoding="utf-8") as dst:
            dst.write("\n".join(output_lines))
            dst.write("\n")

    return updated_records, skipped_records


def enrich_judgments(
    legal_base_dir: Path = typer.Argument(..., exists=True, file_okay=False),
    judgments_dir: Path = typer.Option(
        DEFAULT_JUDGMENTS_DIR,
        "--judgments-dir",
        "-j",
        exists=True,
        file_okay=False,
        help="Directory containing JSONL judgment files.",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would change without writing files."
    ),
):
    legal_base_dir = legal_base_dir.resolve()
    judgments_dir = judgments_dir.resolve()

    typer.echo(f"Loading legal base PDFs from: {legal_base_dir}")
    parser_cache = build_parser_cache(legal_base_dir)
    extractor = LegalReferenceExtractor()

    jsonl_files = sorted(judgments_dir.rglob("*.jsonl"))
    if not jsonl_files:
        typer.echo(f"No JSONL files found under {judgments_dir}")
        raise typer.Exit(code=1)

    total_updated = 0
    total_skipped = 0

    for jsonl_file in jsonl_files:
        typer.echo(f"Processing {jsonl_file}")
        updated, skipped = update_jsonl_file(
            jsonl_file, extractor, parser_cache, dry_run=dry_run
        )
        total_updated += updated
        total_skipped += skipped
        typer.echo(f"  ↳ Updated: {updated} record(s), Skipped: {skipped} record(s).")

    typer.echo(
        "\nSummary:\n"
        f"  • Files processed: {len(jsonl_files)}\n"
        f"  • Records updated: {total_updated}\n"
        f"  • Records skipped : {total_skipped}\n"
        f"  • Mode           : {'dry-run' if dry_run else 'write'}"
    )


if __name__ == "__main__":
    typer.run(enrich_judgments)
