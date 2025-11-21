import sys
from io import BufferedReader

# https://en.wikipedia.org/wiki/Executable_and_Linkable_Format
SH_OFF_OFF = 0x28
SH_OFF_SZ = 0x8
SH_NUM_OFF = 0x3C
SH_NUM_SZ = 0x2
SH_STR_OFF = 0x3E
SH_STR_SZ = 0x2

SH_NAME_SZ = 0x4
SH_SIZE_OFF = 0x20
SH_SIZE_SZ = 0x8

SHENT_SIZE_OFF = 0x3A
SHENT_SIZE_SZ = 0x2


def read_int(f: BufferedReader, off: int, nb: int) -> int:
    _ = f.seek(off)
    return int.from_bytes(f.read(nb), "little")


def read_str(f: BufferedReader, off: int) -> str:
    _ = f.seek(off)
    print(hex(off))
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

    e_shoff = read_int(handle, SH_OFF_OFF, SH_OFF_SZ)
    e_shnum = read_int(handle, SH_NUM_OFF, SH_NUM_SZ)
    e_shstrndx = read_int(handle, SH_STR_OFF, SH_STR_SZ)
    e_shentsize = read_int(handle, SHENT_SIZE_OFF, SHENT_SIZE_SZ)
    print(f"e_shoff: {hex(e_shoff)}")
    print(f"e_shnum: {e_shnum}")
    print(f"e_shstrndx: {e_shstrndx}")
    print(f"e_shentsize: {e_shentsize}")

    off = e_shoff
    offs: list[int] = []
    name_offs: list[int] = []
    for _ in range(0, e_shnum):
        offs.append(off)
        name_offs.append(read_int(handle, off, SH_NAME_SZ))
        off += e_shentsize
    strseg_off = offs[e_shstrndx]
    print(f"str seg: {hex(strseg_off)}")

    for off in name_offs:
        print(read_str(handle, strseg_off + off))

    handle.close()


if __name__ == "__main__":
    main()
