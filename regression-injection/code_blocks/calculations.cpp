#include <cstdlib>
#include <vector>

// For deepsjeng=25, for parsec_freqmine=135
std::vector<std::vector<int> > matrix(25, std::vector<int>(25, 1));
for (int row = 0; row < matrix.size(); ++row) {
    for (int col = 0; col < matrix[0].size(); ++col) {
        matrix[row][col] += row * col;
    }
}
