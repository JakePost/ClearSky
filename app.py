# app.py

import asyncpg
from quart import Quart, render_template, request, session, jsonify
from datetime import datetime
import os
import sys
import uuid
import argparse
import re
import asyncio
import database_handler
import scheduler
import utils
import on_wire
import config_helper
from config_helper import logger
# ======================================================================================================================
# ============================= Pre-checks // Set up logging and debugging information =================================
config = config_helper.read_config()

title_name = "ClearSky"
os.system("title " + title_name)
version = "1.6.4"
current_dir = os.getcwd()
log_version = "ClearSky Version: " + version
runtime = datetime.now()
current_time = runtime.strftime("%m%d%Y::%H:%M:%S")
try:
    username = os.getlogin()
except OSError:
    username = "Cannot get username"
    pass
logger.info(log_version)
logger.debug("Ran from: " + current_dir)
logger.debug("Ran by: " + username)
logger.debug("Ran at: " + str(current_time))
logger.info("File Log level: " + str(config.get("handler_fileHandler", "level")))
logger.info("Stdout Log level: " + str(config.get("handler_consoleHandler", "level")))
app = Quart(__name__)

# Configure session secret key
app.secret_key = 'your-secret-key'
users_db_folder_path = config.get("database", "users_db_path")
users_db_filename = 'users_cache.db'
users_db_path = users_db_folder_path + users_db_filename

# Get the database configuration
database_config = utils.get_database_config()

# Now you can access the configuration values using dictionary keys
pg_user = database_config["user"]
pg_password = database_config["password"]
pg_host = database_config["host"]
pg_database = database_config["database"]

session_ip = None


# ======================================================================================================================
# ================================================== HTML Pages ========================================================
@app.route('/')
async def index():
    # Generate a new session number and store it in the session
    if 'session_number' not in session:
        session['session_number'] = generate_session_number()

    return await render_template('index.html')


@app.route('/loading')
async def loading():

    return await render_template('loading.html')


@app.route('/coming_soon')
async def coming_soon():
    return await render_template('coming_soon.html')


@app.route('/status')
async def always_200():

    return "OK", 200


@app.route('/contact')
async def contact():

    return await render_template('contact.html')


# Handles selection for form
@app.route('/selection_handle', methods=['POST'])
async def selection_handle():
    did_identifier = None
    handle_identifier = None
    global session_ip
    data = await request.form
    session_ip = await get_ip()
    logger.debug(data)

    selection = data.get('selection')
    identifier = data.get('identifier')
    identifier = identifier.lower()
    identifier = identifier.strip()
    identifier = identifier.replace('@', '')

    # Check if the flag to skip "Option 5" is present in the form data
    skip_option5 = data.get('skipOption5', '').lower()
    if skip_option5 == "true":
        skip_option5 = True
    elif skip_option5 == "false":
        skip_option5 = False

    if selection == "4":
        logger.info(str(session_ip) + " > " + str(*session.values()) + " | " + "Total User count requested")
        count = await utils.get_user_count()
        logger.info(str(session_ip) + " > " + str(*session.values()) + " | " + "Total User count: " + str(count))

        return jsonify({"count": count})
    if is_did(identifier) or is_handle(identifier):
        # Check if did or handle exists before processing
        if is_did(identifier):
            handle_identifier = await on_wire.resolve_did(identifier)
            did_identifier = "place_holder"
        if is_handle(identifier):
            did_identifier = await on_wire.resolve_handle(identifier)
            handle_identifier = "place_holder"
        if not handle_identifier or not did_identifier:
            return await render_template('no_longer_exists.html', content_type='text/html')
        if selection != "4":
            if not identifier:
                return await render_template('error.html')
            if selection == "1":
                logger.info(str(session_ip) + " > " + str(*session.values()) + ": " + "DID resolve request made for: " + identifier)
                result = did_identifier
                logger.info(str(session_ip) + " > " + str(*session.values()) + " | " + "Request Result: " + identifier + " | " + result)

                return jsonify({"result": result})
            elif selection == "2":
                logger.info(str(session_ip) + " > " + str(*session.values()) + " | " + "Handle resolve request made for: " + identifier)
                result = handle_identifier
                logger.info(str(session_ip) + " > " + str(*session.values()) + " | " + "Request Result: " + identifier + " | " + str(result))

                return jsonify({"result": result})
            elif selection == "3":
                logger.info(str(session_ip) + " > " + str(*session.values()) + " | " + "Block list requested for: " + identifier)
                blocklist, count = await get_user_block_list_html(identifier)

                if "did" in identifier:
                    identifier = handle_identifier

                return jsonify({"block_list": blocklist, "user": identifier, "count": count})
            elif selection == "5" and not skip_option5:
                logger.info(str(session_ip) + " > " + str(*session.values()) + " | " + "Single Block list requested for: " + identifier)
                blocks, dates, count = await utils.get_single_user_blocks(identifier)
                if "did" in identifier:
                    identifier = handle_identifier

                if type(blocks) != list:
                    blocks = ["None"]
                    dates = [datetime.now().date()]
                    count = 0
                response_data = {
                    "who_block_list": blocks,
                    "user": identifier,
                    "date": dates,
                    "counts": count
                }
                logger.info(str(session_ip) + " > " + str(*session.values()) + " | " + "Single Blocklist Request Result: " + identifier + " | " + "Blocked by: " + str(blocks) + " :: " + "Total count: " + str(count))

                return jsonify(response_data)
                # return jsonify({"user": identifier, "block_list": blocks, "count": count})
            elif skip_option5:
                return jsonify({"message": "Option 5 skipped"})
    else:
        return await render_template('error.html')


@app.route('/fun_facts')
async def fun_facts():
    resolved_blocked = utils.resolved_blocked
    resolved_blockers = utils.resolved_blockers

    # Check if both lists are empty
    if not resolved_blocked and not resolved_blockers:
        return await render_template('coming_soon.html')  # Render the "Coming Soon" page

    # If at least one list is not empty, render the regular page
    return await render_template('fun_facts.html', blocked_results=resolved_blocked, blockers_results=resolved_blockers)


async def get_user_block_list_html(ident):
    blocked_users, timestamps = await utils.get_user_block_list(ident)
    block_list = []

    if not blocked_users:
        total_blocked = 0
        handles = [f"{ident} hasn't blocked anyone."]
        timestamp = datetime.now().date()
        block_list.append({"handle": handles, "timestamp": timestamp})
        return block_list, total_blocked
    else:
        async with asyncpg.create_pool(
            user=pg_user,
            password=pg_password,
            host=pg_host,
            database=pg_database
        ) as new_connection_pool:
            async with new_connection_pool.acquire() as connection:
                records = await connection.fetch(
                    'SELECT handle FROM users WHERE did = ANY($1)',
                    blocked_users
                )

        handles = [record['handle'] for record in records]
        total_blocked = len(handles)

        logger.info(str(session_ip) + " > " + str(*session.values()) + " | " + "Blocklist Request Result: " + ident + " | " + "Total blocked: " + str(total_blocked) + " :: " + str(list(zip(handles, timestamps))))

        for handle, timestamp in zip(handles, timestamps):
            block_list.append({"handle": handle, "timestamp": timestamp})

        return block_list, total_blocked


# ======================================================================================================================
# ============================================= Main functions =========================================================
def generate_session_number():

    return str(uuid.uuid4().hex)


async def get_ip():  # Get IP address of session request
    if 'X-Forwarded-For' in request.headers:
        # Get the client's IP address from the X-Forwarded-For header
        ip = request.headers.get('X-Forwarded-For')
        # The client's IP address may contain multiple comma-separated values
        # Extract the first IP address from the list
        ip = ip.split(',')[0].strip()
    else:
        # Use the remote address if the X-Forwarded-For header is not available
        ip = request.remote_addr
    return ip


def is_did(identifier):
    did_pattern = r'^did:[a-z]+:[a-zA-Z0-9._:%-]*[a-zA-Z0-9._-]$'
    return re.match(did_pattern, identifier) is not None


def is_handle(identifier):
    handle_pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
    return re.match(handle_pattern, identifier) is not None


# ======================================================================================================================
# =============================================== Main Logic ===========================================================
ip_address = config.get("server", "ip")
port_address = config.get("server", "port")

# python app.py --update-users-did-handle-db // command to update users db with dids and handles
# python app.py --update-users-did-only-db // command to update users db with dids only
# python app.py --fetch-users-count // command to get current count in db
# python app.py --update-blocklists-db // command to update all users blocklists
# python app.py --truncate-blocklists_table-db // command to update all users blocklists
# python app.py --truncate-users_table-db // command to update all users blocklists
# python app.py --delete-database // command to delete entire database
# python app.py --retrieve-blocklists-db // initial/re-initialize get for blocklists database


async def main():
    parser = argparse.ArgumentParser(description='ClearSky Web Server: ' + version)
    parser.add_argument('--update-users-did-handle-db', action='store_true', help='Update the database with all users')
    parser.add_argument('--update-users-did-only-db', action='store_true', help='Update the database with all users')
    parser.add_argument('--fetch-users-count', action='store_true', help='Fetch the count of users')
    parser.add_argument('--update-blocklists-db', action='store_true', help='Update the blocklists table')
    parser.add_argument('--retrieve-blocklists-db', action='store_true', help='Initial/re-initialize get for blocklists database')
    parser.add_argument('--truncate-blocklists_table-db', action='store_true', help='delete blocklists table')
    parser.add_argument('--truncate-users_table-db', action='store_true', help='delete users table')
    parser.add_argument('--delete-database', action='store_true', help='delete entire database')
    args = parser.parse_args()

    await database_handler.create_connection_pool()  # Creates connection pool for db

    if args.update_users_did_handle_db:
        # Call the function to update the database with all users
        logger.info("Users db update requested.")
        all_dids = await database_handler.get_all_users_db(True, False)
        logger.info("Users db updated dids.")
        logger.info("Update users handles requested.")
        batch_size = 1000
        total_dids = len(all_dids)
        total_handles_updated = 0

        # Check if there is a last processed DID in the temporary table
        async with database_handler.connection_pool.acquire() as connection:
            async with connection.transaction():
                try:
                    query = "SELECT last_processed_did FROM temporary_table"
                    last_processed_did = await connection.fetchval(query)
                except Exception as e:
                    last_processed_did = None
                    logger.error(f"Exception getting from db: {str(e)}")

        if not last_processed_did:
            await database_handler.create_temporary_table()

        if last_processed_did:
            # Find the index of the last processed DID in the list
            start_index = next((i for i, (did,) in enumerate(all_dids) if did == last_processed_did), None)
            if start_index is None:
                logger.warning(
                    f"Last processed DID '{last_processed_did}' not found in the list. Starting from the beginning.")
            else:
                logger.info(f"Resuming processing from DID: {last_processed_did}")
                all_dids = all_dids[start_index:]

        async with database_handler.connection_pool.acquire() as connection:
            async with connection.transaction():
                # Concurrently process batches and update the handles
                for i in range(0, total_dids, batch_size):
                    logger.info("Getting batch to resolve.")
                    batch_dids = all_dids[i:i + batch_size]

                    # Process the batch asynchronously
                    batch_handles_updated = await database_handler.process_batch(batch_dids)
                    total_handles_updated += batch_handles_updated

                    # Log progress for the current batch
                    logger.info(f"Handles updated: {total_handles_updated}/{total_dids}")
                    logger.info(f"First few DIDs in the batch: {batch_dids[:5]}")

                logger.info("Users db update finished.")
                await database_handler.delete_temporary_table()
                sys.exit()
    elif args.update_users_did_only_db:
        # Call the function to update the database with all users dids
        logger.info("Users db update requested.")
        await database_handler.get_all_users_db(True, False, init_db_run=True)
        logger.info("Users db updated dids finished.")
        sys.exit()
    elif args.fetch_users_count:
        # Call the function to fetch the count of users
        count = await database_handler.count_users_table()
        logger.info(f"Total users in the database: {count}")
        sys.exit()
    elif args.retrieve_blocklists_db:
        logger.info("Get Blocklists db requested.")
        await database_handler.update_all_blocklists()
        await database_handler.delete_blocklist_temporary_table()
        logger.info("Blocklist db fetch finished.")
        sys.exit()
    elif args.update_blocklists_db:
        logger.info("Update Blocklists db requested.")
        database_handler.get_single_users_blocks_db(run_update=False, get_dids=True)
        logger.info("Update Blocklists db finished.")
        sys.exit()
    else:
        await database_handler.get_top_blocks()
        await utils.resolve_top_block_lists()
        # Start the scheduler
        scheduler.start_scheduler()
        logger.info("Web server starting at: " + ip_address + ":" + port_address)
        # await serve(app, host=ip_address, port=port_address)
        await app.run_task(host=ip_address, port=port_address)
if __name__ == '__main__':
    # asyncio.run(main())
    # app.run()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())