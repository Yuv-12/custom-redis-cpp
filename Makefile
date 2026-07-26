CXX = g++
CXXFLAGS = -Wall -Wextra -O2 -std=c++17

SRC = src/main.cpp src/avl.cpp src/hashtable.cpp src/zset.cpp src/heap.cpp src/thread_pool.cpp
OBJ = $(SRC:.cpp=.o)
TARGET = redis_server

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJ) -pthread

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(OBJ) $(TARGET)
