from fastapi import APIRouter
from src.api.api_v1.endpoints import graph, graph_bulk, graph_analysis, nodes, edges

api_router = APIRouter()
api_router.include_router(graph.router, tags=["graph"])
api_router.include_router(graph_bulk.router, tags=["graph"])
api_router.include_router(graph_analysis.router, tags=["graph"])
api_router.include_router(nodes.router, tags=["nodes"])
api_router.include_router(edges.router, tags=["edges"])
