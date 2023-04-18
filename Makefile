CFLAGS += -lboost_filesystem -lboost_system

BranchPredictor: BranchPredictor.cpp BranchPredictor.hpp
	$(CXX) -o BranchPredictor BranchPredictor.cpp $(CFLAGS)

BranchPredictorChecker: BranchPredictorChecker.cpp BranchPredictor.hpp BranchPredictorGold.hpp
	$(CXX) -o BranchPredictorChecker BranchPredictorChecker.cpp $(CFLAGS)

clean:
	rm -f BranchPredictor BranchPredictorChecker