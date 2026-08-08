# ──────────────────────────────────────────────
#  Makefile for mmult C++ (Matrix Multiplication)
# ──────────────────────────────────────────────

# ── Compiler & Flags ─────────────────────────
CXX     = g++
CXXFLAGS = -Wall -O2 -std=c++17

# ── File Lists ───────────────────────────────
SRC     = mmult.cpp
OBJ     = $(SRC:.cpp=.o)
TARGET  = mmult_cpp

# ── Phony Targets ────────────────────────────
.PHONY: all clean run

# ── Default Target ───────────────────────────
all: $(TARGET)

# ── Link: object files → executable ─────────
$(TARGET): $(OBJ)
	$(CXX) $(OBJ) -o $@

# ── Compile: .cpp → .o ──────────────────────
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# ── Run with a default matrix size of 3 ─────
run: $(TARGET)
	./$(TARGET) 3

# ── Clean build artifacts ───────────────────
clean:
	rm -f $(OBJ) $(TARGET)
