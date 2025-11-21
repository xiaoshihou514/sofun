import sys
from dataclasses import dataclass
from io import BufferedReader
from collections.abc import Iterable


# https://en.wikipedia.org/wiki/Executable_and_Linkable_Format

SH_NAME_SZ = 0x4
SH_SIZE_OFF = 0x20
SH_SIZE_SZ = 0x8
SH_OFF_OFF = 0x18
SH_OFF_SZ = 0x8
SH_TYPE_OFF = 0x4
SH_TYPE_SZ = 0x4

# /usr/include/elf.h
ST_SIZE = 24
ST_NAME_OFF = 0x0
ST_NAME_SZ = 0x4


def get_e_shoff(f: BufferedReader) -> int:
    return read_int(f, 0x28, 0x8)


def get_e_shnum(f: BufferedReader) -> int:
    return read_int(f, 0x3C, 0x2)


def get_e_shstrndx(f: BufferedReader) -> int:
    return read_int(f, 0x3E, 0x2)


def get_e_shentsize(f: BufferedReader) -> int:
    return read_int(f, 0x3A, 0x2)


def read_int(f: BufferedReader, off: int, nb: int) -> int:
    _ = f.seek(off)
    return int.from_bytes(f.read(nb), "little")


def read_str(f: BufferedReader, off: int) -> str:
    _ = f.seek(off)
    b = f.read(1)
    bs = bytearray()
    while b and b[0] != 0x0:
        bs.extend(b)
        b = f.read(1)
    return bs.decode()


@dataclass
class ElfHeader:
    e_shoff: int
    e_shnum: int
    e_shstrndx: int
    e_shentsize: int


@dataclass
class Section:
    name: str
    header_offset: int
    name_offset: int
    file_offset: int
    size: int


def read_elf_header(f: BufferedReader) -> ElfHeader:
    return ElfHeader(
        e_shoff=get_e_shoff(f),
        e_shnum=get_e_shnum(f),
        e_shstrndx=get_e_shstrndx(f),
        e_shentsize=get_e_shentsize(f),
    )


def _collect_section_offsets(header: ElfHeader) -> Iterable[int]:
    off = header.e_shoff
    for _ in range(0, header.e_shnum):
        yield off
        off += header.e_shentsize


def parse_sections(f: BufferedReader, header: ElfHeader) -> list[Section]:
    section_offsets = list(_collect_section_offsets(header))
    name_offsets = [read_int(f, off, SH_NAME_SZ) for off in section_offsets]
    strtab_offset = read_int(
        f, section_offsets[header.e_shstrndx] + SH_OFF_OFF, SH_NAME_SZ
    )

    sections: list[Section] = []
    for header_offset, name_offset in zip(section_offsets, name_offsets):
        name = read_str(f, strtab_offset + name_offset)
        file_offset = read_int(f, header_offset + SH_OFF_OFF, SH_OFF_SZ)
        size = read_int(f, header_offset + SH_SIZE_OFF, SH_SIZE_SZ)
        sections.append(
            Section(
                name=name,
                header_offset=header_offset,
                name_offset=name_offset,
                file_offset=file_offset,
                size=size,
            )
        )
    return sections


def find_section(sections: list[Section], name: str) -> Section:
    for section in sections:
        if section.name == name:
            return section
    raise ValueError(f"Section {name} not found")


def list_dynamic_symbols(
    f: BufferedReader, dynsym: Section, dynstr: Section
) -> list[str]:
    symbols: list[str] = []
    for i in range(0, int(dynsym.size / ST_SIZE)):
        entry_off = dynsym.file_offset + i * ST_SIZE
        name_off = read_int(f, entry_off + ST_NAME_OFF, ST_NAME_SZ)
        symbols.append(read_str(f, dynstr.file_offset + name_off))
    return symbols


def main():
    if len(sys.argv) != 2:
        print("sofun.py <input file>")
        exit(-1)

    input_file: str = sys.argv[1]
    print(f"{input_file}:")
    handle = open(input_file, "rb")

    header = read_elf_header(handle)
    print(f"e_shoff: {hex(header.e_shoff)}")
    print(f"e_shnum: {header.e_shnum}")
    print(f"e_shstrndx: {header.e_shstrndx}")
    print(f"e_shentsize: {header.e_shentsize}")

    sections = parse_sections(handle, header)

    print("\nFound the following segments:")
    for section in sections:
        print(f"{section.name}: {hex(section.file_offset)}")

    dynsym = find_section(sections, ".dynsym")
    dynstr = find_section(sections, ".dynstr")
    print(f".dynsym: {hex(dynsym.file_offset)}")
    print(f".dynstr: {hex(dynstr.file_offset)}")

    print("\nSymbols found:")
    for name in list_dynamic_symbols(handle, dynsym, dynstr):
        print(name)

    handle.close()


if __name__ == "__main__":
    main()
