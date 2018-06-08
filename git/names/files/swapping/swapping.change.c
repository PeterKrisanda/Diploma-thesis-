#include <stdio.h>
int main()
{
   int A, B, temp;

   printf("Please enter the 1st number : ");
   scanf("%d",&A);
   printf("\nPlease enter the 2nd number : ");
   scanf("%d",&B);

   printf("\nBefore:");
   printf("A - %d \nB - %d", A, B);

   temp = A;
   A = B;
   B = temp;

   printf("\nAfter swapping:\n");
   printf("A - %d \nB - %d", A, B);

   return 0;
}
