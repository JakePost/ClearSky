# setup.py

import sys
from config_helper import logger
import asyncio
import database_handler
import test


async def create_db():
    try:
        async with database_handler.connection_pool.acquire() as connection:
            async with connection.transaction():
                create_users_table = """
                CREATE TABLE IF NOT EXISTS users (
                    did text primary key,
                    handle text,
                    status bool
                )
                """

                create_blocklists_table = """
                CREATE TABLE IF NOT EXISTS blocklists (
                    user_did text,
                    blocked_did text,
                    block_date text
                )
                """

                create_top_blocks_table = """
                CREATE TABLE IF NOT EXISTS top_block (
                    did text,
                    count int,
                    list_type text
                )
                """

                create_top_24_blocks_table = """
                CREATE TABLE IF NOT EXISTS top_twentyfour_hour_block (
                    did text,
                    count int,
                    list_type text
                )
                """

                await connection.execute(create_users_table)
                await connection.execute(create_blocklists_table)
                await connection.execute(create_top_blocks_table)
                await connection.execute(create_top_24_blocks_table)
    except Exception as e:
        logger.error(f"Error creating db: {e}")


# ======================================================================================================================
# =============================================== Main Logic ===========================================================
async def main():
    await database_handler.create_connection_pool()

    if database_handler.local_db():
        logger.info("Creating local db and tables.")
        await create_db()
        user_data_list = await test.generate_random_user_data()
        await test.generate_random_block_data(user_data_list)
        sys.exit()
    else:
        logger.info("creating db tables.")
        await create_db()
        sys.exit()


if __name__ == '__main__':
    asyncio.run(main())