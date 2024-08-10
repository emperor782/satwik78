import grpc
import sys
import random
import os
from concurrent import futures
from collections import defaultdict

# Import generated gRPC classes
import map_reduce_pb2
import map_reduce_pb2_grpc

# Define gRPC communication details
RPC_TIMEOUT = 10
MAX_MESSAGE_LENGTH = 1024 * 1024 * 1024  # 1GB
MAX_WORKERS = 10

# Define K-means parameters
NUM_MAPPERS = 3
NUM_REDUCERS = 2
NUM_CENTROIDS = 3
NUM_ITERATIONS = 10

# Global variables
centroids = []
mapper_responses = defaultdict(list)
reducer_responses = defaultdict(list)


def initialize_centroids():
    global centroids
    centroids = []
    with open("data3/inputc/points2.txt", "r") as file:
        points = file.readlines()
    random.shuffle(points)
    centroids = [map_reduce_pb2.Point(x=float(point.split(', ')[0]), y=float(point.split(', ')[1])) for point in points[:NUM_CENTROIDS]]


def euclidean_distance(point1, point2):
    return ((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2) ** 0.5


# Function to assign points to the nearest centroid
def assign_points_to_centroids(points):
    assignments = defaultdict(list)
    for point in points:
        min_distance = float('inf')
        closest_centroid = None
        for centroid_id, centroid in enumerate(centroids):
            distance = euclidean_distance(point, centroid)
            if distance < min_distance:
                min_distance = distance
                closest_centroid = centroid_id
        assignments[closest_centroid].append(point)
    return assignments


# Mapper class
class MapperServicer(map_reduce_pb2_grpc.MapperServicer):
    def Map(self, request, context):
        global centroids
        # Read data points from the input split
        split_path = f"data3/inputc/{request.split_path}"
        with open(split_path, "r") as file:
            data_points = [map_reduce_pb2.Point(x=float(line.split(',')[0]), y=float(line.split(',')[1])) for line in file.readlines()]

        # Assign data points to centroids
        assignments = assign_points_to_centroids(data_points)

        os.makedirs(f"data3/Mappers/M{request.mapper_id}", exist_ok=True)

        # Partition key-value pairs
        partitions = [[] for _ in range(NUM_REDUCERS)]
        for centroid_id, points in assignments.items():
            for point in points:
                partitions[centroid_id % NUM_REDUCERS].append((centroid_id, point))

        # Write intermediate key-value pairs to partition files
        for reducer_id, partition in enumerate(partitions, start=1):
            partition_dir = f"data3/Mappers/M{request.mapper_id}"
            with open(f"{partition_dir}/partition_{reducer_id}.txt", "a") as partition_file:
                for centroid_id, point in partition:
                    partition_file.write(f"{centroid_id},{point.x},{point.y}\n")

        # Introduce probabilistic failure
        if random.random() >= 0.5:  # Adjust probability as needed
            return map_reduce_pb2.MapResponse(message="FAILED")
        else:
            return map_reduce_pb2.MapResponse(message="SUCCESS")

    def GetPartitionData(self, request, context):
        partition_path = f"data3/Mappers/M{request.mapper_id}/partition_{request.reducer_id}.txt"
        with open(partition_path, "r") as file:
            lines = file.readlines()

        return map_reduce_pb2.PartitionData(lines=lines)


# Reducer class
class ReducerServicer(map_reduce_pb2_grpc.ReducerServicer):
    def Reduce(self, request, context):
        channel = grpc.insecure_channel('localhost:50051')  # Assuming mapper is running on localhost:50051
        stub = map_reduce_pb2_grpc.MapperStub(channel)
        response = stub.GetPartitionData(map_reduce_pb2.ReducerRequest(mapper_id=request.mapper_id, reducer_id=request.reducer_id))

        lines = response.lines
        # Group values by key
        grouped_values = defaultdict(list)
        for line in lines:
            centroid_id, x, y = map(float, line.strip().split(','))
            grouped_values[int(centroid_id)].append(map_reduce_pb2.Point(x=x, y=y))

        # Sort the values by key
        sorted_values = sorted(grouped_values.items())

        reducer_output_path = f"data3/Reducers/R{request.reducer_id}.txt"
        with open(reducer_output_path, "w") as file:
            file.write("")

        for centroid_id, points in sorted_values:
            # Apply Reduce function
            new_centroid = map_reduce_pb2.Point()
            new_centroid.x = sum(point.x for point in points) / len(points)
            new_centroid.y = sum(point.y for point in points) / len(points)

            # Write updated centroid to file
            with open(reducer_output_path, "a") as file:
                file.write(f"{centroid_id},{new_centroid.x},{new_centroid.y}\n")

        # Introduce probabilistic failure
        if random.random() >= 0.5:  # Adjust probability as needed
            return map_reduce_pb2.ReduceResponse(message="FAILED")
        else:
            return map_reduce_pb2.ReduceResponse(message="SUCCESS")


# Function to start gRPC server for mapper
def start_mapper_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS),
                         options=[('grpc.max_message_length', MAX_MESSAGE_LENGTH)])
    map_reduce_pb2_grpc.add_MapperServicer_to_server(MapperServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


# Function to start gRPC server for reducer
def start_reducer_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS),
                         options=[('grpc.max_message_length', MAX_MESSAGE_LENGTH)])
    map_reduce_pb2_grpc.add_ReducerServicer_to_server(ReducerServicer(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()


# Function to split input data for mappers
def split_input_data(input_file, num_mappers):
    with open(input_file, "r") as file:
        lines = file.readlines()

    total_lines = len(lines)
    lines_per_mapper = total_lines // num_mappers
    remainder = total_lines % num_mappers

    start = 0
    for mapper_id in range(1, num_mappers + 1):
        end = start + lines_per_mapper
        if remainder > 0:
            end += 1
            remainder -= 1

        output_file = f"data3/inputc/input_{mapper_id}.txt"
        with open(output_file, "w") as out_file:
            out_file.writelines(lines[start:end])

        start = end


# Function to run the master program
def run_master():
    with open(r"log.txt", "w") as file:
        file.write("hello master\n")
    with open(r"log.txt", "a") as log:
        for iteration in range(NUM_ITERATIONS):
            log.write(f"Iteration number: {iteration + 1}\n")

            # Initialize centroids (randomly for the first iteration)
            if iteration == 0:
                initialize_centroids()

            # Execute gRPC calls to Mappers
            log.write("Execution of gRPC calls to Mappers:\n")
            split_input_data('data3/inputc/points2.txt', NUM_MAPPERS)
            for mapper_id in range(1, NUM_MAPPERS + 1):
                # Send parameters to mapper
                channel = grpc.insecure_channel(f'localhost:50051')
                stub = map_reduce_pb2_grpc.MapperStub(channel)
                request = map_reduce_pb2.MapRequest(split_path=f"input_{mapper_id}.txt", mapper_id=mapper_id)
                try:
                    response = stub.Map(request, timeout=RPC_TIMEOUT)
                    log.write(f"Mapper {mapper_id}: {response.message}\n")
                    mapper_responses[mapper_id].append(response)
                    if response.message=="FAILED":
                        while True:
                            # If mapper fails, re-run the task
                            response = stub.Map(request, timeout=RPC_TIMEOUT)
                            log.write(f"Retry - Mapper {mapper_id}: {response.message}\n")
                            mapper_responses[mapper_id].append(response)
                            if response.message=="SUCCESS":
                                break
                except grpc.RpcError as e:
                    log.write(f"Mapper {mapper_id}: {e}\n")
                

            # Execute gRPC calls to Reducers after all Mappers finish
            log.write("Execution of gRPC calls to Reducers:\n")
            for map_id in range(1, NUM_MAPPERS + 1):
                for reducer_id in range(1, NUM_REDUCERS + 1):
                    channel = grpc.insecure_channel(f'localhost:50052')
                    stub = map_reduce_pb2_grpc.ReducerStub(channel)
                    request = map_reduce_pb2.ReducerRequest(mapper_id=map_id, reducer_id=reducer_id)
                    try:
                        response = stub.Reduce(request, timeout=RPC_TIMEOUT)
                        log.write(f"Reducer {reducer_id}: {response.message}\n")
                        reducer_responses[reducer_id].append(response)
                        if response.message=="FAILED":
                            while True:
                            # If reducer fails, re-run the task
                                response = stub.Reduce(request, timeout=RPC_TIMEOUT)
                                log.write(f"Retry - Reducer {reducer_id}: {response.message}\n")
                                reducer_responses[reducer_id].append(response)
                                if response.message=="SUCCESS":
                                    break
                    except grpc.RpcError as e:
                        log.write(f"Reducer {reducer_id}: {e}\n")
                        

            # Parse reducer outputs to compile final centroids
            new_centroids = []
            for reducer_id in range(1, NUM_REDUCERS + 1):
                reducer_output_path = f"data3/Reducers/R{reducer_id}.txt"
                if os.path.exists(reducer_output_path):
                    with open(reducer_output_path, "r") as file:
                        lines = file.readlines()
                        k = len(lines)
                        for i in range(k):
                            centroid_id, x, y = map(float, lines[i].strip().split(','))
                            new_centroids.append(map_reduce_pb2.Point(x=x, y=y))

            # Update centroids
            global centroids
            centroids = new_centroids

            # Log centroids generated after each iteration
            log.write(f"Centroids after iteration {iteration + 1}:\n")
            for centroid in centroids:
                log.write(f"{centroid.x},{centroid.y}\n")

            if iteration==9:
                with open("data3/output.txt", "w") as file:
                    file.write("final centroids\n")
                for centroid in centroids:
                    with open("data3/output.txt", "a") as file:
                        file.write(f"{centroid.x},{centroid.y}\n")
                
if __name__ == "__main__":
    # Start mapper and reducer servers in separate threads
    mapper_server_thread = futures.ThreadPoolExecutor(max_workers=1).submit(start_mapper_server)
    reducer_server_thread = futures.ThreadPoolExecutor(max_workers=1).submit(start_reducer_server)

    # Run master program
    run_master()

    # Wait for mapper and reducer server threads to finish
    mapper_server_thread.result()
    reducer_server_thread.result()
    
    print("completed successfully\n")
    sys.exit()
    