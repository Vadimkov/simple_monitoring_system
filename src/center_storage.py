import sqlite3
from logger import log


MONITORING_DB_NAME = "center_monitoring.db"
FILES_TABLE_NAME = 'lastVersionFiles'


def create_monitoring_db():
    log.info("Create DB")

    conn = sqlite3.connect(MONITORING_DB_NAME)
    
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = c.fetchall()

    if (FILES_TABLE_NAME,) not in tables:
        c.execute("CREATE TABLE %s (agentname text, dirname text, filename text, content text)" % (FILES_TABLE_NAME))

    conn.close()


def update_file(agentname, dirname, filename, content):
    log.debug("Update file %s for %s from dir %s:\n%s" % (filename, agentname, dirname, content))
    table = FILES_TABLE_NAME

    try:
        conn = sqlite3.connect(MONITORING_DB_NAME)
        c = conn.cursor()
        
        c.execute("SELECT * FROM %s WHERE dirname = '%s' AND filename = '%s' AND agentname = '%s'" % (table, dirname, filename, agentname))
        if not c.fetchall():
            c.execute("INSERT INTO %s VALUES ('%s', '%s', '%s', '%s')" % (table, agentname, dirname, filename, content))
        else:
            c.execute("UPDATE %s SET content = '%s' WHERE dirname = '%s' AND filename = '%s' AND agentname = '%s'" % (table, content, dirname, filename, agentname))
            
        conn.commit()
    except Exception as e:
        print("Failed for %s (update_file): %s: %s " % (table, type(e).__name__, e))
    finally:
        conn.close()


def get_full():
    log.debug("Get full")
    table = FILES_TABLE_NAME

    try:
        conn = sqlite3.connect(MONITORING_DB_NAME)
        c = conn.cursor()
        
        c.execute("SELECT agentname, dirname, filename, content FROM %s" % (table))
        response = c.fetchall()
        conn.close()

    except Exception as e:
        print("Failed action get_full: %s: %s " % (type(e).__name__, e))
    finally:
        conn.close()

    return response


