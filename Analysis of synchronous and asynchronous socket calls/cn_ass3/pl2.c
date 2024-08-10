#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <poll.h>
#include <inttypes.h>

#define PORT 4444

uint64_t fact(int n) {
    if (n <= 1) return 1;
    if (n > 20) n = 20;  // Limit the input to 20 for efficiency
    uint64_t output = 1;
    for (int i = 1; i <= n; i++) {
        output *= i;
    }
    return output;
}

int main() {
    int socketfd, nsocket;
    struct sockaddr_in serveraddress;
    struct pollfd *fds = NULL;
    socklen_t addr_size;
    char buffer[1024];
    int nfds = 1; // Initialize nfds to 1 for the server socket

    socketfd = socket(AF_INET, SOCK_STREAM, 0);
    if (socketfd < 0) {
        perror("Error in socket");
        exit(1);
    }
    printf("[+]Server Socket is created.\n");

    memset(&serveraddress, 0, sizeof(serveraddress));
    serveraddress.sin_family = AF_INET;
    serveraddress.sin_port = htons(PORT);
    serveraddress.sin_addr.s_addr = inet_addr("10.0.2.15"); // Set the server's IP address

    if (bind(socketfd, (struct sockaddr *)&serveraddress, sizeof(serveraddress)) < 0) {
        perror("Error in binding");
        exit(1);
    }
    printf("[+]Bind to port %d\n", PORT);

    if (listen(socketfd, 10) == 0) {
        printf("[+]Listening....\n");
    } else {
        perror("Error in listening");
        exit(1);
    }

    addr_size = sizeof(struct sockaddr_in);
    fds = (struct pollfd *)malloc(sizeof(struct pollfd));
    fds[0].fd = socketfd;
    fds[0].events = POLLIN;

    while (1) {
        int pollStatus = poll(fds, nfds, -1); // Wait indefinitely

        if (pollStatus < 0) {
            perror("Error in poll");
            exit(1);
        }

        if (fds[0].revents & POLLIN) {
            nsocket = accept(socketfd, (struct sockaddr *)&serveraddress, &addr_size);
            if (nsocket < 0) {
                perror("Error in accepting");
            } else {
                printf("Connection accepted from %s:%d\n", inet_ntoa(serveraddress.sin_addr), ntohs(serveraddress.sin_port));
                nfds++;
                fds = (struct pollfd *)realloc(fds, nfds * sizeof(struct pollfd));
                fds[nfds - 1].fd = nsocket;
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
                    printf("Disconnected from %s:%d\n", inet_ntoa(serveraddress.sin_addr), ntohs(serveraddress.sin_port));
                    close(fds[i].fd);
                    nfds--;
                    for (int j = i; j < nfds; j++) {
                        fds[j] = fds[j + 1];
                    }
                } else {
                    // Read the payload as a 64-bit unsigned integer
                    uint64_t input;
                    sscanf(buffer, "%" SCNu64, &input);
                    
                    // Compute the factorial
                    uint64_t output = fact(input);
                    snprintf(buffer, sizeof(buffer), "%" PRIu64, output);
                    
                    printf("Client (%s:%d): Factorial of %" PRIu64 " is %" PRIu64 "\n", inet_ntoa(serveraddress.sin_addr), ntohs(serveraddress.sin_port), input, output);
                    send(fds[i].fd, buffer, strlen(buffer), 0);
                }
            }
        }
    }

    free(fds);
    return 0;
}
