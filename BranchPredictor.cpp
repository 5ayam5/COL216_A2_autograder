#include "BranchPredictor.hpp"
#include <iostream>
#include <fstream>

struct SaturatingGold : public BranchPredictor {
    std::vector<std::bitset<2>> table;
    SaturatingGold(int value) : table(1 << 14, value) {}

    bool predict(uint32_t pc) {
        return table[pc & 0x3fff].to_ulong() >= 2;
    }

    void update(uint32_t pc, bool taken) {
        uint8_t value = table[pc & 0x3fff].to_ulong();
        if (taken)
            value = std::min(value + 1, 3);
        else
            value = std::max(value - 1, 0);
        
        table[pc & 0x3fff] = value;
    }
};

struct BHRGold : public BranchPredictor {
    std::vector<std::bitset<2>> bhrTable;
    std::bitset<2> bhr;
    BHRGold(int value) : bhrTable(1 << 2, value), bhr(value) {}

    bool predict(uint32_t pc) {
        return bhrTable[bhr.to_ulong()].to_ulong() >= 2;
    }

    void update(uint32_t pc, bool taken) {
        uint8_t value = bhrTable[bhr.to_ulong()].to_ulong();
        if (taken)
            value = std::min(value + 1, 3);
        else
            value = std::max(value - 1, 0);
        
        bhrTable[bhr.to_ulong()] = value;
        bhr = (bhr << 1) | std::bitset<2>(taken);
    }
};

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

void check(BranchPredictor *gold, BranchPredictor *student, std::vector<std::pair<uint32_t, bool>> trace, std::ofstream& outputFile) {
    int correct = 0;
    for (auto& pair : trace) {
        bool goldPredict = gold->predict(pair.first);
        bool studentPredict = student->predict(pair.first);
        if (goldPredict == studentPredict)
            correct++;
        gold->update(pair.first, pair.second);
        student->update(pair.first, pair.second);
    }
    outputFile << (correct == trace.size()) << ',';
}

int main(int argc, char** argv) {
    if (argc != 4) {
        std::cout << "Usage: ./BranchPredictor <student id> <trace file> <output file>" << std::endl;
        return 0;
    }

    std::string studentId(argv[1]);

    std::ifstream traceFile(argv[2]);
    std::vector<std::pair<uint32_t, bool>> trace = readTrace(traceFile);

    std::ofstream outputFile(argv[3], std::ios::app);

    outputFile << studentId << ',';
    for (uint8_t value = 0; value < 4; value++)
        check(new SaturatingGold(value), new SaturatingBranchPredictor(value), trace, outputFile);
    for (uint8_t value = 0; value < 4; value++)
        check(new BHRGold(value), new BHRBranchPredictor(value), trace, outputFile);

    for (uint8_t value = 0; value < 4; value++) {
        SaturatingBHRBranchPredictor student(value, 1 << 14);
        int correct = 0;
        for (auto &pair : trace) {
        correct += student.predict(pair.first) == pair.second;
        student.update(pair.first, pair.second);
        }
        outputFile << correct << ",\n"[value == 3];
    }
}
