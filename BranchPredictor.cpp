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
        sscanf(line.c_str(), "%x %d", &pc, &taken);
        trace.push_back(std::make_pair(pc, taken));
    }
    return trace;
}

int main(int argc, char** argv) {
    if (argc != 5) {
        std::cerr << "Usage: ./BranchPredictor <student id> <trace file> <output directory> <num>" << std::endl;
        return 0;
    }

    boost::filesystem::path studentId(argv[1]);

    std::ifstream traceFile(argv[2]);
    std::vector<std::pair<uint32_t, bool>> trace = readTrace(traceFile);

    boost::filesystem::path outputDirectory = boost::filesystem::path(argv[3]) / boost::filesystem::path(argv[4]);
    if (!boost::filesystem::exists(outputDirectory))
        boost::filesystem::create_directories(outputDirectory);

    for (int caseNum = 1; caseNum <= 3; caseNum++) {
        for (int value = 0; value <= 3; value++) {

            if (!boost::filesystem::exists(outputDirectory / studentId))
                boost::filesystem::create_directory(outputDirectory / studentId);
            std::ofstream outputFile((outputDirectory / studentId / (std::to_string(caseNum) + "_" + std::to_string(value) + ".txt")).string());

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
                outputFile << prediction << '\n';
            }

            delete predictor;
        }
    }
    return 0;
}
