import structlog
from fastapi import WebSocket, WebSocketDisconnect

log = structlog.get_logger()


async def stream_handler(websocket: WebSocket, run_id: str) -> None:
    await websocket.accept()
    log.info("ws.connected", run_id=run_id)
    try:
        # TODO: subscribe to run_id channel in Redis and forward messages
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        log.info("ws.disconnected", run_id=run_id)
