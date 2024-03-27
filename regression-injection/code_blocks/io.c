#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int should_write = rand() % 3;
if (should_write == 1) {
    FILE *fp;
    char there_was_error = 0;
    fp = fopen("random.txt", "w+");
    if (fp == NULL)
    {
        fp = fopen("random.txt", "w");
        if (fp == NULL)
            there_was_error = 1;
    }

    if (there_was_error == 0)
    {
        char *letters = "abcdefghijklmnopqrstuvwxyz";
        char c = letters[rand() % 26];
        fputc(c, fp);
        fclose(fp);
    }
}
