#include <stdio.h>

int main()
{
     int num, sum = 0, count, i;

     printf("Please enter how many numbers you want to add\n");
     scanf("%d", &num);

     printf("Please enter %d numbers one by one\n",num);

     for (count = 1; count <= num; count++){

         scanf("%d",&i);
         sum = sum + i;

     }

     printf("Sum of entered numbers = %d\n",sum);
     return 0;
}
