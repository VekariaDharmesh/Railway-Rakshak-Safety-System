from fastapi import APIRouter
from .auth import router as auth_router
from .dashboard import router as dashboard_router
from .nodes import router as nodes_router
from .corridors import router as corridors_router
from .telemetry import router as telemetry_router
from .threats import router as threats_router
from .incidents import router as incidents_router
from .dispatch import router as dispatch_router
from .drones import router as drones_router
from .predictions import router as predictions_router
from .environment import router as environment_router
from .ledger import router as ledger_router
from .system import router as system_router
from .search import router as search_router
from .stream import router as stream_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(dashboard_router)
api_router.include_router(nodes_router)
api_router.include_router(corridors_router)
api_router.include_router(telemetry_router)
api_router.include_router(threats_router)
api_router.include_router(incidents_router)
api_router.include_router(dispatch_router)
api_router.include_router(drones_router)
api_router.include_router(predictions_router)
api_router.include_router(environment_router)
api_router.include_router(ledger_router)
api_router.include_router(system_router)
api_router.include_router(search_router)
api_router.include_router(stream_router)
