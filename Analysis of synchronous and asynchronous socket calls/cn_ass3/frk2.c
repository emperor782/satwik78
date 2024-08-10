#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <inttypes.h>

#define PORT 4444

// Function to calculate the factorial
uint64_t fact(uint64_t n) {
    if (n > 20) {
        n = 20;
    }
    uint64_t result = 1;
    for (uint64_t i = 1; i <= n; i++) {
        result *= i;
    }
    return result;
    
}

int main() {
    int socketfd, nsocket;
    struct sockaddr_in serveraddress;
    struct sockaddr_in newaddress;
    socklen_t address_size;
    char buffer[1024];

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

    if (bind(socketfd, (struct sockaddr*)&serveraddress, sizeof(serveraddress)) < 0) {
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

    while (1) {
        address_size = sizeof(newaddress);
        nsocket = accept(socketfd, (struct sockaddr*)&newaddress, &address_size);
        if (nsocket < 0) {
            perror("Error in accepting");
            exit(1);
        }
        printf("Connection accepted from %s:%d\n", inet_ntoa(newaddress.sin_addr), ntohs(newaddress.sin_port));

        if (fork() == 0) {
            close(socketfd);

            while (1) {
                bzero(buffer, sizeof(buffer));
                recv(nsocket, buffer, sizeof(buffer), 0);
                if (strcmp(buffer, ":exit") == 0) {
                    printf("Disconnected from %s:%d\n", inet_ntoa(newaddress.sin_addr), ntohs(newaddress.sin_port));
                    close(nsocket);
                    exit(0);
                } else {
                    uint64_t n;
                    sscanf(buffer, "%" PRIu64, &n); // Parse the received number
                    uint64_t result = fact(n);

                    char response[1024];
                    snprintf(response, sizeof(response), "Factorial of %" PRIu64 " is %" PRIu64, n, result);
                    printf("Client (%s:%d): %s\n", inet_ntoa(newaddress.sin_addr), ntohs(newaddress.sin_port), response);
                    send(nsocket, response, strlen(response), 0);
                }
            }
        } else {
            close(nsocket);
        }
    }

    return 0;
}
