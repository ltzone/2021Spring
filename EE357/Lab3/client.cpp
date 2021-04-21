#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<unistd.h>
#include<sys/socket.h>
#include<arpa/inet.h>
#include<netinet/in.h>
#include<signal.h>
#include <arpa/inet.h>
#include <netdb.h>


# define MAXDATASIZE 128

/*处理系统调用中产生的错误*/
void error_print(char * ptr)
{
        perror(ptr);
        exit(EXIT_FAILURE);
}
/*处理通信结束时回调函数接收到的信号*/
void quit_tranmission(int sig)
{
    printf("recv a quit signal = %d\n",sig);
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
    if (argc != 3) {
        fprintf(stderr, "usage: %s <domain name>  <port name>\n", argv[0]);
        exit(0);
    }

    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    if ((rv = getaddrinfo(argv[1], argv[2], &hints, &servinfo)) != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
        return 1;
    }

    // loop through all the results and connect to the first we can
    for(p = servinfo; p != NULL; p = p->ai_next) {
        if ((sockfd = socket(p->ai_family, p->ai_socktype,
                p->ai_protocol)) == -1) {
            perror("client: socket");
            continue;
        }

        if (connect(sockfd, p->ai_addr, p->ai_addrlen) == -1) {
            close(sockfd);
            perror("client: connect");
            continue;
        }

        break;
    }

    if (p == NULL) {
        fprintf(stderr, "client: failed to connect\n");
        return 2;
    }

    inet_ntop(p->ai_family, get_in_addr((struct sockaddr *)p->ai_addr),
            s, sizeof s);
    printf("client: connecting to %s\n", s);

    freeaddrinfo(servinfo); // all done with this structure

    pid_t pid;
    pid = fork();
    if(pid == -1){
        error_print((char*) "fork");
    }

    if(pid == 0){
        char recv_buf[MAXDATASIZE] = {0};
        while(1){
            bzero(recv_buf,sizeof(recv_buf));
            int ret = read(sockfd, recv_buf, sizeof(recv_buf));
            if(ret == -1)
                error_print((char*) "read");
            else if(ret == 0){
                printf("server is close!\n");
                break;//子进程收到服务器端退出的信息（服务器Ctrl+C结束通信进程，read函数返回值为0，退出循环）
            }
            fputs(recv_buf,stdout);/*将收到的信息输出到标准输出stdout上*/
        }
        close(sockfd);/*子进程退出，通信结束关闭套接字*/
        kill(getppid(),SIGUSR1);/*子进程结束，也要向父进程发出一个信号告诉父进程终止接收，否则父进程一直会等待输入*/
        exit(EXIT_SUCCESS);/*子进程正常退出结束，向父进程返回EXIT_SUCCESS*/
    }
    else{
        signal(SIGUSR1,quit_tranmission);/*回调函数处理通信中断*/
        char send_buf[MAXDATASIZE] = {0};
        /*如果服务器Ctrl+C结束通信进程，fgets获取的就是NULL，否则就进入循环正常发送数据*/
        while(fgets(send_buf,sizeof(send_buf), stdin) != NULL){
            int set = write(sockfd, send_buf, strlen(send_buf));/*将send_buf缓冲区的数据发送给对端服务器*/
            if(set < 0)
                error_print((char*) "write");
            bzero(send_buf,strlen(send_buf));
        }
        close(sockfd);/*通信结束，关闭套接字*/
    }
    return 0;
}