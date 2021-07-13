from ciptools.database import DatabaseClient

db = DatabaseClient(host="venus.lab.cip.uw.edu")

with db.transaction() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT txid_current()")
        print(cur.fetchone())

        cur.execute("SELECT txid_current()")
        print(cur.fetchone())


with db.transaction() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT txid_current()")
        print(cur.fetchone())

        cur.execute("SELECT txid_current()")
        print(cur.fetchone())
