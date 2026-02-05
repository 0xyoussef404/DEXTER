"""
Main scan orchestration tasks
"""
from celery import chain, group
from app.tasks.celery_app import celery_app
from app.core.logging import logger


@celery_app.task(bind=True, name="app.tasks.scan_tasks.execute_full_scan")
def execute_full_scan(self, scan_id: int, config: dict):
    """
    Execute a complete security scan (recon + vuln)
    """
    logger.info(f"Starting full scan {scan_id}")
    
    try:
        # Update scan status to running
        self.update_state(state="RUNNING", meta={"phase": "Starting", "progress": 0})
        
        # Execute reconnaissance phase
        logger.info(f"Scan {scan_id}: Starting reconnaissance phase")
        from app.tasks.recon_tasks import execute_recon_scan
        recon_result = execute_recon_scan.apply_async(args=[scan_id, config])
        recon_data = recon_result.get()
        
        self.update_state(state="RUNNING", meta={"phase": "Reconnaissance Complete", "progress": 50})
        
        # Execute vulnerability scanning phase
        logger.info(f"Scan {scan_id}: Starting vulnerability scanning phase")
        from app.tasks.vuln_tasks import execute_vuln_scan
        vuln_result = execute_vuln_scan.apply_async(args=[scan_id, config, recon_data])
        vuln_data = vuln_result.get()
        
        self.update_state(state="RUNNING", meta={"phase": "Finalizing", "progress": 95})
        
        # Finalize scan
        logger.info(f"Scan {scan_id}: Completed successfully")
        
        return {
            "status": "completed",
            "recon": recon_data,
            "vuln": vuln_data
        }
        
    except Exception as e:
        logger.error(f"Scan {scan_id} failed: {e}", exc_info=True)
        raise


@celery_app.task(bind=True, name="app.tasks.scan_tasks.execute_recon_only_scan")
def execute_recon_only_scan(self, scan_id: int, config: dict):
    """
    Execute reconnaissance-only scan
    """
    logger.info(f"Starting recon-only scan {scan_id}")
    
    try:
        from app.tasks.recon_tasks import execute_recon_scan
        result = execute_recon_scan.apply_async(args=[scan_id, config])
        return result.get()
    except Exception as e:
        logger.error(f"Recon scan {scan_id} failed: {e}", exc_info=True)
        raise


@celery_app.task(bind=True, name="app.tasks.scan_tasks.execute_vuln_only_scan")
def execute_vuln_only_scan(self, scan_id: int, config: dict):
    """
    Execute vulnerability-only scan
    """
    logger.info(f"Starting vuln-only scan {scan_id}")
    
    try:
        from app.tasks.vuln_tasks import execute_vuln_scan
        result = execute_vuln_scan.apply_async(args=[scan_id, config, None])
        return result.get()
    except Exception as e:
        logger.error(f"Vuln scan {scan_id} failed: {e}", exc_info=True)
        raise
