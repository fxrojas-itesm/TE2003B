#include <stdio.h>
#include <inttypes.h>
#include <stdlib.h>

#include <unistd.h>
#include <sys/mman.h>
#include <sys/wait.h>
#include <pthread.h>

#define NO_FILE_DESCRIPTOR     -1
#define FILE_DESCRIPTOR_OFFSET  0

int main(int argc, char* argv[])
{
  uint32_t* A = NULL;
  uint32_t* B = NULL;
  uint32_t* C = NULL;

  uint32_t N   = 0;
  uint32_t i   = 0;
  uint32_t j   = 0;
  uint32_t sum = 0;

  pid_t pid  = 0;

  pthread_mutexattr_t mutexattr = {};
  pthread_mutex_t*    mutex     = NULL;

  if (argc < 2)
  {
    printf("ERROR: Incorrect number of arguments!\n");
    return -1;
  }
  else
  {
    N = atoi(argv[1]);
  }

  A     = mmap(NULL, N*N*sizeof(uint32_t), PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, NO_FILE_DESCRIPTOR, FILE_DESCRIPTOR_OFFSET);
  B     = mmap(NULL, N*N*sizeof(uint32_t), PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, NO_FILE_DESCRIPTOR, FILE_DESCRIPTOR_OFFSET);
  C     = mmap(NULL, N*N*sizeof(uint32_t), PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, NO_FILE_DESCRIPTOR, FILE_DESCRIPTOR_OFFSET);
  mutex = mmap(NULL, sizeof(pthread_mutex_t), PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, NO_FILE_DESCRIPTOR, FILE_DESCRIPTOR_OFFSET);
  
  pthread_mutexattr_init(&mutexattr);
  pthread_mutexattr_setpshared(&mutexattr, PTHREAD_PROCESS_SHARED);
  pthread_mutex_init(mutex, &mutexattr);
  pthread_mutexattr_destroy(&mutexattr);

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
        sum += A[i/N*N + j]*B[j*N + i%N];
      }

      pthread_mutex_lock(mutex);
      C[i] = sum;
      printf("C[%d] = %d\n", i, C[i]);
      pthread_mutex_unlock(mutex);

      return 0;
    }
  }

  while(wait(NULL) != -1);

  pthread_mutex_destroy(mutex);

  munmap(mutex, sizeof(pthread_mutex_t)); mutex = NULL;
  munmap(A, N*N*sizeof(uint32_t));            A = NULL;
  munmap(B, N*N*sizeof(uint32_t));            B = NULL;
  munmap(C, N*N*sizeof(uint32_t));            C = NULL;

  return 0;
}
