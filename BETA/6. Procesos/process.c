#include <stdio.h>
#include <inttypes.h>
#include <stdlib.h>

#include <unistd.h>
#include <sys/mman.h>
#include <sys/wait.h>

#define NO_FD     -1
#define FD_OFFSET  0

int main(int argc, char* argv[])
{
  uint32_t* A   = NULL;
  uint32_t* B   = NULL;
  uint32_t* C   = NULL;

  uint32_t  N   = 0;
  uint32_t  i   = 0;
  uint32_t  j   = 0;
  pid_t     pid = 0; 

  if (argc < 2)
  {
    printf("ERROR: Incorrect number of arguments!\n");
    return -1;
  }
  else
  {
    N = atoi(argv[1]);
  }

  A = mmap(NULL, N*N*sizeof(uint32_t), PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, NO_FD, FD_OFFSET);
  B = mmap(NULL, N*N*sizeof(uint32_t), PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, NO_FD, FD_OFFSET);
  C = mmap(NULL, N*N*sizeof(uint32_t), PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, NO_FD, FD_OFFSET);

  for (i = 0; i < N*N; i++)
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

  for(i = 0; i < N*N; i++)
  {
    pid = fork();
    if (pid < 0)
    {
      printf("ERROR: Process not created!\n");
      return -1;
    }
    else if (pid == 0)
    {
      for(j = 0; j < N; j++)
      {
        C[i] += A[i/N*N + j]*B[j*N + i%N];
      }
      printf("C[%d] = %d\n", i, C[i]);
      return 0;
    }
  }

  while(wait(NULL) != -1);

  munmap(A, N*N*sizeof(uint32_t)); A = NULL;
  munmap(B, N*N*sizeof(uint32_t)); B = NULL;
  munmap(C, N*N*sizeof(uint32_t)); C = NULL;

  return 0;
}
