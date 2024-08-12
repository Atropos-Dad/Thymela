import asyncio
import aiohttp
from time import time
import hashlib
from dataclasses import dataclass
import logging
from concurrent.futures import ThreadPoolExecutor
from parsing.article_asseser import assess_article
from dbwrap.db_get_study import get_study
from dbwrap.db_add_result import add_result
from dbwrap.db_get_study import get_studies_to_be_analysed

logger = logging.getLogger(__name__)

# Concurrency settings
MAX_CONCURRENT_TASKS = 256
QUEUE_SIZE = MAX_CONCURRENT_TASKS*3

@dataclass
class TaskStats:
    success_count: int = 0
    failure_count: int = 0

class SharedState:
    def __init__(self):
        self.task_stats = [TaskStats() for _ in range(MAX_CONCURRENT_TASKS)]
        self.total_success = 0
        self.total_failure = 0
        self.start_time = None
        self.total_articles = 0

    def start_timer(self):
        self.start_time = time()

    @property
    def elapsed_time(self):
        if self.start_time is None:
            return 0
        return time() - self.start_time

    @property
    def articles_per_second(self):
        if self.start_time is None or self.elapsed_time == 0:
            return 0
        return (self.total_success + self.total_failure) / self.elapsed_time

shared_state = SharedState()

def hash_string(s: str) -> int:
    return int(hashlib.md5(s.encode()).hexdigest(), 16)

# This will be our thread pool for running synchronous functions
thread_pool = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_TASKS)

async def analyze_article(article_id: str):
    try:
        # Run get_study and assess_article in the thread pool
        loop = asyncio.get_running_loop()
        study_content = await loop.run_in_executor(thread_pool, get_study, article_id)
        result = await loop.run_in_executor(thread_pool, assess_article, study_content)
        
        # Add result to database (this is an async function
        await add_result(article_id, result)

        task_index = hash_string(article_id) % MAX_CONCURRENT_TASKS
        shared_state.task_stats[task_index].success_count += 1
        shared_state.total_success += 1
        logger.info(f"Successfully analyzed article {article_id}")
        return True
    except Exception as e:
        logger.error(f"Error analyzing article {article_id}: {e}")
        task_index = hash_string(article_id) % MAX_CONCURRENT_TASKS
        shared_state.task_stats[task_index].failure_count += 1
        shared_state.total_failure += 1
        return False

async def process_queue(queue):
    while True:
        article_id = await queue.get()
        await analyze_article(article_id)
        queue.task_done()

async def init_article_analysis():
    logger.info("Getting articles to analyse...")
    # Run get_studies_to_be_analysed in the thread pool
    loop = asyncio.get_running_loop()
    studies = await loop.run_in_executor(thread_pool, get_studies_to_be_analysed, "PRIDE", 1000)
    shared_state.total_articles = len(studies)

    queue = asyncio.Queue(maxsize=QUEUE_SIZE)
    tasks = []
    for _ in range(MAX_CONCURRENT_TASKS):
        task = asyncio.create_task(process_queue(queue))
        tasks.append(task)

    shared_state.start_timer()
    logger.info(f"Analyzing {len(studies)} articles...")
    for study in studies:
        await queue.put(study[1])  # Assuming study[1] is the article_id

    await queue.join()

    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)

    logger.info("Analysis complete.")

async def start_analysis():
    await init_article_analysis()

if __name__ == "__main__":
    asyncio.run(start_analysis())
