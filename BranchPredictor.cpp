#include "BranchPredictor.hpp"
#include <iostream>
#include <fstream>
#include <boost/filesystem.hpp>

std::vector<std::pair<uint32_t, bool>> readTrace(std::ifstream& traceFile) {
    std::vector<std::pair<uint32_t, bool>> trace;
    std::string line;
    while (std::getline(traceFile, line)) {
        uint32_t pc;
        int taken;
        sscanf(line.c_str(), "%d %d", &pc, &taken);
        trace.push_back(std::make_pair(pc, taken));
    }
    return trace;
}

int main(int argc, char** argv) {
    if (argc != 4) {
        std::cerr << "Usage: ./BranchPredictor <trace file> <case> <value>" << std::endl;
        return 0;
    }

    std::ifstream traceFile(argv[1]);
    int caseNum = std::stoi(argv[2]);
    int value = std::stoi(argv[3]);

    std::vector<std::pair<uint32_t, bool>> trace = readTrace(traceFile);


    BranchPredictor* predictor;
    switch (caseNum) {
        case 1:
            predictor = new SaturatingBranchPredictor(value);
            break;
        case 2:
            predictor = new BHRBranchPredictor(value);
            break;
        case 3:
            predictor = new SaturatingBHRBranchPredictor(value, 1 << 16);
            break;
        default:
            std::cerr << "Invalid case number" << std::endl;
            return 0;
    }

    for (auto& pair : trace) {
        bool prediction = predictor->predict(pair.first);
        predictor->update(pair.first, pair.second);
        std::cout << prediction << '\n';
    }

    delete predictor;
    return 0;
}
