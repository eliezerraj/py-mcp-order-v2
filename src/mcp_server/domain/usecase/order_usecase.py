import logging
from src.mcp_server.domain.dto.context import SecurityContext

logger = logging.getLogger(__name__)

class OrderUseCase:
    
    def __init__(self, http_adapter):
        logger.info("OrderUseCase initialized SUCCESSFULLY.")
        self.http_adapter = http_adapter
            
    async def get_order_service_info(self):
        logger.info(f"Fetching order service info asynchronously")
        
        try:
            response = await self.http_adapter.request(
                method="GET",
                path="/v1/info",
                params=None,
            )
        except Exception as e:
            logger.error(f"Error fetching order service info asynchronously: {e}")
            response = {"message": str(e)}
        
        return response

    async def get_order(self, sku):
        logger.info(f"Fetching order for sku: {sku}")
        
        try:
            path = f"/v1/order/{sku}"
            response = await self.http_adapter.request(
                method="GET",
                path=path,
                params={"id": sku},
            )
        except Exception as e:
            logger.error(f"Error fetching order for sku {sku}: {e}")
            response = {"message": str(e)}

        return response    
 
    async def post_order(self, payload: dict):
        logger.info(f"Creating order: {payload}")
        
        try:
            path = "/v1/order"
            response = await self.http_adapter.request(
                method="POST",
                path=path,
                payload=payload,
            )
        except Exception as e:
            logger.error(f"Error creating order with payload {payload}: {e}")
            response = {"message": str(e)}

        return response   

    async def post_checkout(self, payload: dict):
        logger.info(f"Creating checkout: {payload}")
        
        try:
            path = "/v1/order/checkout"
            response = await self.http_adapter.request(
                method="POST",
                path=path,
                payload=payload,
            )
        except Exception as e:
            logger.error(f"Error creating checkout with payload {payload}: {e}")
            response = {"message": str(e)}

        return response 
    
    # ----------------
    # Data Providers
    # ---------------
    async def get_time_series_order_items(self, product, limit=7, offset=0):
        logger.info(f"Fetching time series order items for product: {product}")
        
        try:
            path = f"/v1/order/time-series-order-items?product={product}&limit={limit}&offset={offset}"
            response = await self.http_adapter.request(
                method="GET",
                path=path,
                params={"product": product, "limit": limit, "offset": offset},
            )
        except Exception as e:
            logger.error(f"Error fetching order for product {product}: {e}")
            response = {"message": str(e)}

        return response 