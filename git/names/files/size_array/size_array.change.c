#include <stdio.h>

int arr[8]= { 1, 2, 3, 4, 5, 6, 7, 8 };

int main()

{

  int length;

  length = sizeof(arr)/sizeof(int);

  printf("The length of Array is %d", length);

  return 0;

}
