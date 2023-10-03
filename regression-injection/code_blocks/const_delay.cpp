#include <thread>
#include <chrono>

// For deepsjeng=3 to 5, for parsec_freqmine=100
const auto start_time = std::chrono::high_resolution_clock::now();
const auto duration_time = std::chrono::microseconds(1);

do {
    std::this_thread::yield();
} while (std::chrono::high_resolution_clock::now() - start_time < duration_time);
