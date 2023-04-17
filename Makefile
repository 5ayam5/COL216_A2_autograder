BranchPredictor: BranchPredictor.cpp BranchPredictor.hpp
	$(CXX) $(CFLAGS) BranchPredictor.cpp -o BranchPredictor

clean:
	rm -f BranchPredictor