from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .config import settings
from ..services.aggregators.api_connectors import fetch_all_apis
from ..services.aggregators.rss_parser import fetch_all_rss
from ..services.scrapers.web_scraper import run_all_scrapers


logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def run_full_aggregation() -> dict:
    logger.info("[start] Starting full aggregation run")
    rss_results = await fetch_all_rss()
    api_results = await fetch_all_apis()
    scraper_results = await run_all_scrapers()
    logger.info("[done] Aggregation run complete")
    return {"rss": rss_results, "apis": api_results, "scrapers": scraper_results}


def start_scheduler() -> None:
    interval = settings.FEED_REFRESH_INTERVAL_MINUTES
    if scheduler.get_job("full_aggregation") is None:
        scheduler.add_job(
            run_full_aggregation,
            trigger=IntervalTrigger(minutes=interval),
            id="full_aggregation",
            replace_existing=True,
        )
    if not scheduler.running:
        scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
