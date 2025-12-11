"""
Task monitoring endpoints - Monitoraggio task Celery e background jobs
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import structlog

from ....services.data_collector import get_task_status, celery_app
from ....services.cache_service import get_cache_service

logger = structlog.get_logger()

router = APIRouter()

@router.get("/status")
async def get_task_system_status() -> Dict[str, Any]:
    """Ottieni stato generale del sistema di task"""
    try:
        # Ottieni statistiche Celery
        inspect = celery_app.control.inspect()
        
        # Worker attivi
        active_workers = inspect.active()
        if active_workers is None:
            active_workers = {}
        
        # Task attivi
        active_tasks = inspect.active()
        if active_tasks is None:
            active_tasks = {}
        
        # Statistiche generale
        stats = inspect.stats()
        if stats is None:
            stats = {}
        
        # Task in coda
        reserved_tasks = inspect.reserved()
        if reserved_tasks is None:
            reserved_tasks = {}
        
        # Calcola riassunti
        total_active_tasks = sum(len(tasks) for tasks in active_tasks.values())
        total_reserved_tasks = sum(len(tasks) for tasks in reserved_tasks.values())
        worker_count = len(active_workers)
        
        logger.info("Task system status retrieved", 
                   workers=worker_count, 
                   active_tasks=total_active_tasks,
                   reserved_tasks=total_reserved_tasks)
        
        return {
            "system": {
                "healthy": worker_count > 0,
                "workers_connected": worker_count,
                "total_active_tasks": total_active_tasks,
                "total_reserved_tasks": total_reserved_tasks,
                "timestamp": datetime.utcnow().isoformat()
            },
            "workers": {
                worker_name: {
                    "active": len(active_tasks.get(worker_name, [])),
                    "reserved": len(reserved_tasks.get(worker_name, [])),
                    "stats": stats.get(worker_name, {})
                }
                for worker_name in active_workers.keys()
            }
        }
        
    except Exception as e:
        logger.error("Error getting task system status", error=str(e))
        return {
            "system": {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            },
            "workers": {}
        }

@router.get("/active")
async def get_active_tasks() -> List[Dict[str, Any]]:
    """Ottieni lista task attualmente in esecuzione"""
    try:
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        
        if not active_tasks:
            return []
        
        all_tasks = []
        for worker_name, tasks in active_tasks.items():
            for task in tasks:
                task_info = {
                    "task_id": task.get('id'),
                    "name": task.get('name'),
                    "worker": worker_name,
                    "args": task.get('args'),
                    "kwargs": task.get('kwargs'),
                    "time_start": task.get('time_start'),
                    "acknowledged": task.get('acknowledged'),
                    "delivery_info": task.get('delivery_info')
                }
                all_tasks.append(task_info)
        
        logger.info("Active tasks retrieved", count=len(all_tasks))
        return all_tasks
        
    except Exception as e:
        logger.error("Error getting active tasks", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/scheduled")
async def get_scheduled_tasks() -> List[Dict[str, Any]]:
    """Ottieni lista task schedulati (reserved)"""
    try:
        inspect = celery_app.control.inspect()
        reserved_tasks = inspect.reserved()
        
        if not reserved_tasks:
            return []
        
        all_tasks = []
        for worker_name, tasks in reserved_tasks.items():
            for task in tasks:
                task_info = {
                    "task_id": task.get('id'),
                    "name": task.get('name'),
                    "worker": worker_name,
                    "args": task.get('args'),
                    "kwargs": task.get('kwargs'),
                    "eta": task.get('eta'),
                    "priority": task.get('priority'),
                    "delivery_info": task.get('delivery_info')
                }
                all_tasks.append(task_info)
        
        logger.info("Scheduled tasks retrieved", count=len(all_tasks))
        return all_tasks
        
    except Exception as e:
        logger.error("Error getting scheduled tasks", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/history")
async def get_task_history(
    limit: int = Query(50, description="Numero massimo di task da ritornare"),
    task_name: Optional[str] = Query(None, description="Filtra per nome task")
) -> List[Dict[str, Any]]:
    """Ottieni storico task completati"""
    try:
        # TODO: Implementare storage storico task (Redis/DB)
        # Per ora ritorniamo mock data
        
        mock_history = [
            {
                "task_id": "collect-realtime-data-001",
                "name": "app.services.data_collector.collect_realtime_data",
                "status": "SUCCESS",
                "result": {
                    "devices_processed": 2,
                    "total_data_points": 15,
                    "errors": 0
                },
                "started_at": (datetime.utcnow() - timedelta(minutes=2)).isoformat(),
                "completed_at": (datetime.utcnow() - timedelta(minutes=2, seconds=30)).isoformat(),
                "duration_seconds": 30,
                "worker": "celery@worker-1"
            },
            {
                "task_id": "collect-alarm-data-001", 
                "name": "app.services.data_collector.collect_alarm_data",
                "status": "SUCCESS",
                "result": {
                    "devices_processed": 2,
                    "alarms_found": 0,
                    "errors": 0
                },
                "started_at": (datetime.utcnow() - timedelta(minutes=1)).isoformat(),
                "completed_at": (datetime.utcnow() - timedelta(minutes=1, seconds=15)).isoformat(),
                "duration_seconds": 15,
                "worker": "celery@worker-1"
            },
            {
                "task_id": "health-check-001",
                "name": "app.services.data_collector.health_check_task", 
                "status": "SUCCESS",
                "result": {
                    "healthy": True,
                    "services": {
                        "zcs_api": {"status": "healthy"},
                        "cache": {"healthy": True, "hit_rate": 85.2}
                    }
                },
                "started_at": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                "completed_at": (datetime.utcnow() - timedelta(minutes=5, seconds=10)).isoformat(),
                "duration_seconds": 10,
                "worker": "celery@worker-1"
            }
        ]
        
        # Filtra per task name se specificato
        if task_name:
            mock_history = [task for task in mock_history if task_name in task["name"]]
        
        # Limita risultati
        limited_history = mock_history[:limit]
        
        logger.info("Task history retrieved", count=len(limited_history), filtered_by=task_name)
        return limited_history
        
    except Exception as e:
        logger.error("Error getting task history", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{task_id}")
async def get_task_details(task_id: str) -> Dict[str, Any]:
    """Ottieni dettagli specifici di un task"""
    try:
        result = celery_app.AsyncResult(task_id)
        
        task_details = {
            "task_id": task_id,
            "status": result.status,
            "result": result.result,
            "traceback": result.traceback,
            "date_done": result.date_done.isoformat() if result.date_done else None,
            "task_name": result.name,
            "args": getattr(result, 'args', None),
            "kwargs": getattr(result, 'kwargs', None)
        }
        
        # Informazioni aggiuntive se disponibili
        if hasattr(result, 'info') and result.info:
            task_details["info"] = result.info
        
        logger.info("Task details retrieved", task_id=task_id, status=result.status)
        return task_details
        
    except Exception as e:
        logger.error("Error getting task details", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/trigger/{task_name}")
async def trigger_task(
    task_name: str,
    args: Optional[List] = None,
    kwargs: Optional[Dict] = None,
    delay_seconds: Optional[int] = None
) -> Dict[str, Any]:
    """Trigger manuale di un task specifico"""
    try:
        # Mappa task names a task functions
        task_map = {
            "collect_realtime_data": "app.services.data_collector.collect_realtime_data",
            "collect_alarm_data": "app.services.data_collector.collect_alarm_data",
            "health_check": "app.services.data_collector.health_check_task"
        }
        
        full_task_name = task_map.get(task_name)
        if not full_task_name:
            available_tasks = list(task_map.keys())
            raise HTTPException(
                status_code=400, 
                detail=f"Task '{task_name}' not found. Available tasks: {available_tasks}"
            )
        
        # Prepara parametri
        task_args = args or []
        task_kwargs = kwargs or {}
        
        # Trigger task
        if delay_seconds:
            # Task con delay
            result = celery_app.send_task(
                full_task_name,
                args=task_args,
                kwargs=task_kwargs,
                countdown=delay_seconds
            )
            trigger_type = "delayed"
        else:
            # Task immediato
            result = celery_app.send_task(
                full_task_name,
                args=task_args,
                kwargs=task_kwargs
            )
            trigger_type = "immediate"
        
        logger.info("Task triggered manually", 
                   task_name=task_name, 
                   task_id=result.id,
                   trigger_type=trigger_type)
        
        return {
            "message": f"Task '{task_name}' triggered successfully",
            "task_id": result.id,
            "task_name": full_task_name,
            "trigger_type": trigger_type,
            "delay_seconds": delay_seconds,
            "args": task_args,
            "kwargs": task_kwargs,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error triggering task", task_name=task_name, error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/{task_id}")
async def revoke_task(task_id: str, terminate: bool = Query(False)) -> Dict[str, Any]:
    """Revoca/cancella un task in esecuzione"""
    try:
        celery_app.control.revoke(task_id, terminate=terminate)
        
        logger.info("Task revoked", task_id=task_id, terminate=terminate)
        return {
            "message": f"Task {task_id} revoked successfully",
            "task_id": task_id,
            "terminated": terminate,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error revoking task", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/workers/stats")
async def get_worker_statistics() -> Dict[str, Any]:
    """Ottieni statistiche dettagliate dei worker Celery"""
    try:
        inspect = celery_app.control.inspect()
        
        # Statistiche base
        stats = inspect.stats()
        if not stats:
            return {"workers": {}, "summary": {"total_workers": 0}}
        
        # Processi attivi
        active = inspect.active()
        reserved = inspect.reserved()
        
        # Registri workers
        registered = inspect.registered()
        
        worker_details = {}
        for worker_name, worker_stats in stats.items():
            worker_details[worker_name] = {
                "stats": worker_stats,
                "active_tasks": len(active.get(worker_name, [])),
                "reserved_tasks": len(reserved.get(worker_name, [])),
                "registered_tasks": len(registered.get(worker_name, [])),
                "processes": worker_stats.get('pool', {}).get('processes', 0),
                "max_concurrency": worker_stats.get('pool', {}).get('max-concurrency', 0)
            }
        
        summary = {
            "total_workers": len(stats),
            "total_active_tasks": sum(len(tasks) for tasks in active.values()),
            "total_reserved_tasks": sum(len(tasks) for tasks in reserved.values()),
            "total_processes": sum(w.get('processes', 0) for w in worker_details.values())
        }
        
        logger.info("Worker statistics retrieved", workers=len(stats))
        return {
            "workers": worker_details,
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting worker statistics", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 