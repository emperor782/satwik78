#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>

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

void *clientHandler(void *arg) {
    int *newSocket = (int *)arg;
    char buffer[1024];
    int n;

    while (1) {
        n = recv(*newSocket, buffer, sizeof(buffer), 0);
        if (n <= 0) {
            if (n < 0)
                perror("Error in receiving");
            close(*newSocket);
            printf("Client disconnected\n");
            break;
        }

        buffer[n] = '\0'; // Null-terminate the received data

        // Convert the received data to a 64-bit unsigned integer
        unsigned long long input;
        if (sscanf(buffer, "%llu", &input) == 1) {
            // Calculate the factorial
            unsigned long long result = fact(input);
            char response[1024];
            snprintf(response, sizeof(response), "Factorial of %llu: %llu\n", input, result);

            // Send the response back to the client
            int bytes_sent = send(*newSocket, response, strlen(response), 0);
            if (bytes_sent < 0) {
                perror("Error in sending");
            } else {
                printf("Sent response: %s", response);
            }
        } else {
            // Invalid input, send an error message
            send(*newSocket, "Invalid input. Please send a valid number.\n", 44, 0);
        }
    }
    free(newSocket);  // Free the dynamically allocated socket descriptor
    pthread_exit(NULL);
}

int main() {
    int sockfd, *newSocket;
    struct sockaddr_in serverAddr;
    struct sockaddr_in newAddr;
    socklen_t addr_size;
    pthread_t tid;

    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("Error in socket");
        exit(1);
    }
    printf("[+]Server Socket is created.\n");

    memset(&serverAddr, 0, sizeof(serverAddr));
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(PORT);
    serverAddr.sin_addr.s_addr = INADDR_ANY; // Listen on all available network interfaces

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

    while (1) {
        addr_size = sizeof(newAddr);
        newSocket = (int *)malloc(sizeof(int)); // Allocate a new socket descriptor
        *newSocket = accept(sockfd, (struct sockaddr *)&newAddr, &addr_size);
        if (*newSocket < 0) {
            perror("Error in accepting");
            free(newSocket); // Free the allocated socket descriptor
            exit(1);
        }
        printf("Connection accepted from %s:%d\n", inet_ntoa(newAddr.sin_addr), ntohs(newAddr.sin_port));

        if (pthread_create(&tid, NULL, clientHandler, newSocket) != 0) {
            perror("Error in creating thread");
            free(newSocket); // Free the allocated socket descriptor
            exit(1);
        }
    }

    // The server will keep running and handling multiple clients using threads.

    close(sockfd); // Close the server socket (not recommended for a production server)

    return 0;
}
