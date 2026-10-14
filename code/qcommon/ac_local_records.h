// Bounded same-process transport. Tokens preserve reliable-command ordering;
// reset/eviction can discard a cosmetic record, never alias it to another hit.
#pragma once
#include <cstdint>
#include <cstddef>
template<class T, std::size_t Capacity> class ACLocalRecords {
    struct Slot {std::uint64_t token=0;T value={};};
    Slot slots[Capacity];std::uint64_t serial=0;
public:
    std::uint64_t Store(const T& value) {
        if(++serial==0)++serial;
        auto& s=slots[serial%Capacity];s.value=value;s.token=serial;return serial;
    }
    bool Take(std::uint64_t token,T& value) {
        auto& s=slots[token%Capacity];if(!token || s.token!=token)return false;
        value=s.value;s.token=0;return true;
    }
    void Clear() {for(auto& s:slots)s.token=0;}
};
