import psycopg2

class DB(object):

    def __init__(self):
        db = u = 'openlogistix'
        with open('conf/pw') as pwfile:
            pw = pwfile.read().rstrip()
        self.conn = psycopg2.connect(dbname=db, user=u, password=pw)
        self.cursor = self.conn.cursor()

    def getonematching(self, table, **predicates):
        query = "SELECT * FROM {t} WHERE ".format(t=table)
        predicatefmt = "{col} = %({val})s"
        where = " AND ".join(predicatefmt.format(col=k, val=k) for k in predicates)
        self.cursor.execute(query+where+" LIMIT 1", predicates)
        results = self.cursor.fetchone()
        return results

    def getallmatching(self, table, **predicates):
        where = ""
        query = "SELECT * FROM {t} WHERE ".format(t=table)
        if predicates:
            predicatefmt = "{col} = %({val})s"
            where = " AND ".join(predicatefmt.format(col=k, val=k) for k in predicates)
        self.cursor.execute(query+where, predicates)
        results = self.cursor.fetchall()
        return results

    def commit(self):
        self.conn.commit()
