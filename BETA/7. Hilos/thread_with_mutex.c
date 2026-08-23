#include <stdio.h>
#include <inttypes.h>
#include <stdlib.h>

#include <pthread.h>

uint32_t* A  = NULL;
uint32_t* B  = NULL;
uint32_t* C  = NULL;

uint32_t  N  = 0;

pthread_mutex_t mutex = {};

typedef struct
{
  uint32_t i;
} thread_data;

void* dot_product(void* arguments)
{
  uint32_t   i = ((thread_data*)arguments)->i;
  uint32_t   j = 0;
  uint32_t sum = 0;

  for(j = 0; j < N; j++)
  {
    sum += A[i/N*N + j]*B[j*N + i%N];
  }

  pthread_mutex_lock(&mutex);
  C[i] = sum;
  printf("C[%d] = %d\n", i, C[i]);
  pthread_mutex_unlock(&mutex);

  return NULL;
}

int main(int argc, char* argv[])
{
  pthread_t*   threads     = NULL;
  thread_data* parameters  = NULL;
  
  int32_t      ret = 0;
  uint32_t     i   = 0;

  if (argc < 2)
  {
    printf("ERROR: Incorrect number of arguments!\n");
    return -1;
  }
  else
  {
    N = atoi(argv[1]);
  }

  A           = (uint32_t*)malloc(N*N*sizeof(uint32_t));
  B           = (uint32_t*)malloc(N*N*sizeof(uint32_t));
  C           = (uint32_t*)calloc(N*N, sizeof(uint32_t));
  threads     = (pthread_t*)malloc(N*N*sizeof(pthread_t));
  parameters  = (thread_data*)malloc(N*N*sizeof(thread_data));

  pthread_mutex_init(&mutex, NULL);

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
    parameters[i].i = i;
    
    ret = pthread_create(&threads[i], NULL, dot_product, (void*)&parameters[i]);
    if (ret != 0)
    {
      printf("ERROR: Thread not created!\n");
      return -1;
    }
  }

  for(i = 0; i < N*N; i++)
  {
    pthread_join(threads[i], NULL);
    printf("C[%d] = %d\n", i, C[i]);
  }

  pthread_mutex_destroy(&mutex);

  free(A);           A          = NULL;
  free(B);           B          = NULL;
  free(C);           C          = NULL;
  free(threads);     threads    = NULL;
  free(parameters);  parameters = NULL;

  return 0;
}
