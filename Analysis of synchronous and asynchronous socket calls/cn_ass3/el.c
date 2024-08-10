#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/epoll.h>

#define PORT 4444

int main() {
    int sockfd;
    struct sockaddr_in serverAddr;
    int epoll_fd;
    struct epoll_event event, *events;
    char buffer[1024];

    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("Error in socket");
        exit(1);
    }
    printf("[+]Server Socket is created.\n");

    memset(&serverAddr, 0, sizeof(serverAddr));
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(PORT);
    serverAddr.sin_addr.s_addr = inet_addr("10.0.2.15"); // Set the server's IP address

    if (bind(sockfd, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) < 0) {
        perror("Error in binding");
        exit(1);
    }
    printf("[+]Bind to port %d\n", PORT);

    if (listen(sockfd, 10) == 0) {
        printf("[+]Listening....\n");
    } else {
        perror("Error in listening");
        exit(1);
    }

    epoll_fd = epoll_create1(0);
    if (epoll_fd == -1) {
        perror("Error in epoll_create");
        exit(1);
    }

    event.events = EPOLLIN;
    event.data.fd = sockfd;

    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, sockfd, &event) == -1) {
        perror("Error in epoll_ctl");
        exit(1);
    }

    events = (struct epoll_event*)malloc(sizeof(struct epoll_event));

    while (1) {
        int nfds = epoll_wait(epoll_fd, events, 1, -1);
        if (nfds == -1) {
            perror("Error in epoll_wait");
            exit(1);
        }

        for (int i = 0; i < nfds; i++) {
            if (events[i].data.fd == sockfd) {
                int newSocket = accept(sockfd, NULL, NULL);
                if (newSocket < 0) {
                    perror("Error in accepting");
                } else {
                    printf("Connection accepted from %s:%d\n", inet_ntoa(serverAddr.sin_addr), ntohs(serverAddr.sin_port));
                    event.events = EPOLLIN | EPOLLET;
                    event.data.fd = newSocket;
                    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, newSocket, &event) == -1) {
                        perror("Error in epoll_ctl for newSocket");
                        exit(1);
                    }
                }
            } else {
                int clientSocket = events[i].data.fd;
                bzero(buffer, sizeof(buffer));
                int bytesRead = recv(clientSocket, buffer, sizeof(buffer), 0);
                if (bytesRead <= 0) {
                    printf("Disconnected from client %d\n", clientSocket);
                    epoll_ctl(epoll_fd, EPOLL_CTL_DEL, clientSocket, NULL);
                    close(clientSocket);
                } else {
                    printf("Client (%s:%d): %s\n", inet_ntoa(serverAddr.sin_addr), ntohs(serverAddr.sin_port), buffer);
                    send(clientSocket, buffer, bytesRead, 0);
                }
            }
        }
    }

    free(events);
    return 0;
}
