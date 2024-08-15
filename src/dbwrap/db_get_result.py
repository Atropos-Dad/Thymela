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



sql_dict = {
    "PRIDE": """SELECT "processed_Studies"."studyId", response, source,title, "projectDescription", "sampleProcessingProtocol", "dataProcessingProtocol",keywords, organisms, "organismParts", diseases, "projectTags", instruments
                        FROM "processed_Studies"
                        INNER JOIN "PRIDE_Studies"
                        ON "processed_Studies"."studyId" = "PRIDE_Studies"."studyId" """,
    "MBW": 'SELECT * FROM public."MBW_Studies"',
    "Metabolights": 'SELECT * FROM public."Metabolights_Studies"'
}
# get all results with original content
async def get_all_results_original(limit=None):
    async with DatabasePool.acquire() as conn:
        async with conn.transaction():
            results = []
            for source in ["PRIDE"]:
                try:
                    sql = sql_dict[source]
                    if limit:
                        sql += f' LIMIT {limit}'
                    source_results = await conn.fetch(sql)
                    results.extend(source_results)
                except Exception as e:
                    logging.error(f"Error fetching results for source {source}: {e}")
            return results
