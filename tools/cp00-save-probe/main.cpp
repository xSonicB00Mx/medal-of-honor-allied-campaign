// Diagnostic reader for freshly generated CP0 test saves only.
// Uses the engine's existing decoder; never modifies a save or game state.
#include "../../code/corepp/lz77.h"
#include <algorithm>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <iterator>
#include <vector>

int main(int argc, char **argv)
{
    if (argc != 2) return 2;
    std::ifstream file(argv[1], std::ios::binary);
    std::vector<unsigned char> input((std::istreambuf_iterator<char>(file)), {});
    if (input.size() < 12 || std::memcmp(input.data(), "CSVG", 4)) return 3;
    uint32_t expected;
    std::memcpy(&expected, input.data() + 4, 4);
    if (!expected || expected > 64 * 1024 * 1024) return 4;
    std::vector<unsigned char> output(expected + 64);
    size_t actual = 0;
    if (g_lz77.Decompress(input.data() + 8, input.size() - 8, output.data(), &actual)
        || actual != expected) return 5;
    output.resize(actual);
    const float probes[2][3] = {{17.25f, 29.5f, 128.0f}, {-31.5f, 41.75f, 300.0f}};
    for (const auto &probe : probes) {
        const auto *bytes = reinterpret_cast<const unsigned char *>(probe);
        size_t count = 0;
        auto pos = output.begin();
        while ((pos = std::search(pos, output.end(), bytes, bytes + sizeof(probe))) != output.end()) {
            ++count;
            ++pos;
        }
        std::cout << count << '\n';
    }
}
