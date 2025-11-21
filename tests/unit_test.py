from io import BytesIO

import pytest

from src.sofun.sofun import (
    SH_OFF_OFF,
    SH_OFF_SZ,
    SH_SIZE_OFF,
    SH_SIZE_SZ,
    ST_NAME_OFF,
    ST_NAME_SZ,
    ST_SIZE,
    Section,
    find_section,
    list_dynamic_symbols,
    parse_sections,
    read_elf_header,
    read_int,
    read_str,
)


def _write_int(buf: bytearray, offset: int, value: int, size: int) -> None:
    buf[offset : offset + size] = value.to_bytes(size, "little")


def _build_in_memory_elf() -> BytesIO:
    data = bytearray(1024)

    e_shoff = 0x100
    e_shnum = 2
    e_shstrndx = 1
    e_shentsize = 0x40

    _write_int(data, 0x28, e_shoff, 8)
    _write_int(data, 0x3C, e_shnum, 2)
    _write_int(data, 0x3A, e_shentsize, 2)
    _write_int(data, 0x3E, e_shstrndx, 2)

    strtab_offset = 0x300
    strtab = b"\x00.text\x00.shstrtab\x00"

    _write_int(data, e_shoff, 1, 4)
    _write_int(data, e_shoff + SH_OFF_OFF, 0x200, SH_OFF_SZ)
    _write_int(data, e_shoff + SH_SIZE_OFF, 0x10, SH_SIZE_SZ)

    second_header = e_shoff + e_shentsize
    _write_int(data, second_header, 7, 4)
    _write_int(data, second_header + SH_OFF_OFF, strtab_offset, SH_OFF_SZ)
    _write_int(data, second_header + SH_SIZE_OFF, len(strtab), SH_SIZE_SZ)

    data[strtab_offset : strtab_offset + len(strtab)] = strtab

    return BytesIO(bytes(data))


def test_read_helpers_respect_offsets_and_terminators():
    buf = bytearray(32)
    _write_int(buf, 4, 0x1234ABCD, 4)
    buf[16:22] = b"hello\x00"
    handle = BytesIO(bytes(buf))

    assert read_int(handle, 4, 4) == 0x1234ABCD
    assert read_str(handle, 16) == "hello"


def test_parse_sections_works_against_in_memory_layout():
    handle = _build_in_memory_elf()
    header = read_elf_header(handle)

    sections = parse_sections(handle, header)

    assert [sec.name for sec in sections] == [".text", ".shstrtab"]
    text = find_section(sections, ".text")
    assert text.file_offset == 0x200
    assert text.size == 0x10
    assert sections[header.e_shstrndx].name == ".shstrtab"
    with pytest.raises(ValueError):
        _ = find_section(sections, ".missing")


def test_list_dynamic_symbols_reads_offsets_from_dynsym_table():
    dynstr = b"\x00alpha\x00beta\x00"
    dynsym_entries = bytearray(ST_SIZE * 3)
    _write_int(dynsym_entries, ST_NAME_OFF, 0, ST_NAME_SZ)
    _write_int(dynsym_entries, ST_SIZE + ST_NAME_OFF, 1, ST_NAME_SZ)
    _write_int(dynsym_entries, (2 * ST_SIZE) + ST_NAME_OFF, 7, ST_NAME_SZ)

    blob = bytearray(256)
    dynsym_offset = 0x20
    dynstr_offset = 0x80
    blob[dynsym_offset : dynsym_offset + len(dynsym_entries)] = dynsym_entries
    blob[dynstr_offset : dynstr_offset + len(dynstr)] = dynstr
    handle = BytesIO(bytes(blob))

    dynsym_section = Section(
        name=".dynsym",
        header_offset=0,
        name_offset=0,
        file_offset=dynsym_offset,
        size=len(dynsym_entries),
    )
    dynstr_section = Section(
        name=".dynstr",
        header_offset=0,
        name_offset=0,
        file_offset=dynstr_offset,
        size=len(dynstr),
    )

    symbols = list_dynamic_symbols(handle, dynsym_section, dynstr_section)

    assert symbols == ["", "alpha", "beta"]
