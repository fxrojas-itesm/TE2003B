# ──────────────────────────────────────────────
#  Makefile for mmult (Matrix Multiplication)
# ──────────────────────────────────────────────

# ── Compiler & Flags ─────────────────────────
CC      = gcc
CFLAGS  = -Wall -O2

# ── File Lists ───────────────────────────────
SRC     = mmult.c
OBJ     = $(SRC:.c=.o)
TARGET  = mmult

# ── Phony Targets ────────────────────────────
.PHONY: all clean run

# ── Default Target ───────────────────────────
all: $(TARGET)

# ── Link: object files → executable ─────────
$(TARGET): $(OBJ)
	$(CC) $(OBJ) -o $@

# ── Compile: .c → .o ────────────────────────
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# ── Run with a default matrix size of 3 ─────
run: $(TARGET)
	./$(TARGET) 3

# ── Clean build artifacts ───────────────────
clean:
	rm -f $(OBJ) $(TARGET)
