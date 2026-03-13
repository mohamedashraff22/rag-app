"""Middleware"""

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

# Define metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP Requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP Request Latency", ["method", "endpoint"]
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    # function that will always be used for every request will pass on it.
    async def dispatch(self, request: Request, call_next):  # شكل ثابت

        start_time = time.time()

        # Process the request
        response = await call_next(request)

        # Record metrics after request is processed
        duration = time.time() - start_time
        endpoint = request.url.path

        REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(
            duration
        )
        REQUEST_COUNT.labels(
            method=request.method, endpoint=endpoint, status=response.status_code
        ).inc()

        return response  # if i dont return response , the middleware will block every thing.


def setup_metrics(app: FastAPI):
    """
    Setup Prometheus metrics middleware and endpoint
    """
    # Add Prometheus middleware
    app.add_middleware(PrometheusMiddleware)

    # this end point i will get all the data analyics i want.
    # include_in_schema=False -> if i go to docs i will not find this endpoint as it so sensetive.
    # generate_latest(), media_type=CONTENT_TYPE_LATEST -> get the lastest data analytics.
    # @app.get("/metrics") is so easy to be predicted and i dont want it to be available for user, so using random name will be more secure.
    @app.get("/TrhBVe_m5gg2002_E5VVqS", include_in_schema=False)
    def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
