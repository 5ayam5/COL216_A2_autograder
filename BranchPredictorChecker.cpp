#include "BranchPredictorGold.hpp"
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

std::vector<bool> get_predictions(BranchPredictor *predictor, std::vector<std::pair<uint32_t, bool>> trace) {
    std::vector<bool> predictions;
    for (auto& pair : trace) {
        bool prediction = predictor->predict(pair.first);
        predictions.push_back(prediction);
        predictor->update(pair.first, pair.second);
    }
    return predictions;
}

std::vector<bool> get_predictions(std::string fileName) {
    std::ifstream file(fileName);
    std::string line;
    std::vector<bool> predictions;
    while (std::getline(file, line)) {
        predictions.push_back(line == "1");
    }
    return predictions;
}

std::vector<std::vector<std::vector<bool>>> get_all_predictions(std::vector<std::pair<uint32_t, bool>> trace) {
    std::vector<std::vector<std::vector<bool>>> predictions(2, std::vector<std::vector<bool>>(4));
    BranchPredictor *predictor;
    for (int value = 0; value <= 3; value++) {
        predictor = new SaturatingGold(value);
        predictions[0][value] = get_predictions(predictor, trace);
        delete predictor;
        predictor = new BHRGold(value);
        predictions[1][value] = get_predictions(predictor, trace);
    }

    return predictions;
}

bool check(std::vector<bool> gold, std::string fileName) {
    std::ifstream file(fileName);
    std::string line;
    int i = 0;

    while (std::getline(file, line)) {
        if (i >= gold.size())
            return false;
        if (line != (gold[i] ? "1" : "0"))
            return false;
        i++;
    }
    return i == gold.size();
}

int main(int argc, char** argv) {
    if (argc != 4) {
        std::cerr << "Usage: ./BranchPredictorChecker <directory> <trace file> <output>" << std::endl;
        return 0;
    }

    boost::filesystem::path directory(argv[1]);
    std::ifstream traceFile(argv[2]);
    std::ofstream outputFile(argv[3]);

    auto trace = readTrace(traceFile);
    std::vector<std::vector<std::vector<bool>>> gold_predictions = get_all_predictions(trace);

    if (!boost::filesystem::exists(directory)) {
        std::cerr << "Directory does not exist" << std::endl;
        return 0;
    }

    for (auto it = boost::filesystem::directory_iterator(directory); it != boost::filesystem::directory_iterator(); it++) {
        auto student = it->path();
        outputFile << student.filename().string() << ',';
        for (int caseNum = 1; caseNum <= 2; caseNum++)
            for (int value = 0; value <= 3; value++)
                outputFile << check(gold_predictions[caseNum - 1][value], (student / (std::to_string(caseNum) + "_" + std::to_string(value) + ".txt")).string()) << ',';

        for (int value = 0; value <= 3; value++) {
            auto predictions = get_predictions((student / ("3_" + std::to_string(value) + ".txt")).string());
            int count = 0;
            if (predictions.size() == trace.size())
                for (int i = 0; i < predictions.size(); i++)
                    if (predictions[i] == trace[i].second)
                        count++;
            
            outputFile << count << ",\n"[value == 3];
        }
    }
}