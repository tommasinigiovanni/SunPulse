"""
Real-Time Data Broadcaster

Background service that broadcasts device data and alarms to WebSocket clients.
Integrates with Celery tasks for automatic data collection and broadcasting.
"""
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
import structlog

from .websocket_manager import get_connection_manager
from .zcs_api_service import get_zcs_service
from .cache_service import get_cache_service, DataType, make_device_cache_key

logger = structlog.get_logger()


class RealtimeBroadcaster:
    """
    Real-time data broadcaster

    Broadcasts device data, status changes, and alarms to subscribed WebSocket clients.
    """

    def __init__(self):
        self.manager = get_connection_manager()
        self._running = False
        logger.info("RealtimeBroadcaster initialized")

    async def broadcast_device_data(
        self,
        device_thing_key: str,
        data: Dict[str, Any],
        event_type: str = "realtime_update"
    ) -> int:
        """
        Broadcast device real-time data to subscribed clients

        Args:
            device_thing_key: Device identifier
            data: Real-time data dictionary
            event_type: Event type (default: realtime_update)

        Returns:
            int: Number of clients that received the message
        """
        message = {
            "event": event_type,
            "thing_key": device_thing_key,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }

        count = await self.manager.broadcast_to_device_subscribers(
            message,
            device_thing_key
        )

        if count > 0:
            logger.debug(
                "Device data broadcasted",
                device=device_thing_key,
                event=event_type,
                recipients=count
            )

        return count

    async def broadcast_device_status(
        self,
        device_thing_key: str,
        status: str,
        previous_status: Optional[str] = None,
        reason: Optional[str] = None
    ) -> int:
        """
        Broadcast device status change to subscribed clients

        Args:
            device_thing_key: Device identifier
            status: New status
            previous_status: Previous status
            reason: Optional reason for status change

        Returns:
            int: Number of clients that received the message
        """
        data = {
            "thing_key": device_thing_key,
            "status": status,
            "previous_status": previous_status,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }

        message = {
            "event": "device_status",
            "thing_key": device_thing_key,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }

        count = await self.manager.broadcast_to_device_subscribers(
            message,
            device_thing_key
        )

        logger.info(
            "Device status broadcasted",
            device=device_thing_key,
            status=status,
            recipients=count
        )

        return count

    async def broadcast_alarm(
        self,
        device_thing_key: str,
        alarm: Dict[str, Any],
        alarm_action: str = "triggered"
    ) -> int:
        """
        Broadcast alarm event to subscribed clients

        Args:
            device_thing_key: Device identifier
            alarm: Alarm data dictionary
            alarm_action: Action type (triggered, acknowledged, resolved)

        Returns:
            int: Number of clients that received the message
        """
        event = f"alarm_{alarm_action}" if alarm_action != "triggered" else "new_alarm"

        message = {
            "event": event,
            "thing_key": device_thing_key,
            "data": {
                "action": alarm_action,
                "alarm": alarm
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        # Broadcast to device subscribers
        device_count = await self.manager.broadcast_to_device_subscribers(
            message,
            device_thing_key
        )

        # Also broadcast critical alarms to all clients
        if alarm.get("severity") == "critical":
            all_count = await self.manager.broadcast(message)
            logger.info(
                "Critical alarm broadcasted to all clients",
                device=device_thing_key,
                alarm_code=alarm.get("alarm_code"),
                recipients=all_count
            )
            return all_count

        logger.info(
            "Alarm broadcasted",
            device=device_thing_key,
            alarm_code=alarm.get("alarm_code"),
            action=alarm_action,
            recipients=device_count
        )

        return device_count

    async def broadcast_system_notification(
        self,
        notification_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Broadcast system-wide notification to all clients

        Args:
            notification_type: Type of notification
            message: Notification message
            data: Optional additional data

        Returns:
            int: Number of clients that received the message
        """
        notification = {
            "event": "system.notification",
            "data": {
                "type": notification_type,
                "message": message,
                "details": data or {}
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        count = await self.manager.broadcast(notification)

        logger.info(
            "System notification broadcasted",
            type=notification_type,
            recipients=count
        )

        return count

    async def fetch_and_broadcast_device_data(
        self,
        device_thing_key: str,
        use_cache: bool = True
    ) -> bool:
        """
        Fetch device data and broadcast to subscribers

        Args:
            device_thing_key: Device identifier
            use_cache: Use cached data if available

        Returns:
            bool: True if successful
        """
        try:
            cache_service = await get_cache_service()
            zcs_service = await get_zcs_service()

            # Try cache first
            data = None
            if use_cache:
                cache_key = make_device_cache_key(device_thing_key, DataType.REALTIME)
                data = await cache_service.get(cache_key, DataType.REALTIME)

            # Fetch from ZCS if no cache
            if not data:
                data = await zcs_service.get_realtime_data([device_thing_key])
                if data and device_thing_key in data:
                    data = data[device_thing_key]

            if data:
                await self.broadcast_device_data(device_thing_key, data)
                return True
            else:
                logger.warning(
                    "No data available for broadcast",
                    device=device_thing_key
                )
                return False

        except Exception as e:
            logger.error(
                "Error fetching and broadcasting device data",
                device=device_thing_key,
                error=str(e)
            )
            return False


# Global broadcaster instance
_broadcaster: Optional[RealtimeBroadcaster] = None


def get_broadcaster() -> RealtimeBroadcaster:
    """
    Get or create global RealtimeBroadcaster instance

    Returns:
        RealtimeBroadcaster: Global broadcaster
    """
    global _broadcaster

    if _broadcaster is None:
        _broadcaster = RealtimeBroadcaster()

    return _broadcaster


# Convenience functions for use in Celery tasks and other services

async def broadcast_device_update(
    device_thing_key: str,
    data: Dict[str, Any]
) -> int:
    """
    Convenience function to broadcast device data update

    Args:
        device_thing_key: Device identifier
        data: Device data

    Returns:
        int: Number of recipients
    """
    broadcaster = get_broadcaster()
    return await broadcaster.broadcast_device_data(device_thing_key, data)


async def broadcast_status_change(
    device_thing_key: str,
    new_status: str,
    old_status: Optional[str] = None
) -> int:
    """
    Convenience function to broadcast device status change

    Args:
        device_thing_key: Device identifier
        new_status: New status
        old_status: Previous status

    Returns:
        int: Number of recipients
    """
    broadcaster = get_broadcaster()
    return await broadcaster.broadcast_device_status(
        device_thing_key,
        new_status,
        old_status
    )


async def broadcast_alarm_event(
    device_thing_key: str,
    alarm: Dict[str, Any],
    action: str = "triggered"
) -> int:
    """
    Convenience function to broadcast alarm event

    Args:
        device_thing_key: Device identifier
        alarm: Alarm data
        action: Alarm action (triggered, acknowledged, resolved)

    Returns:
        int: Number of recipients
    """
    broadcaster = get_broadcaster()
    return await broadcaster.broadcast_alarm(device_thing_key, alarm, action)
