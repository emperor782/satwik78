import grpc
from concurrent import futures
import time

import market_pb2
import market_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class MarketServicer(market_pb2_grpc.MarketServicer):

    def __init__(self):
        self.sellers = {}
        self.items = {}

    def RegisterSeller(self, request, context):
        if request.address not in self.sellers:
            self.sellers[request.address] = request.uuid
            print(f"Seller join request from {request.address}, uuid = {request.uuid}")
            return market_pb2.RegisterSellerResponse(status=market_pb2.RegisterSellerResponse.SUCCESS)
        else:
            return market_pb2.RegisterSellerResponse(status=market_pb2.RegisterSellerResponse.FAILED)

    def SellItem(self, request, context):
        item_id = len(self.items) + 1
        self.items[item_id] = {
            "product_name": request.product_name,
            "category": request.category,
            "quantity": request.quantity,
            "description": request.description,
            "seller_address": request.seller_address,
            "price": request.price
        }
        print(f"Sell Item request from {request.seller_address}")
        return market_pb2.SellItemResponse(status=market_pb2.SellItemResponse.SUCCESS, item_id=item_id)

    def UpdateItem(self, request, context):
        if request.item_id in self.items:
            self.items[request.item_id]["price"] = request.new_price
            self.items[request.item_id]["quantity"] = request.new_quantity
            print(f"Update Item {request.item_id} request from {request.seller_address}")
            return market_pb2.UpdateItemResponse(status=market_pb2.UpdateItemResponse.SUCCESS)
        else:
            return market_pb2.UpdateItemResponse(status=market_pb2.UpdateItemResponse.FAILED)

    def DeleteItem(self, request, context):
        if request.item_id in self.items:
            del self.items[request.item_id]
            print(f"Delete Item {request.item_id} request from {request.seller_address}")
            return market_pb2.DeleteItemResponse(status=market_pb2.DeleteItemResponse.SUCCESS)
        else:
            return market_pb2.DeleteItemResponse(status=market_pb2.DeleteItemResponse.FAILED)

    def DisplaySellerItems(self, request, context):
        seller_items = []
        for item_id, item_info in self.items.items():
            if item_info["seller_address"] == request.seller_address:
                item = market_pb2.DisplaySellerItemsResponse.Item(
                    item_id=item_id,
                    price=item_info["price"],
                    name=item_info["product_name"],
                    category=item_info["category"],
                    description=item_info["description"],
                    quantity_remaining=item_info["quantity"],
                    seller_address=item_info["seller_address"],
                    rating=0.0  # Placeholder for rating, to be implemented
                )
                seller_items.append(item)
        return market_pb2.DisplaySellerItemsResponse(items=seller_items)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    market_pb2_grpc.add_MarketServicer_to_server(MarketServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Market Server is running...")
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()

