"""Database Connection Library

This library makes a connection to the database and re-establishes it in the
event of a fork or a new thread. Multiple connections may be maintained using
the same library by specifying a client id.

Example:

    # connect using your current login name to a database of the same name
    conn = ciptools.database.conn(host="venus.lab.cip.uw.edu")

    # connect using your current login name to the election2020 database on mars
    conn = ciptools.database.conn(
        host="mars.lab.cip.uw.edu",
        database="election2020",
    )

    # create a new connection to the same database -- with the "client_id"
    # argument this would just reuse the connection created above.
    conn = ciptools.database.conn(
        host="mars.lab.cip.uw.edu",
        database="election2020",
        client_id="my-different-client-id"
    )

    # connect with a specific username and password
    conn = ciptools.database.conn(
        host="mars.lab.cip.uw.edu",
        database="coronavirus",
        user="username",
        password="password",
        client_id="my-different-client-id"
    )

"""

import logging
import os
import threading
import traceback
from collections import defaultdict

import psycopg2
import psycopg2.extras

# export the class that connects to the database. this may cause a circular
# import problem since that class relies on this module but only if we call
# this code when doing the import so we're ok.
from ciptools.database.client import DatabaseClient

# export the database client class
__all__ = ["DatabaseClient"]

# keep track of all of the database connections. this is a dict of dicts. the
# key to the first dict is the combo of process and thread id. the key to the
# second dict is the combo of the dsn and the client id.
connections = defaultdict(dict)

# want logging on database connections
logger = logging.getLogger(__name__)


def conn(
        host: str = None,
        database: str = None,
        user: str = None,
        password: str = None,
        sslmode: str = "require",
        client_id: str = "default",
):
    # add standard options to the list of options
    options = {
        "host": host,
        "database": database,
        "user": user,
        "password": password,
        "sslmode": sslmode,
        "cursor_factory": psycopg2.extras.DictCursor,
    }

    # get identifier for the connection and the key for the connection
    connection_id = get_connection_id()
    dsn = (host, database, user, password, sslmode, client_id)

    # if this dsn doesn't exist then mark it as "down"
    if dsn not in connections[connection_id]:
        connections[connection_id][dsn] = None

    # try to get the connection out of our connection dict
    connection = connections[connection_id][dsn]

    try:
        if connection is not None:
            # if we have a connection handle already then try to verify that it
            # still works. if it doesn't then go try to connect again below.
            try:
                with connection.cursor() as cur:
                    cur.execute("SELECT 1")
                logger.debug("reusing connection for {}".format(dsn))
                return connection
            except psycopg2.Error:
                # it is ok if this fails as we will just create a new connection
                pass

        # actually connect to the database. if we can't connect to the database
        # then this line will blow up.
        logger.debug("creating new connection for {}".format(dsn))
        connection = psycopg2.connect(**options)

        # make this behave like everything else for now
        connection.autocommit = True

        # add this new connection to our list of connections
        connections[connection_id][dsn] = connection

        return connection
    except Exception:
        logger.error(traceback.format_exc())

        # try to rollback connection but ok if it fails
        try:
            connection.rollback()
        except (AttributeError, psycopg2.Error):
            pass

        # try to disconnect but ok if it fails
        try:
            connection.close()
        except (AttributeError, psycopg2.Error):
            pass

        # remove references to it which destroys the object
        del connections[connection_id][dsn]

        # re-raise the exception that got us here
        raise


def get_connection_id():
    # yes, thread ids "may be recycled when a thread exits and another thread
    # is created" but since this value is never getting communicated to other
    # threads then it is ok to use it here to identify ourselves.
    return "{}-{}".format(os.getpid(), threading.current_thread().ident)
