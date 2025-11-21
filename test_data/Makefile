CC = gcc
CFLAGS = -Wall -Wextra -fPIC -g
LDFLAGS = -shared

MATH_OBJ = math_utils.o
STRING_OBJ = string_utils.o

MATH_SO = libmath_utils.so
STRING_SO = libstring_utils.so

all: $(MATH_SO) $(STRING_SO)

$(MATH_SO): $(MATH_OBJ)
	$(CC) $(LDFLAGS) -o $@ $^

$(STRING_SO): $(STRING_OBJ)
	$(CC) $(LDFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f *.o *.so $(MAIN_EXE)

info:
	@echo "=== Math Library Info ==="
	readelf -s $(MATH_SO) | grep FUNC || true
	@echo "=== String Library Info ==="  
	readelf -s $(STRING_SO) | grep FUNC || true

.PHONY: all clean info
