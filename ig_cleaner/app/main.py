import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.db import Session, Schedule, Account
from app.workers import process_account
from app.config import WORKERS_COUNT
from app.logging_config import get_logger, setup_logging

# Setup logging at the application's entry point
setup_logging()
log = get_logger(__name__)

async def worker_wrapper(semaphore, account_id):
    """A wrapper to manage the semaphore for each worker task."""
    async with semaphore:
        await process_account(account_id)

async def run_job(account_ids):
    """
    Runs the worker process for a list of account IDs in parallel,
    limited by a semaphore.
    """
    semaphore = asyncio.Semaphore(WORKERS_COUNT)
    tasks = [worker_wrapper(semaphore, acc_id) for acc_id in account_ids]
    await asyncio.gather(*tasks)

def schedule_jobs(scheduler):
    """
    Reads schedules from the database and adds them to the scheduler.
    """
    db_session = Session()
    schedules = db_session.query(Schedule).filter_by(enabled=True).all()

    for job in schedules:
        log.info("Scheduling job.", job_id=job.id, cron_expr=job.cron_expr)

        account_ids_to_run = []
        if job.target_account_ids == 'all':
            accounts = db_session.query(Account).filter_by(enabled=True, status='active').all()
            account_ids_to_run = [acc.id for acc in accounts]
        else:
            try:
                account_ids_to_run = [int(i) for i in job.target_account_ids.split(',')]
            except ValueError:
                log.error("Invalid target_account_ids for schedule. Skipping.", schedule_id=job.id)
                continue

        scheduler.add_job(
            run_job,
            trigger=CronTrigger.from_crontab(job.cron_expr),
            args=[account_ids_to_run],
            id=str(job.id),
            replace_existing=True
        )

    db_session.close()

def main():
    """
    Main entry point for the scheduler.
    """
    scheduler = AsyncIOScheduler()
    schedule_jobs(scheduler)

    if scheduler.get_jobs():
        scheduler.start()
        log.info("Scheduler started. Press Ctrl+C to exit.")
        try:
            asyncio.get_event_loop().run_forever()
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            log.info("Scheduler shut down.")
    else:
        log.info("No jobs scheduled. Exiting.")

if __name__ == "__main__":
    main()
