import grpc
import seller_pb2
import seller_pb2_grpc

def register_seller():
    channel = grpc.insecure_channel('localhost:50051')
    stub = seller_pb2_grpc.MarketStub(channel)
    response = stub.Register(seller_pb2.RegisterRequest(
        seller_info=seller_pb2.SellerInfo(
            ip_address="192.13.188.178:50051",
            uuid="987a515c-a6e5-11ed-906b-76aef1e817c5"
        )
    ))
    print("Seller prints:", "SUCCESS" if response.status == seller_pb2.RegisterResponse.Status.SUCCESS else "FAIL")

if __name__ == '__main__':
    register_seller()
