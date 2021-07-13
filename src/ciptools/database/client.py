"""Database Client Library

Example:

    from ciptools.database import DatabaseClient

    db = DatabaseClient(
        host="mars.lab.cip.uw.edu",
        database="election2020",
    )

    # get a working database handle. this is not guaranteed to return the same
    # handle with each invocation so only use this if you don't care about
    # transactions.
    conn = db.conn()

    # this will always return the same database handle and will croak if the
    # handle is unable to be used anymore. this is handy for transactions. all
    # the same arguments that can be passed to .conn() can be passed to this.
    conn = db.persistent_conn()

    # run a transaction, change client id to "foobar" to make a new or
    # secondary database connection while still using the same options.
    db = DatabaseClient(host="venus.lab.cip.uw.edu", client_id="foobar")
    with db.transaction() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT txid_current()")
            print(cur.fetchone())

            cur.execute("SELECT txid_current()")
            print(cur.fetchone())


It is worth noting that psycopg2 loads the entire result set into memory. If
that is not desirable then one can name the cursor and it will be loaded into
memory one row at a time. See this resource for more information:
* http://initd.org/psycopg/docs/usage.html#server-side-cursors

    cur = conn.cursor(name="something_unique")
    cur.execute("SELECT foo FROM bar")
    for row in cur:
        print "found {}".format(row["foo"])
    cur.close()


For more examples of how to use databases in Python, this is a great resource:
* http://www.slideshare.net/petereisentraut/programming-with-python-and-postgresql

"""
import contextlib
import logging
from threading import Event

import psycopg2
import tenacity

import ciptools.database

logger = logging.getLogger(__name__)


class DatabaseClient:
    def __init__(
            self,
            host: str = None,
            database: str = None,
            user: str = None,
            password: str = None,
            sslmode: str = "prefer",
            client_id: str = "default",
            retry: bool = True,
    ):
        """Creates a database client object.

        This should be called like this, passing the connection arguments:

            db = DatabaseClient(
                host="foo.lab.cip.uw.edu",
                database="foo",
                user="myuser",
            )

        Finally, after the connection, a *client_id* argument may be passed to
        give the connection a name for situations where you might be making
        multiple connections to the same database. For example:

            db = DatabaseClient(
                host="foo.lab.cip.uw.edu",
                user="foo",
                database="bar",
                client_id="bar",
            )

        Aside from *client_id* and *retry*, all arguments are passed directly
        to the underlying connection library.
        """

        self.dsn = {
            "host": host,
            "database": database,
            "user": user,
            "password": password,
            "sslmode": sslmode,
            "client_id": client_id,
        }

        # this will store a persistent connection so we can ensure that we are
        # giving the user the same connection every time
        self.persistent = None

        # if the user told us not to retry then prevent retrying
        self.retry = retry

    def conn(self, retry=None):
        """Get a database connection.

        If it does not matter to you whether you get the same handle with each
        invocation you can use this method. If no current database connection
        exists or the database went away then this method will try to connect
        to the database.
        """

        # if set then we will not retry connections
        retry_flag = Event()

        # control retries. give the user a second chance to stop retries.
        if (retry is None and self.retry) or retry:
            retry_flag.clear()
        else:
            retry_flag.set()

        # make a copy so that we don't modify the original data structure
        dsn = self.dsn.copy()

        counter = 0
        for attempt in tenacity.Retrying(
                reraise=True,
                stop=tenacity.stop_when_event_set(retry_flag),
                wait=tenacity.wait_fixed(0.1) + tenacity.wait_random(0, 0.9),
        ):
            with attempt:
                counter = counter + 1
                try:
                    return ciptools.database.conn(**dsn)
                except Exception as e:
                    logger.error("failed to connect to database on attempt {}: {}".format(counter, e))
                    raise

    def persistent_conn(self):
        """Get a persistent database connection.

        If it matters whether the same handle is used for each database request
        then this method can be used. If no current database connection exists
        then this method will try to connect to the database using normal
        methods. But if there had been a connection and it went away then this
        method will throw an exception.
        """
        if self.persistent is not None:
            # we have a handle, make sure it is live. if it is not live then
            # clean it and die.
            try:
                with self.persistent.cursor() as cur:
                    cur.execute("SELECT 1")
            except Exception:
                self.persistent = None
                raise
        else:
            # we don't have a handle already so create one. this handle will be
            # returned every time persistent_conn is called.
            self.persistent = self.conn()

        return self.persistent

    @contextlib.contextmanager
    def transaction(self):
        """Get a connection in a transaction.

        This will return a connection that is in a transaction. You should use
        it as a context wrapper. When the context wrapper finishes then the
        transaction will commit. If anything in your context wrapper throws an
        exception then the transaction will be rolled back.
        """
        conn = None
        try:
            conn = self.conn()
            conn.autocommit = False
            yield conn
            conn.commit()
        except Exception:
            try:
                if conn is not None:
                    conn.rollback()
            except (AttributeError, psycopg2.Error) as e:
                logger.warning("could not rollback connection: {}".format(e))

            raise
        finally:
            try:
                if conn is not None:
                    conn.autocommit = True
            except (AttributeError, psycopg2.Error) as e:
                logger.warning("could not reset autocommit on connection: {}".format(e))
