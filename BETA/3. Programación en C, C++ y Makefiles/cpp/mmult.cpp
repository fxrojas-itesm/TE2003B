#include <iostream>
#include <vector>
#include <cstdint>
#include <cstdlib>

int main(int argc, char* argv[])
{
  if (argc < 2)
  {
    std::cout << "ERROR: Incorrect number of arguments!" << std::endl;
    return -1;
  }

  uint32_t N = std::atoi(argv[1]);

  std::vector<uint32_t> A(N*N, 0);
  std::vector<uint32_t> B(N*N, 0);
  std::vector<uint32_t> C(N*N, 0);

  // Initialize A as identity matrix, B with sequential values
  for (uint32_t i = 0; i < N*N; i++)
  {
    if (i/N == i%N)
    {
      A[i] = 1;
    }
    else
    {
      A[i] = 0;
    }

    B[i] = i;
  }

  // Matrix multiplication: C = A * B
  for (uint32_t i = 0; i < N*N; i++)
  {
    for (uint32_t j = 0; j < N; j++)
    {
      C[i] += A[i/N*N + j] * B[j*N + i%N];
    }
    std::cout << "C[" << i << "] = " << C[i] << std::endl;
  }

  return 0;
}
