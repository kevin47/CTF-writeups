#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <sodium.h>
#include <errno.h>
#include <string.h>

int main(int argc, char *argv[]){
    DIR* dir;
    struct dirent *ent;
    struct stat states;
    char *child = NULL;
    char path[512] = {0};

    char *name = argv[1];
    dir = opendir(name);
    if (!dir) {
        printf("Can't opendir(%s)\n", name);
        return 1;
    }

    while ((ent = readdir(dir)) != NULL) {
        if (!strcmp(".", ent->d_name) || !strcmp("..", ent->d_name)) {
            continue;
        }
        else {
            printf("%s\n", ent->d_name);
        }
    }
    return 0;
}
