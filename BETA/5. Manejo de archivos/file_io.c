#include <stdio.h>
#include <inttypes.h>
#include <stdlib.h>

int main(int argc, char* argv[])
{
  uint32_t* A   = NULL;
  uint32_t* B   = NULL;
  uint32_t* C   = NULL;
  
  uint32_t  N   = 0;
  uint32_t  i   = 0;
  uint32_t  j   = 0;
  FILE*     fp  = NULL;

  if (argc < 2)
  {
    printf("ERROR: Please provide the input file name! (e.g. ./program input.txt)\n");
    return -1;
  }

  fp = fopen(argv[1], "r");
  if (fp == NULL)
  {
    printf("ERROR: Could not open file %s\n", argv[1]);
    return -1;
  }

  if (fscanf(fp, "%" SCNu32, &N) != 1)
  {
    printf("ERROR: Failed to read N from the file.\n");
    fclose(fp);
    return -1;
  }

  A = (uint32_t*)malloc(N*N*sizeof(uint32_t));
  B = (uint32_t*)malloc(N*N*sizeof(uint32_t));
  C = (uint32_t*)calloc(N*N, sizeof(uint32_t)); 

  for (i = 0; i < N * N; i++)
  {
    if (fscanf(fp, "%" SCNu32, &A[i]) != 1)
    {
      printf("ERROR: Failed to read element for Matrix A at index %u\n", i);
      free(A); free(B); free(C);
      fclose(fp);
      return -1;
    }
  }

  for (i = 0; i < N*N; i++)
  {
    if (fscanf(fp, "%" SCNu32, &B[i]) != 1)
    {
      printf("ERROR: Failed to read element for Matrix B at index %u\n", i);
      free(A); free(B); free(C);
      fclose(fp);
      return -1;
    }
  }

  fclose(fp); 

  for (i = 0; i < N*N; i++)
  {
    for (j = 0; j < N; j++)
    {
      C[i] += A[i/N*N + j] * B[j*N + i%N];
    }
    printf("C[%d] = %d\n", i, C[i]);
  }
  
  free(A);
  free(B);
  free(C);

  return 0;
}
