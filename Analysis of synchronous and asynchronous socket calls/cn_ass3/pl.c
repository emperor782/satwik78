#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <poll.h>

#define PORT 4444

int main() {
    int sockfd, newSocket;
    struct sockaddr_in serverAddr;
    struct pollfd *fds = NULL;
    socklen_t addr_size;
    char buffer[1024];
    int nfds = 1; // Initialize nfds to 1 for the server socket

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
    if (bind(sockfd, (struct sockaddr *)&serverAddr, sizeof(serverAddr)) < 0) {
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

    addr_size = sizeof(struct sockaddr_in);
    fds = (struct pollfd *)malloc(sizeof(struct pollfd));
    fds[0].fd = sockfd;
    fds[0].events = POLLIN;

    while (1) {
        int pollStatus = poll(fds, nfds, -1); // Wait indefinitely

        if (pollStatus < 0) {
            perror("Error in poll");
            exit(1);
        }

        if (fds[0].revents & POLLIN) {
            newSocket = accept(sockfd, (struct sockaddr *)&serverAddr, &addr_size);
            if (newSocket < 0) {
                perror("Error in accepting");
            } else {
                printf("Connection accepted from %s:%d\n", inet_ntoa(serverAddr.sin_addr), ntohs(serverAddr.sin_port));
                nfds++;
                fds = (struct pollfd *)realloc(fds, nfds * sizeof(struct pollfd));
                fds[nfds - 1].fd = newSocket;
                fds[nfds - 1].events = POLLIN;
            }
        }

        for (int i = 1; i < nfds; i++) {
            if (fds[i].revents & (POLLERR | POLLHUP)) {
                // Error or client closed the connection
                close(fds[i].fd);
                nfds--;
                for (int j = i; j < nfds; j++) {
                    fds[j] = fds[j + 1];
                }
            }

            if (fds[i].revents & POLLIN) {
                bzero(buffer, sizeof(buffer));
                int bytesRead = recv(fds[i].fd, buffer, sizeof(buffer), 0);
                if (bytesRead <= 0) {
                    printf("Disconnected from %s:%d\n", inet_ntoa(serverAddr.sin_addr), ntohs(serverAddr.sin_port));
                    close(fds[i].fd);
                    nfds--;
                    for (int j = i; j < nfds; j++) {
                        fds[j] = fds[j + 1];
                    }
                } else {
                    printf("Client (%s:%d): %s\n", inet_ntoa(serverAddr.sin_addr), ntohs(serverAddr.sin_port), buffer);
                    send(fds[i].fd, buffer, strlen(buffer), 0);
                }
            }
        }
    }

    free(fds);
    return 0;
}
