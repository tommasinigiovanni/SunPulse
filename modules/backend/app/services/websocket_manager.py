"""
WebSocket Connection Manager

Manages WebSocket connections, subscriptions, and real-time data broadcasting.
Supports device-specific subscriptions and bulk broadcasts.
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, Optional, Any, List
from datetime import datetime
import json
import asyncio
import structlog

logger = structlog.get_logger()


class ConnectionManager:
    """
    WebSocket Connection Manager

    Manages active WebSocket connections, client subscriptions,
    and message broadcasting to clients.

    Features:
    - Connection lifecycle management (connect/disconnect)
    - Device-specific subscriptions
    - Bulk broadcasting to all clients
    - Targeted messaging to specific clients
    - Heartbeat mechanism
    - Error handling and reconnection support
    """

    def __init__(self):
        # Active connections: {client_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}

        # Client subscriptions: {client_id: Set[device_thing_keys]}
        self.subscriptions: Dict[str, Set[str]] = {}

        # Reverse index: {device_thing_key: Set[client_ids]}
        self.device_subscribers: Dict[str, Set[str]] = {}

        # Heartbeat tracking: {client_id: last_heartbeat_timestamp}
        self.last_heartbeat: Dict[str, datetime] = {}

        # Connection metadata: {client_id: {connected_at, user_agent, etc}}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}

        logger.info("WebSocket ConnectionManager initialized")

    async def connect(
        self,
        websocket: WebSocket,
        client_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Accept and register a new WebSocket connection

        Args:
            websocket: WebSocket connection instance
            client_id: Unique client identifier
            metadata: Optional connection metadata (user_agent, auth, etc.)
        """
        await websocket.accept()

        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = set()
        self.last_heartbeat[client_id] = datetime.utcnow()
        self.connection_metadata[client_id] = metadata or {}
        self.connection_metadata[client_id]["connected_at"] = datetime.utcnow().isoformat()

        logger.info(
            "WebSocket client connected",
            client_id=client_id,
            total_connections=len(self.active_connections),
            metadata=metadata
        )

        # Send welcome message
        await self.send_personal_message(
            {
                "event": "connection.established",
                "data": {
                    "client_id": client_id,
                    "server_time": datetime.utcnow().isoformat(),
                    "message": "Connected to SunPulse real-time server"
                },
                "timestamp": datetime.utcnow().isoformat()
            },
            client_id
        )

    async def disconnect(self, client_id: str) -> None:
        """
        Disconnect and cleanup a client connection

        Args:
            client_id: Client identifier to disconnect
        """
        # Remove from active connections
        if client_id in self.active_connections:
            del self.active_connections[client_id]

        # Remove all subscriptions
        if client_id in self.subscriptions:
            subscribed_devices = self.subscriptions[client_id]

            # Remove from reverse index
            for device_key in subscribed_devices:
                if device_key in self.device_subscribers:
                    self.device_subscribers[device_key].discard(client_id)
                    if not self.device_subscribers[device_key]:
                        del self.device_subscribers[device_key]

            del self.subscriptions[client_id]

        # Remove heartbeat tracking
        if client_id in self.last_heartbeat:
            del self.last_heartbeat[client_id]

        # Remove metadata
        if client_id in self.connection_metadata:
            del self.connection_metadata[client_id]

        logger.info(
            "WebSocket client disconnected",
            client_id=client_id,
            remaining_connections=len(self.active_connections)
        )

    async def send_personal_message(
        self,
        message: Dict[str, Any],
        client_id: str
    ) -> bool:
        """
        Send message to a specific client

        Args:
            message: Message dictionary to send
            client_id: Target client identifier

        Returns:
            bool: True if sent successfully, False otherwise
        """
        if client_id not in self.active_connections:
            logger.warning("Client not found for personal message", client_id=client_id)
            return False

        try:
            websocket = self.active_connections[client_id]
            await websocket.send_json(message)
            return True

        except WebSocketDisconnect:
            logger.warning("Client disconnected during send", client_id=client_id)
            await self.disconnect(client_id)
            return False

        except Exception as e:
            logger.error(
                "Error sending personal message",
                client_id=client_id,
                error=str(e)
            )
            return False

    async def broadcast(
        self,
        message: Dict[str, Any],
        exclude_clients: Optional[Set[str]] = None
    ) -> int:
        """
        Broadcast message to all connected clients

        Args:
            message: Message dictionary to broadcast
            exclude_clients: Optional set of client IDs to exclude

        Returns:
            int: Number of clients that received the message
        """
        exclude_clients = exclude_clients or set()
        success_count = 0
        failed_clients = []

        for client_id, websocket in list(self.active_connections.items()):
            if client_id in exclude_clients:
                continue

            try:
                await websocket.send_json(message)
                success_count += 1

            except WebSocketDisconnect:
                logger.warning("Client disconnected during broadcast", client_id=client_id)
                failed_clients.append(client_id)

            except Exception as e:
                logger.error(
                    "Error broadcasting to client",
                    client_id=client_id,
                    error=str(e)
                )
                failed_clients.append(client_id)

        # Cleanup failed connections
        for client_id in failed_clients:
            await self.disconnect(client_id)

        if success_count > 0:
            logger.debug(
                "Broadcast completed",
                event=message.get("event"),
                recipients=success_count,
                failed=len(failed_clients)
            )

        return success_count

    async def broadcast_to_device_subscribers(
        self,
        message: Dict[str, Any],
        device_thing_key: str
    ) -> int:
        """
        Broadcast message only to clients subscribed to a specific device

        Args:
            message: Message dictionary to send
            device_thing_key: Device identifier

        Returns:
            int: Number of clients that received the message
        """
        if device_thing_key not in self.device_subscribers:
            logger.debug(
                "No subscribers for device",
                device_thing_key=device_thing_key
            )
            return 0

        subscriber_ids = self.device_subscribers[device_thing_key].copy()
        success_count = 0
        failed_clients = []

        for client_id in subscriber_ids:
            if client_id not in self.active_connections:
                failed_clients.append(client_id)
                continue

            try:
                websocket = self.active_connections[client_id]
                await websocket.send_json(message)
                success_count += 1

            except WebSocketDisconnect:
                logger.warning(
                    "Client disconnected during device broadcast",
                    client_id=client_id,
                    device_thing_key=device_thing_key
                )
                failed_clients.append(client_id)

            except Exception as e:
                logger.error(
                    "Error broadcasting to device subscriber",
                    client_id=client_id,
                    device_thing_key=device_thing_key,
                    error=str(e)
                )
                failed_clients.append(client_id)

        # Cleanup failed connections
        for client_id in failed_clients:
            await self.disconnect(client_id)

        if success_count > 0:
            logger.debug(
                "Device broadcast completed",
                device_thing_key=device_thing_key,
                recipients=success_count,
                failed=len(failed_clients)
            )

        return success_count

    async def subscribe(
        self,
        client_id: str,
        device_thing_keys: List[str]
    ) -> bool:
        """
        Subscribe client to specific devices

        Args:
            client_id: Client identifier
            device_thing_keys: List of device identifiers to subscribe to

        Returns:
            bool: True if subscribed successfully
        """
        if client_id not in self.active_connections:
            logger.warning("Client not found for subscription", client_id=client_id)
            return False

        if client_id not in self.subscriptions:
            self.subscriptions[client_id] = set()

        # Add subscriptions
        for device_key in device_thing_keys:
            self.subscriptions[client_id].add(device_key)

            # Update reverse index
            if device_key not in self.device_subscribers:
                self.device_subscribers[device_key] = set()

            self.device_subscribers[device_key].add(client_id)

        logger.info(
            "Client subscribed to devices",
            client_id=client_id,
            devices=device_thing_keys,
            total_subscriptions=len(self.subscriptions[client_id])
        )

        # Send confirmation
        await self.send_personal_message(
            {
                "event": "subscription.confirmed",
                "data": {
                    "devices": device_thing_keys,
                    "total_subscriptions": len(self.subscriptions[client_id])
                },
                "timestamp": datetime.utcnow().isoformat()
            },
            client_id
        )

        return True

    async def unsubscribe(
        self,
        client_id: str,
        device_thing_keys: List[str]
    ) -> bool:
        """
        Unsubscribe client from specific devices

        Args:
            client_id: Client identifier
            device_thing_keys: List of device identifiers to unsubscribe from

        Returns:
            bool: True if unsubscribed successfully
        """
        if client_id not in self.subscriptions:
            return False

        # Remove subscriptions
        for device_key in device_thing_keys:
            self.subscriptions[client_id].discard(device_key)

            # Update reverse index
            if device_key in self.device_subscribers:
                self.device_subscribers[device_key].discard(client_id)
                if not self.device_subscribers[device_key]:
                    del self.device_subscribers[device_key]

        logger.info(
            "Client unsubscribed from devices",
            client_id=client_id,
            devices=device_thing_keys,
            remaining_subscriptions=len(self.subscriptions[client_id])
        )

        # Send confirmation
        await self.send_personal_message(
            {
                "event": "unsubscription.confirmed",
                "data": {
                    "devices": device_thing_keys,
                    "remaining_subscriptions": len(self.subscriptions[client_id])
                },
                "timestamp": datetime.utcnow().isoformat()
            },
            client_id
        )

        return True

    async def handle_heartbeat(self, client_id: str) -> None:
        """
        Handle client heartbeat/ping

        Args:
            client_id: Client identifier
        """
        if client_id in self.last_heartbeat:
            self.last_heartbeat[client_id] = datetime.utcnow()

            # Send pong response
            await self.send_personal_message(
                {
                    "event": "connection.pong",
                    "data": {
                        "server_time": datetime.utcnow().isoformat()
                    },
                    "timestamp": datetime.utcnow().isoformat()
                },
                client_id
            )

    def get_connection_stats(self) -> Dict[str, Any]:
        """
        Get connection statistics

        Returns:
            dict: Connection statistics
        """
        total_subscriptions = sum(len(subs) for subs in self.subscriptions.values())

        return {
            "active_connections": len(self.active_connections),
            "total_subscriptions": total_subscriptions,
            "subscribed_devices": len(self.device_subscribers),
            "clients": [
                {
                    "client_id": client_id,
                    "subscriptions": list(self.subscriptions.get(client_id, [])),
                    "last_heartbeat": self.last_heartbeat.get(client_id).isoformat()
                    if client_id in self.last_heartbeat else None,
                    "metadata": self.connection_metadata.get(client_id, {})
                }
                for client_id in self.active_connections.keys()
            ]
        }


# Global connection manager instance
_connection_manager: Optional[ConnectionManager] = None


def get_connection_manager() -> ConnectionManager:
    """
    Get or create global ConnectionManager instance

    Returns:
        ConnectionManager: Global connection manager
    """
    global _connection_manager

    if _connection_manager is None:
        _connection_manager = ConnectionManager()

    return _connection_manager
