import sys
from io import BufferedReader

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
ST_INFO_OFF = 0x4
ST_INFO_SZ = 0x1
ST_NDX_OFF = 0x6
ST_NDX_SZ = 0x2
ST_INFO_TYPE_MASK = 0x0F
ST_INFO_TYPE_FUNC = 0x2
SHT_HASH = 0x5

SHT_SYMTAB = 0x2


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
    # print(hex(off))
    b = f.read(1)
    bs = bytearray()
    while b and b[0] != 0x0:
        bs.extend(b)
        b = f.read(1)
    return bs.decode()


def main():
    if len(sys.argv) != 2:
        print("sofun.py <input file>")
        exit(-1)

    input_file: str = sys.argv[1]
    print(f"{input_file}:")
    handle = open(input_file, "rb")

    # Read the global ELF header
    e_shoff = get_e_shoff(handle)
    e_shnum = get_e_shnum(handle)
    e_shstrndx = get_e_shstrndx(handle)
    e_shentsize = get_e_shentsize(handle)
    print(f"e_shoff: {hex(e_shoff)}")
    print(f"e_shnum: {e_shnum}")
    print(f"e_shstrndx: {e_shstrndx}")
    print(f"e_shentsize: {e_shentsize}")

    off = e_shoff
    offs: list[int] = []
    name_offs: list[int] = []
    # First pass: collect all segment header offsets
    for _ in range(0, e_shnum):
        offs.append(off)
        name_offs.append(read_int(handle, off, SH_NAME_SZ))
        off += e_shentsize
    # Find address of string segment
    strseg_off = read_int(handle, offs[e_shstrndx] + SH_OFF_OFF, SH_NAME_SZ)
    print(f"shstr: {hex(strseg_off)}")

    # Locate symtab segment which contains all the segment names
    names: list[str] = []
    for off in name_offs:
        names.append(read_str(handle, strseg_off + off))

    # Find the symbol table segment
    # We can re-traverse again to look for SHT_SYMTAB but meh
    symtab_off = offs[names.index(".symtab")]
    assert read_int(handle, symtab_off + SH_TYPE_OFF, SH_TYPE_SZ) == SHT_SYMTAB
    symtab = read_int(handle, symtab_off + SH_OFF_OFF, SH_OFF_SZ)
    print(f".symtab: {hex(symtab)}")

    # Find strtab containing the function names
    strtab_off = offs[names.index(".strtab")]
    strtab = read_int(handle, strtab_off + SH_OFF_OFF, SH_OFF_SZ)
    print(f".strtab: {hex(strtab)}")

    symtab_size = read_int(handle, symtab_off + SH_SIZE_OFF, SH_SIZE_SZ)

    # Traverse symtab, check type and print names if match
    print("\nSymbols found:")
    for i in range(0, int(symtab_size / ST_SIZE)):
        entry_off = symtab + i * ST_SIZE
        name_off = read_int(handle, entry_off + ST_NAME_OFF, ST_NAME_SZ)
        info = read_int(handle, entry_off + ST_INFO_OFF, ST_INFO_SZ)
        ndx = read_int(handle, entry_off + ST_NDX_OFF, ST_NDX_SZ)
        if (info & ST_INFO_TYPE_MASK) == ST_INFO_TYPE_FUNC and ndx == SHT_HASH:
            name = read_str(handle, strtab + name_off)
            print(name)

    handle.close()


if __name__ == "__main__":
    main()
