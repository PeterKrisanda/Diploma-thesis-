#include <stdio.h>

int main(){

     int i, j, num, temp, arr[1500];

     printf("Enter number of elements\n");
     scanf("%d", &num);

     printf("Enter %d integers\n", num);

     for (i = 0; i < num; i++){
          scanf("%d", &arr[i]);
     }

     for (i = 1 ; i <= num - 1; i++){

           j = i;

           while ( j > 0 && arr[j] < arr[j-1]){
                  temp = arr[j];
                  arr[j] = arr[j-1];
                  arr[j-1] = temp;
                  j--;
           }
     }

     printf("Sorting:\n");

     for (i = 0; i <= num - 1; i++){
           printf("%d\n", arr[i]);
     }

     return 0;
}
