#ifndef __BRANCH_PREDICTOR_GOLD_HPP__
#define __BRANCH_PREDICTOR_GOLD_HPP__

#include "BranchPredictor.hpp"

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


#endif