cmake_minimum_required(VERSION 3.20)
project(cp00_save_probe LANGUAGES CXX)
add_executable(cp00_save_probe main.cpp ../../code/corepp/lz77.cpp)
target_compile_features(cp00_save_probe PRIVATE cxx_std_17)
