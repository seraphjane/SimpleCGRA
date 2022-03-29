DEBUG    := 1
LOGLEVEL := 0
include Options.mk

COMMON_OBJECTS := $(addprefix ./build/objects/, Common.o Logger.o HyperGraph.o HierGraph.o)
UTIL_OBJECTS := $(addprefix ./build/objects/, NetworkAnalyzer.o VanillaMatcher.o NOrderValidator.o VanillaValidator.o)
OBJECTS := $(COMMON_OBJECTS) $(UTIL_OBJECTS)
TEST_EXECS := $(addprefix ./build/, test0)
EXECUTABLES := $(TEST_EXECS)
LLVMPASS_LIBS := $(addprefix ./build/, libPassModule2DFG.so)
LIBRARIES := $(LLVMPASS_LIBS)

all: info $(EXECUTABLES) $(LIBRARIES)

info:
	@echo "============================================="
	@echo "INFO: CXX: \t \t $(CXX)"
	@echo "INFO: DEBUG: \t \t $(DEBUG)"
	@echo "INFO: LOGLEVEL: \t $(LOGLEVEL)"
	@echo "INFO: CXX_FLAGS: \t $(CXX_FLAGS)"
	@echo "INFO: COMMON_OBJECTS: \t $(COMMON_OBJECTS)"
	@echo "INFO: TEST_EXECS: \t $(TEST_EXECS)"
	@echo "============================================="
	@echo ""

$(COMMON_OBJECTS):./build/objects/%.o: ./common/%.cpp ./common/%.h
	$(CXX) $(CXX_FLAGS) -c $< -o $@

$(UTIL_OBJECTS):./build/objects/%.o: ./util/%.cpp ./util/%.h
	$(CXX) $(CXX_FLAGS) -c $< -o $@

$(TEST_EXECS):./build/%: ./test/%.cpp $(OBJECTS)
	$(CXX) $(CXX_FLAGS) $< $(OBJECTS) -o $@

$(LLVMPASS_LIBS):./build/%.so: ./dataflow/%.cpp ./dataflow/%.h  $(OBJECTS)
	$(CXX) $(CXX_FLAGS) `llvm-config --cxxflags` `llvm-config --ldflags` -Wl,-znodelete -fno-rtti -shared $<  $(OBJECTS) -o $@

.PHONY: clean
clean: 
	@rm $(OBJECTS) $(EXECUTABLES) $(LIBRARIES)
