#include <stdio.h>

int arr[]= {};

int main()

{

  int length;

  length = sizeof(arr)/sizeof(int);

  printf("The length of Array is %d", length);

  return 0;

}
