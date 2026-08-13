"""Extract an Excel column into a JSON or YAML string list."""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile


RELATIONSHIP_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def _xml(archive: ZipFile, member: str):
    return ET.fromstring(archive.read(member))


def _shared_strings(archive: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = _xml(archive, "xl/sharedStrings.xml")
    return ["".join(node.text or "" for node in item.findall(".//{*}t")) for item in root.findall("{*}si")]


def _sheet_path(target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(posixpath.join("xl", target))


def _sheet_records(archive: ZipFile):
    workbook = _xml(archive, "xl/workbook.xml")
    relationships = _xml(archive, "xl/_rels/workbook.xml.rels")
    targets = {item.get("Id"): item.get("Target") for item in relationships}
    return [(sheet.get("name"), _sheet_path(targets[sheet.get(RELATIONSHIP_ID)])) for sheet in workbook.findall(".//{*}sheet")]


def _cell_text(cell, shared: list[str]) -> str:
    if cell.get("t") == "inlineStr":
        return "".join(node.text or "" for node in cell.findall(".//{*}t"))
    value = cell.find("{*}v")
    raw = value.text if value is not None and value.text is not None else ""
    if cell.get("t") == "s" and raw:
        return shared[int(raw)]
    return "TRUE" if cell.get("t") == "b" and raw == "1" else raw


def _column_index(reference: str) -> int:
    letters = re.match(r"[A-Za-z]+", reference or "")
    if not letters:
        return -1
    result = 0
    for letter in letters.group().upper():
        result = result * 26 + ord(letter) - 64
    return result - 1


def _row_values(row, shared: list[str]) -> dict[int, str]:
    return {_column_index(cell.get("r")): _cell_text(cell, shared) for cell in row.findall("{*}c")}


def _sheet_rows(root, shared: list[str]):
    return [_row_values(row, shared) for row in root.findall(".//{*}sheetData/{*}row")]


def _header_column(row: dict[int, str], column_header: str):
    expected = str(column_header).strip().casefold()
    return next((column for column, value in row.items() if str(value).strip().casefold() == expected), None)


def _remaining_values(rows, start: int, column: int) -> list[str]:
    values = (str(row.get(column, "")).strip() for row in rows[start:])
    return [value for value in values if value]


def _column_values(root, shared: list[str], column_header: str):
    rows = _sheet_rows(root, shared)
    for index, row in enumerate(rows):
        column = _header_column(row, column_header)
        if column is not None:
            return _remaining_values(rows, index + 1, column)
    return None


def _selected_sheets(records, sheet_name: str | None):
    if sheet_name is None:
        return records
    selected = [record for record in records if record[0] == sheet_name]
    if not selected:
        raise ValueError(f"Worksheet not found: {sheet_name}")
    return selected


def _read_xlsx(path: Path, column_header: str, sheet_name: str | None) -> list[str]:
    with ZipFile(path) as archive:
        shared = _shared_strings(archive)
        for _, member in _selected_sheets(_sheet_records(archive), sheet_name):
            values = _column_values(_xml(archive, member), shared, column_header)
            if values is not None:
                return values
    raise ValueError(f"Column header not found: {column_header}")


def read_excel_column(workbook_path: str | Path, column_header: str, *, sheet_name: str | None = None):
    """Read all nonblank values below a header from an Excel workbook."""
    path = Path(workbook_path)
    if path.suffix.lower() == ".xls":
        raise ValueError("Legacy .xls is unsupported; save the workbook as .xlsx first")
    if path.suffix.lower() not in {".xlsx", ".xlsm"}:
        raise ValueError("Workbook must use the .xlsx or .xlsm format")
    return _read_xlsx(path, column_header, sheet_name)


def _yaml_list(values: list[str]) -> str:
    return "\n".join(f"- {json.dumps(value, ensure_ascii=False)}" for value in values) + "\n"


def write_name_list(values: list[str], output_path: str | Path) -> None:
    """Write names as JSON or YAML, selected by the output extension."""
    path = Path(output_path)
    if path.suffix.lower() == ".json":
        text = json.dumps(values, indent=2, ensure_ascii=False) + "\n"
    elif path.suffix.lower() in {".yaml", ".yml"}:
        text = _yaml_list(values)
    else:
        raise ValueError("Output must use the .json, .yaml, or .yml extension")
    path.write_text(text, encoding="utf-8")


def xls_to_list(workbook_path: str | Path, column_header: str, output_path: str | Path):
    """Extract a named Excel column, write it as a list, and return the list."""
    values = read_excel_column(workbook_path, column_header)
    write_name_list(values, output_path)
    return values


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", help="Input .xlsx or .xlsm workbook")
    parser.add_argument("column_header", help="Header of the column to extract")
    parser.add_argument("output", help="Output .json, .yaml, or .yml file")
    parser.add_argument("--sheet", help="Optional worksheet name")
    return parser


def main() -> int:
    args = _argument_parser().parse_args()
    values = read_excel_column(args.workbook, args.column_header, sheet_name=args.sheet)
    write_name_list(values, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
