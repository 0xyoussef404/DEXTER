"""
Vulnerability scanning tasks
"""
from app.tasks.celery_app import celery_app
from app.core.logging import logger


@celery_app.task(bind=True, name="app.tasks.vuln_tasks.execute_vuln_scan")
def execute_vuln_scan(self, scan_id: int, config: dict, recon_data: dict = None):
    """
    Execute vulnerability scanning
    """
    logger.info(f"Starting vulnerability scan {scan_id}")
    
    try:
        vuln_config = config.get("vuln", {})
        results = {}
        
        # XSS Detection
        if vuln_config.get("xss_detection", True):
            logger.info(f"Scan {scan_id}: XSS detection")
            self.update_state(state="RUNNING", meta={"phase": "XSS Detection", "progress": 55})
            from app.services.vuln.xss_detector import XSSDetector
            detector = XSSDetector(scan_id, vuln_config)
            results["xss"] = detector.detect(recon_data)
        
        # SQL Injection Detection
        if vuln_config.get("sqli_detection", True):
            logger.info(f"Scan {scan_id}: SQLi detection")
            self.update_state(state="RUNNING", meta={"phase": "SQL Injection Detection", "progress": 65})
            from app.services.vuln.sqli_detector import SQLiDetector
            detector = SQLiDetector(scan_id, vuln_config)
            results["sqli"] = detector.detect(recon_data)
        
        # SSRF Detection
        if vuln_config.get("ssrf_detection", True):
            logger.info(f"Scan {scan_id}: SSRF detection")
            self.update_state(state="RUNNING", meta={"phase": "SSRF Detection", "progress": 75})
            from app.services.vuln.ssrf_detector import SSRFDetector
            detector = SSRFDetector(scan_id, vuln_config)
            results["ssrf"] = detector.detect(recon_data)
        
        # Advanced Fuzzing
        if vuln_config.get("fuzzing_enabled", True):
            logger.info(f"Scan {scan_id}: Advanced fuzzing")
            self.update_state(state="RUNNING", meta={"phase": "Advanced Fuzzing", "progress": 85})
            from app.services.vuln.fuzzer import AdvancedFuzzer
            fuzzer = AdvancedFuzzer(scan_id, vuln_config)
            results["fuzzing"] = fuzzer.fuzz(recon_data)
        
        logger.info(f"Vulnerability scan {scan_id} completed")
        return results
        
    except Exception as e:
        logger.error(f"Vulnerability scan {scan_id} failed: {e}", exc_info=True)
        raise
