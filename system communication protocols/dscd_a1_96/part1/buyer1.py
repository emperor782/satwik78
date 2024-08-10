import grpc
import client_pb2
import client_pb2_grpc

def search_item():
    channel = grpc.insecure_channel('localhost:50051')
    stub = client_pb2_grpc.MarketStub(channel)
    response = stub.Search(client_pb2.SearchRequest(
        item_name="",
        category=client_pb2.SearchRequest.Category.ANY
    ))
    print("Buyer prints:")
    for item in response.items:
        print(f"Item ID: {item.id}, Price: ${item.price}, Name: {item.name}, Category: {item.category.name}, Description: {item.description}, Quantity Remaining: {item.quantity}, Seller: {item.seller_info.ip_address}")

if __name__ == '__main__':
    search_item()
