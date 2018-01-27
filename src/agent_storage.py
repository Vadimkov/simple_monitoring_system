import sqlite3
from logger import log


MONITORING_DB_NAME = "agent_monitoring.db"
LAST_VERSION_FILES_NAME = 'lastVersionFiles'
DIFF_FILES_NAME = 'diffFiles'
LAST_REQUESTED_FILES_NAME = 'lastRequestedFiles'


def create_monitoring_db():
    log.info("Create DB")

    conn = sqlite3.connect(MONITORING_DB_NAME)
    
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = c.fetchall()

    if (LAST_VERSION_FILES_NAME,) not in tables:
        c.execute("CREATE TABLE %s (dirname text, filename text, content text)" % (LAST_VERSION_FILES_NAME))

    if (DIFF_FILES_NAME,) not in tables:
        c.execute("CREATE TABLE %s (dirname text, filename text, content text)" % (DIFF_FILES_NAME))
    
    if (LAST_REQUESTED_FILES_NAME,) not in tables:
        c.execute("CREATE TABLE %s (dirname text, filename text, content text)" % (LAST_REQUESTED_FILES_NAME))

    conn.close()


def update_file(table, dirname, filename, content):
    log.debug("Update %s of file %s from dir %s:\n%s" % (table, filename, dirname, content))

    try:
        conn = sqlite3.connect(MONITORING_DB_NAME)
        c = conn.cursor()
        
        c.execute("SELECT * FROM %s WHERE dirname = '%s' AND filename = '%s'" % (table, dirname, filename))
        if not c.fetchall():
            c.execute("INSERT INTO %s VALUES ('%s', '%s', '%s')" % (table, dirname, filename, content))
        else:
            c.execute("UPDATE %s SET content = '%s' WHERE dirname = '%s' AND filename = '%s'" % (table, content, dirname, filename))
            
        conn.commit()
    except Exception as e:
        print("Failed for %s (update_file): %s: %s " % (table, type(e).__name__, e))
    finally:
        conn.close()


def get_file(table, dirname, filename):
    log.debug("Get %s of file %s from dir %s" % (table, filename, dirname))

    try:
        conn = sqlite3.connect(MONITORING_DB_NAME)
        c = conn.cursor()
        
        c.execute("SELECT content FROM %s WHERE dirname = '%s' AND filename = '%s'" % (table, dirname, filename))
        response = c.fetchall()
        conn.close()

    except Exception as e:
        print("Failed for %s (get_file): %s: %s " % (table, type(e).__name__, e))
    finally:
        conn.close()

    return response


def get_full(table):
    log.debug("Get full %s" % (table))

    try:
        conn = sqlite3.connect(MONITORING_DB_NAME)
        c = conn.cursor()
        
        c.execute("SELECT dirname, filename, content FROM %s" % (table))
        response = c.fetchall()
        conn.close()

    except Exception as e:
        print("Failed for %s (get_file): %s: %s " % (table, type(e).__name__, e))
    finally:
        conn.close()

    return response


### LAST ###


def update_last_version_file(dirname, filename, content):
    update_file(LAST_VERSION_FILES_NAME, dirname, filename, content)


def get_last_version_file(dirname, filename):
    return get_file(LAST_VERSION_FILES_NAME, dirname, filename)


def get_full_last_version():
    return get_full(LAST_VERSION_FILES_NAME)


### DIFF ###


def update_diff_file(dirname, filename, content):
    update_file(DIFF_FILES_NAME, dirname, filename, content)


def get_diff_file(dirname, filename):
    return get_file(DIFF_FILES_NAME, dirname, filename)

def get_full_diff():
    return get_full(DIFF_FILES_NAME)


### LAST REQUESTED ###


def update_last_requested_file(dirname, filename, content):
    update_file(LAST_REQUESTED_FILES_NAME, dirname, filename, content)


def get_last_requested_file(dirname, filename):
    return get_file(LAST_REQUESTED_FILES_NAME, dirname, filename)


def get_full_last_requested():
    return get_full(LAST_REQUESTED_FILES_NAME)


def update_last_requested_from_last_version():
    log.debug("Update last requested from last version")

    try:
        conn = sqlite3.connect(MONITORING_DB_NAME)
        c = conn.cursor()
        
        c.execute("DELETE FROM %s" % (LAST_REQUESTED_FILES_NAME))
        c.execute("INSERT INTO %s SELECT * FROM %s" % (LAST_REQUESTED_FILES_NAME, LAST_VERSION_FILES_NAME))
        c.execute("DELETE FROM %s" % (DIFF_FILES_NAME))
            
        conn.commit()
    except Exception as e:
        print("Failed for update_last_requested: %s: %s " % (type(e).__name__, e))
    finally:
        conn.close()
