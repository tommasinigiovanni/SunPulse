"""
WebSocket Endpoint

Real-time bidirectional communication endpoint for device data,
alarms, and system notifications.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import uuid
import json
import structlog
from datetime import datetime

from ....services.websocket_manager import get_connection_manager

logger = structlog.get_logger()

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None, description="Optional client identifier"),
    token: Optional[str] = Query(None, description="Optional authentication token")
):
    """
    WebSocket endpoint for real-time communication

    **Connection URL:**
    ```
    ws://localhost:8000/api/v1/ws?client_id=client123&token=optional_token
    ```

    **Client Message Format:**
    ```json
    {
        "event": "subscribe|unsubscribe|ping|request_data",
        "data": {
            "devices": ["device_key_1", "device_key_2"]
        }
    }
    ```

    **Server Message Format:**
    ```json
    {
        "event": "realtime_update|device_status|new_alarm|alarm_resolved",
        "thing_key": "device_key",
        "data": {...},
        "timestamp": "2024-01-01T00:00:00Z"
    }
    ```

    **Supported Client Events:**
    - `subscribe`: Subscribe to device updates
    - `unsubscribe`: Unsubscribe from device updates
    - `ping`: Heartbeat ping
    - `request_data`: Request current data for devices

    **Server Events:**
    - `connection.established`: Connection confirmed
    - `subscription.confirmed`: Subscription confirmed
    - `realtime_update`: Real-time device data update
    - `device_status`: Device status change
    - `new_alarm`: New alarm triggered
    - `alarm_resolved`: Alarm resolved
    - `connection.pong`: Heartbeat pong response
    """
    manager = get_connection_manager()

    # Generate client_id if not provided
    if not client_id:
        client_id = str(uuid.uuid4())

    # Connection metadata
    metadata = {
        "user_agent": websocket.headers.get("user-agent", "unknown"),
        "token": bool(token),  # Don't log actual token
    }

    try:
        # Accept connection
        await manager.connect(websocket, client_id, metadata)

        logger.info(
            "WebSocket connection established",
            client_id=client_id,
            metadata=metadata
        )

        # Main message loop
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)

                event = message.get("event")
                payload = message.get("data", {})

                logger.debug(
                    "WebSocket message received",
                    client_id=client_id,
                    event=event,
                    payload=payload
                )

                # Handle different event types
                if event == "subscribe":
                    # Subscribe to devices
                    devices = payload.get("devices", [])
                    if devices:
                        await manager.subscribe(client_id, devices)
                    else:
                        await manager.send_personal_message(
                            {
                                "event": "error",
                                "data": {
                                    "message": "No devices specified for subscription"
                                },
                                "timestamp": datetime.utcnow().isoformat()
                            },
                            client_id
                        )

                elif event == "unsubscribe":
                    # Unsubscribe from devices
                    devices = payload.get("devices", [])
                    if devices:
                        await manager.unsubscribe(client_id, devices)
                    else:
                        await manager.send_personal_message(
                            {
                                "event": "error",
                                "data": {
                                    "message": "No devices specified for unsubscription"
                                },
                                "timestamp": datetime.utcnow().isoformat()
                            },
                            client_id
                        )

                elif event == "ping":
                    # Heartbeat
                    await manager.handle_heartbeat(client_id)

                elif event == "request_data":
                    # Client requests current data
                    devices = payload.get("devices", [])
                    await manager.send_personal_message(
                        {
                            "event": "data.requested",
                            "data": {
                                "message": f"Data request received for {len(devices)} devices",
                                "devices": devices,
                                "note": "Data will be sent when available"
                            },
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        client_id
                    )

                elif event == "get_stats":
                    # Get connection statistics
                    stats = manager.get_connection_stats()
                    await manager.send_personal_message(
                        {
                            "event": "stats",
                            "data": stats,
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        client_id
                    )

                else:
                    # Unknown event
                    await manager.send_personal_message(
                        {
                            "event": "error",
                            "data": {
                                "message": f"Unknown event type: {event}"
                            },
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        client_id
                    )

            except json.JSONDecodeError as e:
                logger.error(
                    "Invalid JSON received",
                    client_id=client_id,
                    error=str(e)
                )
                await manager.send_personal_message(
                    {
                        "event": "error",
                        "data": {
                            "message": "Invalid JSON format"
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    client_id
                )

            except Exception as e:
                logger.error(
                    "Error processing WebSocket message",
                    client_id=client_id,
                    error=str(e)
                )
                await manager.send_personal_message(
                    {
                        "event": "error",
                        "data": {
                            "message": "Error processing message"
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    client_id
                )

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected normally", client_id=client_id)
        await manager.disconnect(client_id)

    except Exception as e:
        logger.error(
            "WebSocket connection error",
            client_id=client_id,
            error=str(e)
        )
        await manager.disconnect(client_id)


@router.get("/ws/stats")
async def get_websocket_stats():
    """
    Get WebSocket connection statistics

    Returns information about active connections,
    subscriptions, and connected clients.
    """
    manager = get_connection_manager()
    stats = manager.get_connection_stats()

    return {
        "status": "success",
        "data": stats,
        "timestamp": datetime.utcnow().isoformat()
    }
