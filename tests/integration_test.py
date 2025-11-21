from pathlib import Path

import pytest

from src.sofun.sofun import (
    find_section,
    list_dynamic_symbols,
    parse_sections,
    read_elf_header,
)


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "test_data"


def test_header_metadata_reads_expected_sizes():
    lib_path = FIXTURE_DIR / "libmath_utils.so"
    with lib_path.open("rb") as handle:
        header = read_elf_header(handle)

    assert header.e_shoff > 0
    assert header.e_shnum > 0
    assert header.e_shentsize == 64


def test_section_parsing_includes_known_entries():
    lib_path = FIXTURE_DIR / "libmath_utils.so"
    with lib_path.open("rb") as handle:
        header = read_elf_header(handle)
        sections = parse_sections(handle, header)

    names = {section.name for section in sections}
    assert {".dynsym", ".dynstr", ".text", ".shstrtab"}.issubset(names)
    assert sections[header.e_shstrndx].name == ".shstrtab"
    with pytest.raises(ValueError):
        _ = find_section(sections, ".does_not_exist")


def test_dynamic_symbols_include_exported_math_functions():
    lib_path = FIXTURE_DIR / "libmath_utils.so"
    with lib_path.open("rb") as handle:
        header = read_elf_header(handle)
        sections = parse_sections(handle, header)
        dynsym = find_section(sections, ".dynsym")
        dynstr = find_section(sections, ".dynstr")
        symbols = list_dynamic_symbols(handle, dynsym, dynstr)

    exported = {"add", "subtract", "multiply", "divide", "factorial"}
    assert exported.issubset(symbols)
    assert symbols[0] == ""


def test_dynamic_symbols_for_strings_library():
    lib_path = FIXTURE_DIR / "libstring_utils.so"
    with lib_path.open("rb") as handle:
        header = read_elf_header(handle)
        sections = parse_sections(handle, header)
        dynsym = find_section(sections, ".dynsym")
        dynstr = find_section(sections, ".dynstr")
        symbols = list_dynamic_symbols(handle, dynsym, dynstr)

    exported = {
        "reverse_string",
        "to_uppercase",
        "string_length",
        "is_palindrome",
    }
    assert exported.issubset(symbols)
