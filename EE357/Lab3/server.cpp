/*
** selectserver.c -- a cheezy multiperson chat server
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>

#define PORT "9034" // port we're listening on
#define MAX_FD_NUM 64


// get sockaddr, IPv4 or IPv6:
void *get_in_addr(struct sockaddr *sa)
{
    if (sa->sa_family == AF_INET)
    {
        return &(((struct sockaddr_in *)sa)->sin_addr);
    }

    return &(((struct sockaddr_in6 *)sa)->sin6_addr);
}


int main(void)
{
    fd_set master;   // master file descriptor list
    fd_set read_fds; // temp file descriptor list for select()
    int fdmax;       // maximum file descriptor number

    int listener;                       // listening socket descriptor
    int newfd;                          // newly accept()ed socket descriptor
    struct sockaddr_storage remoteaddr; // client address
    socklen_t addrlen;

    char id_msg[INET6_ADDRSTRLEN+256+5]; // temp buffer for packing messages for send()
    char* remoteIPs[MAX_FD_NUM]; // remoteIPs

    char buf[256]; // buffer for client data
    int nbytes;

    char remoteIP[INET6_ADDRSTRLEN];

    int yes = 1; // for setsockopt() SO_REUSEADDR, below
    int i, j, rv;

    struct addrinfo hints, *ai, *p;

    FD_ZERO(&master); // clear the master and temp sets
    FD_ZERO(&read_fds);

    // get us a socket and bind it
    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = AI_PASSIVE;
    if ((rv = getaddrinfo(NULL, PORT, &hints, &ai)) != 0)
    {
        fprintf(stderr, "selectserver: %s\n", gai_strerror(rv));
        exit(1);
    }

    for (p = ai; p != NULL; p = p->ai_next)
    {
        listener = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
        if (listener < 0)
        {
            continue;
        }

        // lose the pesky "address already in use" error message
        setsockopt(listener, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(int));

        if (bind(listener, p->ai_addr, p->ai_addrlen) < 0)
        {
            close(listener);
            continue;
        }


        // /* print setup info */
        // fprintf(stdout, "socket setup done, on port %d\n", ((struct sockaddr_in*) p->ai_addr)->sin_port);
        // struct in_addr p_addr = ((struct sockaddr_in*) p->ai_addr)->sin_addr;
        // char ip_str[INET_ADDRSTRLEN];
        // fprintf(stdout, "socket setup done, on address %s\n", inet_ntop(AF_INET, &(p_addr), ip_str, INET_ADDRSTRLEN));
        break;
    }


    // if we got here, it means we didn't get bound
    if (p == NULL)
    {
        fprintf(stderr, "selectserver: failed to bind\n");
        exit(2);
    }

    freeaddrinfo(ai); // all done with this

    // listen
    if (listen(listener, 10) == -1)
    {
        perror("listen");
        exit(3);
    }

    // add the listener to the master set
    FD_SET(listener, &master);

    // keep track of the biggest file descriptor
    fdmax = listener; // so far, it's this one

    // main loop
    for (;;)
    {
        read_fds = master; // copy it
        if (select(fdmax + 1, &read_fds, NULL, NULL, NULL) == -1)
        {
            perror("select");
            exit(4);
        }

        // run through the existing connections looking for data to read
        for (i = 0; i <= fdmax; i++)
        {
            if (FD_ISSET(i, &read_fds))
            { // we got one!!
                if (i == listener)
                {
                    // handle new connections
                    addrlen = sizeof remoteaddr;
                    newfd = accept(listener,
                                   (struct sockaddr *)&remoteaddr,
                                   &addrlen);
                    inet_ntop(remoteaddr.ss_family,
                                get_in_addr((struct sockaddr *)&remoteaddr),
                                remoteIP, INET6_ADDRSTRLEN);
                    remoteIPs[newfd] = (char*) malloc((strlen(remoteIP)+1)*sizeof(char));
                    strcpy(remoteIPs[newfd], remoteIP);
                    // remoteIPs[newfd][strlen(remoteIP)] = '\0';

                    if (newfd == -1)
                    {
                        perror("accept");
                    }
                    else
                    {
                        FD_SET(newfd, &master); // add to master set
                        if (newfd > fdmax)
                        { // keep track of the max
                            fdmax = newfd;
                        }
                        printf("selectserver: new connection from %s on "
                               "socket %d\n", remoteIP, newfd);
                        // we should notify other users
                        for (j = 0; j <= fdmax; j++)
                        {
                            // send to everyone!
                            if (FD_ISSET(j, &master))
                            {
                                // except the listener and ourselves
                                if (j != listener && j != i)
                                {
                                    memset(id_msg, 0, sizeof id_msg); 
                                    strcat(id_msg, "INFO: ");
                                    strcat(id_msg, inet_ntop(remoteaddr.ss_family,
                                                    get_in_addr((struct sockaddr *)&remoteaddr),
                                                    remoteIP, INET6_ADDRSTRLEN));
                                    strcat(id_msg," has logged into of the room\n");
                                    if (send(j, id_msg, strlen(id_msg) , 0) == -1)
                                    {
                                        perror("send");
                                    }
                                }
                            }
                        }
                    }
                }
                else
                {
                    // handle data from a client
                    if ((nbytes = recv(i, buf, sizeof buf, 0)) <= 0)
                    {
                        // got error or connection closed by client
                        if (nbytes == 0)
                        {
                            // connection closed
                            printf("selectserver: socket %d hung up\n", i);
                            // we should notify other users
                            for (j = 0; j <= fdmax; j++)
                            {
                                // send to everyone!
                                if (FD_ISSET(j, &master))
                                {
                                    // except the listener and ourselves
                                    if (j != listener && j != i)
                                    {
                                        memset(id_msg, 0, sizeof id_msg); 
                                        strcat(id_msg, "INFO: ");
                                        strcat(id_msg, inet_ntop(remoteaddr.ss_family,
                                                        get_in_addr((struct sockaddr *)&remoteaddr),
                                                        remoteIP, INET6_ADDRSTRLEN));
                                        strcat(id_msg," left the room\n");
                                        if (send(j, id_msg, strlen(id_msg) , 0) == -1)
                                        {
                                            perror("send");
                                        }
                                    }
                                }
                            }
                        }
                        else
                        {
                            perror("recv");
                        }
                        close(i);           // bye!
                        FD_CLR(i, &master); // remove from master set
                        free(remoteIPs[i]);
                    }
                    else
                    {
                        // we got some data from a client
                        for (j = 0; j <= fdmax; j++)
                        {
                            // send to everyone!
                            if (FD_ISSET(j, &master))
                            {
                                // except the listener and ourselves
                                if (j != listener && j != i)
                                {
                                    memset(id_msg, 0, sizeof id_msg); 
                                    strcat(id_msg, remoteIPs[i]);
                                    strcat(id_msg,": ");
                                    strncat(id_msg,buf,strlen(buf));
                                    if (send(j, id_msg, strlen(id_msg) , 0) == -1)
                                    {
                                        perror("send");
                                    }
                                }
                            }
                        }
                        memset(buf, 0, sizeof buf);  /* IMPORTANT! */
                    }
                } // END handle data from client
            }     // END got new incoming connection
        }         // END looping through file descriptors
    }             // END for(;;)--and you thought it would never end!

    return 0;
}