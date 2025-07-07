import time
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Try to import psutil, but make it optional
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.warning("psutil not available. Memory metrics will be disabled.")

class ScraperAnalytics:
    def __init__(self, scraper_name: str):
        self.scraper_name = scraper_name
        self.start_time = None
        self.end_time = None
        self.total_items_identified = 0
        self.successfully_extracted = 0
        self.failed_extractions = 0
        self.errors: List[Dict] = []
        self.requests_count = 0
        self.initial_memory = None
        self.analytics_dir = "analytics"
        
        # Create analytics directory if it doesn't exist
        if not os.path.exists(self.analytics_dir):
            os.makedirs(self.analytics_dir)

    def start_scraping(self):
        """Start tracking scraping metrics"""
        self.start_time = time.time()
        if PSUTIL_AVAILABLE:
            self.initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

    def end_scraping(self):
        """End tracking and save analytics"""
        self.end_time = time.time()
        self._save_analytics()

    def increment_identified(self, count: int = 1):
        """Increment the count of identified items"""
        self.total_items_identified += count

    def increment_success(self, count: int = 1):
        """Increment the count of successfully extracted items"""
        self.successfully_extracted += count

    def increment_failure(self, count: int = 1):
        """Increment the count of failed extractions"""
        self.failed_extractions += count

    def add_error(self, error_type: str, error_message: str, item_id: Optional[str] = None):
        """Add an error to the tracking"""
        self.errors.append({
            "type": error_type,
            "message": error_message,
            "item_id": item_id,
            "timestamp": datetime.now().isoformat()
        })

    def increment_requests(self, count: int = 1):
        """Increment the count of requests made"""
        self.requests_count += count

    def _calculate_metrics(self) -> Dict:
        """Calculate all metrics for the scraping session"""
        duration = self.end_time - self.start_time if self.end_time else 0
        
        metrics = {
            "scraper_name": self.scraper_name,
            "timestamp": {
                "start": datetime.fromtimestamp(self.start_time).isoformat() if self.start_time else None,
                "end": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
                "duration_seconds": round(duration, 2)
            },
            "data_metrics": {
                "total_items_identified": self.total_items_identified,
                "successfully_extracted": self.successfully_extracted,
                "failed_extractions": self.failed_extractions,
                "success_rate": round((self.successfully_extracted / self.total_items_identified * 100), 2) if self.total_items_identified > 0 else 0
            },
            "performance_metrics": {
                "average_time_per_item": round(duration / self.successfully_extracted, 2) if self.successfully_extracted > 0 else 0,
                "requests_count": self.requests_count
            },
            "errors": self.errors
        }

        # Add memory metrics only if psutil is available
        if PSUTIL_AVAILABLE and self.initial_memory is not None:
            final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            memory_used = final_memory - self.initial_memory
            metrics["performance_metrics"]["memory_used_mb"] = round(memory_used, 2)

        return metrics

    def _save_analytics(self):
        """Save analytics to a JSON file"""
        metrics = self._calculate_metrics()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.analytics_dir}/{self.scraper_name}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)
            logging.info(f"Analytics saved to {filename}")
        except Exception as e:
            logging.error(f"Failed to save analytics: {str(e)}")

    def get_current_metrics(self) -> Dict:
        """Get current metrics without ending the scraping session"""
        return self._calculate_metrics()


def print_success_summary(scraper_name: str, item_count: int, storage_paths: Dict[str, str]) -> None:
    """Print a uniform success summary for a scraper."""
    print(f"\n✅ [{scraper_name}] scraping concluído com sucesso!")
    print(f"📊 Total de itens coletados: {item_count}")
    print("📁 Arquivos salvos em: database/")
    json_path = storage_paths.get("json")
    csv_path = storage_paths.get("csv")
    if json_path:
        print(f"   - JSON: {os.path.basename(json_path)}")
    if csv_path:
        print(f"   - CSV: {os.path.basename(csv_path)}")
