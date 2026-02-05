"""
Reconnaissance orchestration tasks
"""
from celery import group
from app.tasks.celery_app import celery_app
from app.core.logging import logger


@celery_app.task(bind=True, name="app.tasks.recon_tasks.execute_recon_scan")
def execute_recon_scan(self, scan_id: int, config: dict):
    """
    Execute complete reconnaissance scan
    Orchestrates all recon modules based on configuration
    """
    logger.info(f"Starting reconnaissance scan {scan_id}")
    
    try:
        recon_config = config.get("recon", {})
        results = {}
        
        # Phase 1: Subdomain Enumeration
        if recon_config.get("subdomain_enumeration", True):
            logger.info(f"Scan {scan_id}: Subdomain enumeration")
            self.update_state(state="RUNNING", meta={"phase": "Subdomain Enumeration", "progress": 5})
            results["subdomains"] = subdomain_enumeration_task.apply_async(args=[scan_id, recon_config]).get()
        
        # Phase 2: DNS Analysis
        if recon_config.get("dns_analysis", True):
            logger.info(f"Scan {scan_id}: DNS analysis")
            self.update_state(state="RUNNING", meta={"phase": "DNS Analysis", "progress": 15})
            results["dns"] = dns_analysis_task.apply_async(args=[scan_id, results.get("subdomains", [])]).get()
        
        # Phase 3: Port Scanning
        if recon_config.get("port_scanning", True):
            logger.info(f"Scan {scan_id}: Port scanning")
            self.update_state(state="RUNNING", meta={"phase": "Port Scanning", "progress": 25})
            results["ports"] = port_scanning_task.apply_async(args=[scan_id, recon_config]).get()
        
        # Phase 4: Technology Detection
        if recon_config.get("tech_detection", True):
            logger.info(f"Scan {scan_id}: Technology detection")
            self.update_state(state="RUNNING", meta={"phase": "Technology Detection", "progress": 35})
            results["technologies"] = tech_detection_task.apply_async(args=[scan_id]).get()
        
        # Phase 5: Web Crawling
        if recon_config.get("web_crawling", True):
            logger.info(f"Scan {scan_id}: Web crawling")
            self.update_state(state="RUNNING", meta={"phase": "Web Crawling", "progress": 40})
            results["crawl"] = web_crawling_task.apply_async(args=[scan_id, recon_config]).get()
        
        # Phase 6: JavaScript Analysis
        if recon_config.get("javascript_analysis", True):
            logger.info(f"Scan {scan_id}: JavaScript analysis")
            self.update_state(state="RUNNING", meta={"phase": "JavaScript Analysis", "progress": 50})
            results["javascript"] = javascript_analysis_task.apply_async(args=[scan_id, results.get("crawl", {})]).get()
        
        # Phase 7: Content Discovery
        if recon_config.get("content_discovery", True):
            logger.info(f"Scan {scan_id}: Content discovery")
            self.update_state(state="RUNNING", meta={"phase": "Content Discovery", "progress": 60})
            results["content"] = content_discovery_task.apply_async(args=[scan_id, recon_config]).get()
        
        # Phase 8: API Discovery
        if recon_config.get("api_discovery", True):
            logger.info(f"Scan {scan_id}: API discovery")
            self.update_state(state="RUNNING", meta={"phase": "API Discovery", "progress": 70})
            results["apis"] = api_discovery_task.apply_async(args=[scan_id, results.get("crawl", {})]).get()
        
        # Phase 9: Parameter Discovery
        if recon_config.get("parameter_discovery", True):
            logger.info(f"Scan {scan_id}: Parameter discovery")
            self.update_state(state="RUNNING", meta={"phase": "Parameter Discovery", "progress": 80})
            results["parameters"] = parameter_discovery_task.apply_async(args=[scan_id, results.get("crawl", {})]).get()
        
        logger.info(f"Reconnaissance scan {scan_id} completed")
        return results
        
    except Exception as e:
        logger.error(f"Reconnaissance scan {scan_id} failed: {e}", exc_info=True)
        raise


@celery_app.task(name="app.tasks.recon_tasks.subdomain_enumeration_task")
def subdomain_enumeration_task(scan_id: int, config: dict):
    """
    Subdomain enumeration task
    """
    from app.services.recon.subdomain_enum import SubdomainEnumerator
    
    try:
        enumerator = SubdomainEnumerator(scan_id, config)
        subdomains = enumerator.enumerate()
        logger.info(f"Scan {scan_id}: Found {len(subdomains)} subdomains")
        return subdomains
    except Exception as e:
        logger.error(f"Subdomain enumeration failed for scan {scan_id}: {e}", exc_info=True)
        return []


@celery_app.task(name="app.tasks.recon_tasks.dns_analysis_task")
def dns_analysis_task(scan_id: int, subdomains: list):
    """
    DNS analysis task
    """
    from app.services.recon.dns_analyzer import DNSAnalyzer
    
    try:
        analyzer = DNSAnalyzer(scan_id)
        results = analyzer.analyze(subdomains)
        logger.info(f"Scan {scan_id}: DNS analysis completed")
        return results
    except Exception as e:
        logger.error(f"DNS analysis failed for scan {scan_id}: {e}", exc_info=True)
        return {}


@celery_app.task(name="app.tasks.recon_tasks.port_scanning_task")
def port_scanning_task(scan_id: int, config: dict):
    """
    Port scanning task
    """
    from app.services.recon.port_scanner import PortScanner
    
    try:
        scanner = PortScanner(scan_id, config)
        results = scanner.scan()
        logger.info(f"Scan {scan_id}: Port scanning completed")
        return results
    except Exception as e:
        logger.error(f"Port scanning failed for scan {scan_id}: {e}", exc_info=True)
        return {}


@celery_app.task(name="app.tasks.recon_tasks.tech_detection_task")
def tech_detection_task(scan_id: int):
    """
    Technology detection task
    """
    from app.services.recon.tech_detector import TechDetector
    
    try:
        detector = TechDetector(scan_id)
        results = detector.detect()
        logger.info(f"Scan {scan_id}: Technology detection completed")
        return results
    except Exception as e:
        logger.error(f"Technology detection failed for scan {scan_id}: {e}", exc_info=True)
        return {}


@celery_app.task(name="app.tasks.recon_tasks.web_crawling_task")
def web_crawling_task(scan_id: int, config: dict):
    """
    Web crawling task
    """
    from app.services.recon.web_crawler import WebCrawler
    
    try:
        crawler = WebCrawler(scan_id, config)
        results = crawler.crawl()
        logger.info(f"Scan {scan_id}: Web crawling completed")
        return results
    except Exception as e:
        logger.error(f"Web crawling failed for scan {scan_id}: {e}", exc_info=True)
        return {}


@celery_app.task(name="app.tasks.recon_tasks.javascript_analysis_task")
def javascript_analysis_task(scan_id: int, crawl_data: dict):
    """
    JavaScript analysis task
    """
    from app.services.recon.js_analyzer import JSAnalyzer
    
    try:
        analyzer = JSAnalyzer(scan_id)
        results = analyzer.analyze(crawl_data)
        logger.info(f"Scan {scan_id}: JavaScript analysis completed")
        return results
    except Exception as e:
        logger.error(f"JavaScript analysis failed for scan {scan_id}: {e}", exc_info=True)
        return {}


@celery_app.task(name="app.tasks.recon_tasks.content_discovery_task")
def content_discovery_task(scan_id: int, config: dict):
    """
    Content discovery task
    """
    from app.services.recon.content_discovery import ContentDiscovery
    
    try:
        discovery = ContentDiscovery(scan_id, config)
        results = discovery.discover()
        logger.info(f"Scan {scan_id}: Content discovery completed")
        return results
    except Exception as e:
        logger.error(f"Content discovery failed for scan {scan_id}: {e}", exc_info=True)
        return {}


@celery_app.task(name="app.tasks.recon_tasks.api_discovery_task")
def api_discovery_task(scan_id: int, crawl_data: dict):
    """
    API discovery task
    """
    from app.services.recon.api_discovery import APIDiscovery
    
    try:
        discovery = APIDiscovery(scan_id)
        results = discovery.discover(crawl_data)
        logger.info(f"Scan {scan_id}: API discovery completed")
        return results
    except Exception as e:
        logger.error(f"API discovery failed for scan {scan_id}: {e}", exc_info=True)
        return {}


@celery_app.task(name="app.tasks.recon_tasks.parameter_discovery_task")
def parameter_discovery_task(scan_id: int, crawl_data: dict):
    """
    Parameter discovery task
    """
    from app.services.recon.param_discovery import ParamDiscovery
    
    try:
        discovery = ParamDiscovery(scan_id)
        results = discovery.discover(crawl_data)
        logger.info(f"Scan {scan_id}: Parameter discovery completed")
        return results
    except Exception as e:
        logger.error(f"Parameter discovery failed for scan {scan_id}: {e}", exc_info=True)
        return {}
