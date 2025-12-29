
from fastapi import APIRouter, BackgroundTasks
from app.tasks.binance_prices import run_binance_update

router = APIRouter(prefix="/tasks", tags=["background"])

@router.post("/run")
async def run_binance_task(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_binance_update)
    return {"status": "started"}
