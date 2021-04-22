#include <arpa/inet.h>
#include <errno.h>
#include <netdb.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

#define SERVERPORT "4950"  // the port users will be connecting to

#define MAXDATASIZE 128

const char *network_ips[] = {"10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4"};

#define HOST_NUM 4

/* print message for error signals */
void error_print(char *ptr) {
  perror(ptr);
  exit(EXIT_FAILURE);
}
/* quit program on signal */
void quit_tranmission(int sig) {
  printf("recv a quit signal = %d\n", sig);
  exit(EXIT_SUCCESS);
}

// get sockaddr, IPv4 or IPv6:
void *get_in_addr(struct sockaddr *sa) {
  if (sa->sa_family == AF_INET) {
    return &(((struct sockaddr_in *)sa)->sin_addr);
  }

  return &(((struct sockaddr_in6 *)sa)->sin6_addr);
}

int main(int argc, char *argv[]) {
  struct addrinfo hints;

  int listenfd;
  int rv;
  int numbytes;
  int host_idx;
  int talkfd[HOST_NUM];
  int self;

  if (argc != 2) {
    fprintf(stderr, "usage: %s <your declared host number> \n", argv[0]);
    exit(1);
  }

  sscanf(argv[1], "%d", &self);

  pid_t pid;
  pid = fork();
  if (pid == -1) {
    error_print((char *)"fork");
  }

  if (pid == 0) {  // listener
    struct addrinfo *servinfo, *p;
    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_INET;  // set to AF_INET to use IPv4
    hints.ai_socktype = SOCK_DGRAM;
    hints.ai_flags = AI_PASSIVE;  // use my IP
    if ((rv = getaddrinfo(NULL, SERVERPORT, &hints, &servinfo)) != 0) {
      fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
      return 1;
    }

    // loop through all the results and make a socket
    for (p = servinfo; p != NULL; p = p->ai_next) {
      if ((listenfd = socket(p->ai_family, p->ai_socktype, p->ai_protocol)) ==
          -1) {
        perror("listener: socket");
        continue;
      }

      if (bind(listenfd, p->ai_addr, p->ai_addrlen) == -1) {
        close(listenfd);
        perror("listener: bind");
        continue;
      }

      break;
    }

    if (p == NULL) {
      fprintf(stderr, "listener: failed to create socket\n");
      return 2;
    }

    freeaddrinfo(servinfo);
    struct sockaddr_storage their_addr;
    char buf[MAXDATASIZE];
    socklen_t addr_len;
    char s[INET6_ADDRSTRLEN];
    while (1) {
      addr_len = sizeof their_addr;
      if ((numbytes = recvfrom(listenfd, buf, MAXDATASIZE - 1, 0,
                               (struct sockaddr *)&their_addr, &addr_len)) ==
          -1) {
        error_print((char *)"recvfrom");
      } else if (numbytes == 0) {
        printf("server is close!\n");
        break;
      }
      if (strcmp(inet_ntop(their_addr.ss_family,
                           get_in_addr((struct sockaddr *)&their_addr), s,
                           sizeof s),
                 network_ips[self]) != 0) {
        buf[numbytes] = '\0';
        printf(
            "%s : %s",
            inet_ntop(their_addr.ss_family,
                      get_in_addr((struct sockaddr *)&their_addr), s, sizeof s),
            buf);
      }
      bzero(buf, strlen(buf));
    }
    close(listenfd); /* before ending, close the socket file descriptor */
    kill(getppid(), SIGUSR1); /* should signal the father process to exit */
    exit(EXIT_SUCCESS);       /* should notify father process exit success */
  } else {                    // talker
    signal(SIGUSR1, quit_tranmission); /* deal with transmission corruption */
    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_INET;  // set to AF_INET to use IPv4
    hints.ai_socktype = SOCK_DGRAM;

    pid_t ppid;

    struct addrinfo *servinfo[HOST_NUM], *p[HOST_NUM];

    for (host_idx = 0; host_idx < HOST_NUM; ++host_idx) {
      if ((rv = getaddrinfo(network_ips[host_idx], SERVERPORT, &hints,
                            &(servinfo[host_idx]))) != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
        return 1;
      }

      // loop through all the results and make a socket
      for (p[host_idx] = servinfo[host_idx]; p[host_idx] != NULL;
           p[host_idx] = p[host_idx]->ai_next) {
        if ((talkfd[host_idx] =
                 socket(p[host_idx]->ai_family, p[host_idx]->ai_socktype,
                        p[host_idx]->ai_protocol)) == -1) {
          perror("talker: socket");
          continue;
        }

        break;
      }

      if (p[host_idx] == NULL) {
        fprintf(stderr, "talker: failed to create socket\n");
        return 2;
      }
    }

    char send_buf[MAXDATASIZE] = {0};

    while (fgets(send_buf, sizeof(send_buf), stdin) != NULL)
    /* if the stdin is not closed */
    {
      for (int i = 0; i < HOST_NUM; ++i) {
        if ((numbytes = sendto(talkfd[i], send_buf, strlen(send_buf), 0,
                               (p[i])->ai_addr, (p[i])->ai_addrlen)) == -1) {
          error_print((char *)"sendto");
        }
      }
      bzero(send_buf, strlen(send_buf));
    }
    for (int i = 0; i < HOST_NUM; ++i) {
      freeaddrinfo(servinfo[i]);
      close(talkfd[i]); /* end of program, close socket file descriptor */
    }
  }

  return 0;
}