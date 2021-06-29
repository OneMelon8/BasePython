import time

from src.utils.sql_util import ChainedStatement, SQLError
from src.data.settings import SCHEDULER_LOOP_INTERVAL, SCHEDULER_DATABASE_INTERVAL

# Database ping variables
ping_count = 0


def tick():
    """ Should be called every 10 seconds """
    global ping_count

    # To ping or not to ping
    if ping_count * SCHEDULER_LOOP_INTERVAL < SCHEDULER_DATABASE_INTERVAL:
        ping_count += 1
        return

    now = time.time()
    # Query database & retrieve data
    with ChainedStatement() as statement:
        # Query all messages within the time interval of [now, now + interval]
        result = statement.query(f"SELECT * FROM scheduled_messages WHERE timestamp > {now} AND timestamp < {now + SCHEDULER_DATABASE_INTERVAL}")
        # Delete all messages before now
        statement.delete(table="scheduled_messages", where=f"timestamp < {now}")

    for row in result:
        _, channel, message, timestamp = row
        # TODO: add message to broadcast

    # Reset ping count
    ping_count = 0
