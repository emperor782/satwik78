#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/select.h>

#define PORT 4444
#define IP_ADDRESS "10.0.2.15"

struct Client {
    int socket;
    struct Client* next;
};

int main() {
    int sockfd, newSocket, activity;
    struct Client* clientList = NULL;
    struct sockaddr_in serverAddr;
    fd_set readfds;
    socklen_t addr_size;
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
    serverAddr.sin_addr.s_addr = inet_addr(IP_ADDRESS);

    if (bind(sockfd, (struct sockaddr *)&serverAddr, sizeof(serverAddr)) < 0) {
        perror("Error in binding");
        exit(1);
    }
    printf("[+]Bind to IP address %s, port %d\n", IP_ADDRESS, PORT);

    if (listen(sockfd, SOMAXCONN) == 0) {
        printf("[+]Listening....\n");
    } else {
        perror("Error in listening");
        exit(1);
    }

    addr_size = sizeof(struct sockaddr_in);

    while (1) {
        FD_ZERO(&readfds);
        FD_SET(sockfd, &readfds);

        int maxSocket = sockfd;
        struct Client* current = clientList;

        while (current != NULL) {
            if (current->socket > 0) {
                FD_SET(current->socket, &readfds);
                if (current->socket > maxSocket) {
                    maxSocket = current->socket;
                }
            }
            current = current->next;
        }

        activity = select(maxSocket + 1, &readfds, NULL, NULL, NULL);
        if (activity < 0) {
            perror("Error in select");
            exit(1);
        }

        if (FD_ISSET(sockfd, &readfds)) {
            newSocket = accept(sockfd, (struct sockaddr *)&serverAddr, &addr_size);
            if (newSocket < 0) {
                perror("Error in accepting");
            } else {
                printf("Connection accepted from %s:%d\n", inet_ntoa(serverAddr.sin_addr), ntohs(serverAddr.sin_port));
                struct Client* newClient = (struct Client*)malloc(sizeof(struct Client));
                newClient->socket = newSocket;
                newClient->next = clientList;
                clientList = newClient;
            }
        }

        current = clientList;
        while (current != NULL) {
            if (current->socket > 0 && FD_ISSET(current->socket, &readfds)) {
                bzero(buffer, sizeof(buffer));
                int bytesRead = recv(current->socket, buffer, sizeof(buffer), 0);
                if (bytesRead <= 0) {
                    if (current->socket > 0) {
                        getpeername(current->socket, (struct sockaddr *)&serverAddr, &addr_size);
                        printf("Disconnected from %s:%d\n", inet_ntoa(serverAddr.sin_addr), ntohs(serverAddr.sin_port));
                        close(current->socket);
                    }

                    // Remove the disconnected client from the linked list
                    if (current == clientList) {
                        clientList = current->next;
                        free(current);
                        current = clientList;
                    } else {
                        struct Client* prev = clientList;
                        while (prev->next != current) {
                            prev = prev->next;
                        }
                        prev->next = current->next;
                        free(current);
                        current = prev->next;
                    }
                } else {
                    if (current->socket > 0) {
                        getpeername(current->socket, (struct sockaddr *)&serverAddr, &addr_size);
                        printf("Client (%s:%d): %s\n", inet_ntoa(serverAddr.sin_addr), ntohs(serverAddr.sin_port), buffer);
                        send(current->socket, buffer, strlen(buffer), 0);
                    }
                }
            } else {
                current = current->next;
            }
        }
    }

    // Cleanup (this part will not be reached in practice)
    while (clientList != NULL) {
        struct Client* temp = clientList;
        clientList = clientList->next;
        if (temp->socket > 0) {
            close(temp->socket);
        }
        free(temp);
    }
    close(sockfd);

    return 0;
}
