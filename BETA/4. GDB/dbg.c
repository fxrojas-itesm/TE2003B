#include <stdio.h>
#include <inttypes.h>

void add_one(uint32_t* array, uint32_t length)
{
  uint32_t i = 0;

  for (i=0; i <= length; i++)
  {
    array[i] += 1;
  }
}

void print(uint32_t* array, uint32_t length)
{
  uint32_t i = 0;

  for (i=0; i < length; i++)
  {
    printf("%d ", array[i]);
  }
  printf("\n");
}

int main()
{
  uint32_t array1[] = {0, 1, 2, 3, 4};
  uint32_t array2[] = {5, 6, 7, 8};
  uint32_t N1 = (uint32_t)(sizeof(array1)/sizeof(array1[0]));
  uint32_t N2 = (uint32_t)(sizeof(array2)/sizeof(array2[0]));

  add_one(array1, N1);
  add_one(array2, N2);

  print(array1, N1);
  print(array2, N2);

  return 0;
}
