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

void *clientHandler(void *arg) {
    int *nsocket = (int *)arg;
    char buffer[1024];
    int n;

    while (1) {
        n = recv(*nsocket, buffer, sizeof(buffer), 0);
        if (n <= 0) {
            if (n < 0)
                perror("Error in receiving");
            close(*nsocket);
            printf("Client disconnected\n");
            break;
        }
        
        buffer[n] = '\0'; // Null-terminate the received data
        if (strcmp(buffer, ":exit") == 0) {
            close(*nsocket);
            printf("Client disconnected\n");
            break;
        } else {
            printf("Client: %s\n", buffer);
            send(*nsocket, buffer, strlen(buffer), 0);
        }
    }
    free(nsocket);  // Free the dynamically allocated socket descriptor
    pthread_exit(NULL);
}

int main() {
    int socketfd, *nsocket;
    struct sockaddr_in serveraddress;
    struct sockaddr_in newaddress;
    socklen_t address_size;
    pthread_t tid;

    socketfd = socket(AF_INET, SOCK_STREAM, 0);
    if (socketfd < 0) {
        perror("Error in socket");
        exit(1);
    }
    printf("[+]Server Socket is created.\n");

    memset(&serveraddress, 0, sizeof(serveraddress));
    serveraddress.sin_family = AF_INET;
    serveraddress.sin_port = htons(PORT);
    serveraddress.sin_addr.s_addr = INADDR_ANY; // Listen on all available network interfaces

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

    while (1) {
        address_size = sizeof(newaddress);
        nsocket = (int *)malloc(sizeof(int)); // Allocate a new socket descriptor
        *nsocket = accept(socketfd, (struct sockaddr *)&newaddress, &address_size);
        if (*nsocket < 0) {
            perror("Error in accepting");
            free(nsocket); // Free the allocated socket descriptor
            exit(1);
        }
        printf("Connection accepted from %s:%d\n", inet_ntoa(newaddress.sin_addr), ntohs(newaddress.sin_port));

        if (pthread_create(&tid, NULL, clientHandler, nsocket) != 0) {
            perror("Error in creating thread");
            free(nsocket); // Free the allocated socket descriptor
            exit(1);
        }
    }

    // The server will keep running and handling multiple clients using threads.

    close(socketfd); // Close the server socket (not recommended for a production server)

    return 0;
}
