#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <signal.h>
#include <arpa/inet.h>
#include <netdb.h>

#define MAXDATASIZE 128

/* print message for error signals */
void error_print(char *ptr)
{
    perror(ptr);
    exit(EXIT_FAILURE);
}
/* quit program on signal */
void quit_tranmission(int sig)
{
    printf("recv a quit signal = %d\n", sig);
    exit(EXIT_SUCCESS);
}

// get sockaddr, IPv4 or IPv6:
void *get_in_addr(struct sockaddr *sa)
{
    if (sa->sa_family == AF_INET)
    {
        return &(((struct sockaddr_in *)sa)->sin_addr);
    }

    return &(((struct sockaddr_in6 *)sa)->sin6_addr);
}

int main(int argc, char *argv[])
{
    int sockfd, numbytes;
    struct addrinfo hints, *servinfo, *p;
    int rv;

    char s[INET6_ADDRSTRLEN];
    if (argc != 3)
    {
        fprintf(stderr, "usage: %s <domain name>  <port name>\n", argv[0]);
        exit(0);
    }

    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    if ((rv = getaddrinfo(argv[1], argv[2], &hints, &servinfo)) != 0)
    {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
        return 1;
    }

    // loop through all the results and connect to the first we can
    for (p = servinfo; p != NULL; p = p->ai_next)
    {
        if ((sockfd = socket(p->ai_family, p->ai_socktype,
                             p->ai_protocol)) == -1)
        {
            perror("client: socket");
            continue;
        }

        if (connect(sockfd, p->ai_addr, p->ai_addrlen) == -1)
        {
            close(sockfd);
            perror("client: connect");
            continue;
        }

        break;
    }

    if (p == NULL)
    {
        fprintf(stderr, "client: failed to connect\n");
        return 2;
    }

    inet_ntop(p->ai_family, get_in_addr((struct sockaddr *)p->ai_addr),
              s, sizeof s);
    printf("client: connecting to %s\n", s);

    freeaddrinfo(servinfo); // all done with this structure

    pid_t pid;
    pid = fork();
    if (pid == -1)
    {
        error_print((char *)"fork");
    }

    if (pid == 0)
    { // child process
        char recv_buf[MAXDATASIZE] = {0};
        
        while (1)
        {
            bzero(recv_buf, sizeof(recv_buf));
            int ret = read(sockfd, recv_buf, sizeof(recv_buf));
            if (ret == -1)
                error_print((char *)"read");
            else if (ret == 0)
            { /* server is closed */
                printf("server is close!\n");
                break;
            }
            fputs(recv_buf, stdout); /* for received message, print into stdout */
        }

        close(sockfd);            /* before ending, close the socket file descriptor */
        kill(getppid(), SIGUSR1); /* should signal the father process to exit */
        exit(EXIT_SUCCESS);       /* should notify father process exit success */
    }
    else
    {
        signal(SIGUSR1, quit_tranmission); /* deal with transmission corruption */
        char send_buf[MAXDATASIZE] = {0};

        while (fgets(send_buf, sizeof(send_buf), stdin) != NULL) 
        /* if the stdin is not closed */
        {
            int set = write(sockfd, send_buf, strlen(send_buf)); 
            /* send data to the server */
            if (set < 0)
                error_print((char *)"write");
            bzero(send_buf, strlen(send_buf));
        }

        close(sockfd); /* end of program, close socket file descriptor */
    }
    return 0;
}