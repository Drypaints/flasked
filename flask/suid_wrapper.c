// gcc -o suid_wrapper suid_wrapper.c
#include <stdlib.h>
#include <unistd.h>

int main() {
    setuid(0);
    setgid(0);
    execl("/bin/bash", "bash", "/home/flask-app/backup.sh", NULL);
    return 0;
}
