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
        query = "SELECT * FROM {t}".format(t=table)
        if predicates:
            predicatefmt = "{col} = %({val})s"
            where = " WHERE "+" AND ".join(predicatefmt.format(col=k, val=k) for k in predicates)
        self.cursor.execute(query+where, predicates)
        results = self.cursor.fetchall()
        return results

    def updateonematching(self, table, **columns):
        query = "UPDATE {t} SET".format(t=table)
        columnfmt = "{col} = %({val})s"
        where = "WHERE id = %(id)s"
        cols = ", ".join(columnfmt.format(col=k, val=k) for k in columns)
        query = " ".join([query, cols, where])
        self.cursor.execute(query, columns)
        self.commit()

    def deletematching(self, table, **predicates):
        where = ""
        query = "DELETE FROM {t}".format(t=table)
        if predicates:
            predicatefmt = "{col} = %({val})s"
            where = " WHERE "+" AND ".join(predicatefmt.format(col=k, val=k) for k in predicates)
        self.cursor.execute(query+where, predicates)
        self.commit()

    def insert(self, table, **data):
        insert = "INSERT INTO {t}".format(t=table)
        columns = "({c})".format(c=", ".join(data))
        values = "VALUES ({v})".format(v=", ".join("%({col})s".format(col=c) for c in data))
        self.cursor.execute(" ".join((insert, columns, values)), data)
        self.commit()

    def commit(self):
        self.conn.commit()
