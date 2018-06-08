#include <stdio.h>
int main()
{
   int f1=0, f2=1, fib_ser, cnt=2, lmt;

   printf("Please enter the limit of the Fibonacci series :");
   scanf("%d",&lmt);


   while (cnt < lmt)
   {
      fib_ser=f1+f2;
      cnt++;
      printf("%d\n",fib_ser);
      f1=f2;
      f2=fib_ser;
   }
   return 0;
}
