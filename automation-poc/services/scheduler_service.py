"""APScheduler wrapper — schedule and reschedule the daily collection job."""
import logging
from typing import Callable, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)
JOB_ID = "data_collection"


class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def start(self):
        self.scheduler.start()
        logger.info("Scheduler started")

    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    def reschedule(self, hour: int, minute: int, callback: Callable, enabled: bool) -> None:
        if self.scheduler.get_job(JOB_ID):
            self.scheduler.remove_job(JOB_ID)
        if not enabled:
            logger.info("Automation disabled — no job scheduled")
            return
        self.scheduler.add_job(
            callback,
            CronTrigger(hour=hour, minute=minute),
            id=JOB_ID,
            replace_existing=True,
        )
        logger.info("Data collection scheduled daily at %02d:%02d", hour, minute)

    def get_next_run(self) -> Optional[str]:
        job = self.scheduler.get_job(JOB_ID)
        if job and job.next_run_time:
            return job.next_run_time.strftime("%Y-%m-%d %H:%M:%S %Z")
        return None

    @property
    def is_running(self) -> bool:
        return self.scheduler.running

    def job_exists(self) -> bool:
        return self.scheduler.get_job(JOB_ID) is not None
