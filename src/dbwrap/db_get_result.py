from dbwrap.conn_pool import DatabasePool
import logging; logger = logging.getLogger(__name__)

async def get_result(study_id):
    async with DatabasePool.acquire() as conn:
        async with conn.transaction():
            try:
                sql = 'SELECT * FROM public."processed_Studies" WHERE "studyId" = $1'
                result = await conn.fetchval(sql, study_id)
                return result
                
            except Exception as e:
                # Handle the error appropriately
                logging.error(f"Error retrieving data for study ID {study_id}: {e}")
                pass



# get all results
async def get_all_results(limit=None):
    async with DatabasePool.acquire() as conn:
        async with conn.transaction():
            try:
                sql = 'SELECT * FROM public."processed_Studies"'
                if limit:
                    sql += f' LIMIT {limit}'
                
                results = await conn.fetch(sql)
                return results
                
            except Exception as e:
                # Handle the error appropriately
                logging.error(f"Error retrieving data: {e}")
                pass

# get all results with original content
async def get_all_results_original(limit=None):
    async with DatabasePool.acquire() as conn:
        async with conn.transaction():
            results = []
            for source in ["PRIDE", "MBW", "Metabolights"]:
                try:
                    sql = f"""
                    SELECT *
                    FROM "processed_Studies"
                    INNER JOIN "{source}_Studies"
                    ON "processed_Studies"."studyId" = "{source}_Studies"."studyId"
                    """
                    if limit:
                        sql += f' LIMIT {limit}'
                    source_results = await conn.fetch(sql)
                    results.extend(source_results)
                except Exception as e:
                    logging.error(f"Error fetching results for source {source}: {e}")
            return results
