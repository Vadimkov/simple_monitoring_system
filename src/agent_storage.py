import sqlite3
import os
from logger import log


MONITORING_DB_NAME = "agent_monitoring.db"
LAST_VERSION_OBJECTS_NAME = 'last_version_objects'
DIFF_OBJECTS_NAME = 'diff_objects'
LAST_REQUESTED_OBJECTS_NAME = 'last_requested_objects'


def create_monitoring_db():
    log.info("Create DB")

    conn = sqlite3.connect(MONITORING_DB_NAME)

    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = c.fetchall()

    if (LAST_VERSION_OBJECTS_NAME,) not in tables:
        log.debug("CREATE TABLE %s (space_name text, object_name text, content text)"
                  % (LAST_VERSION_OBJECTS_NAME))
        c.execute("CREATE TABLE %s (space_name text, object_name text, content text)"
                  % (LAST_VERSION_OBJECTS_NAME))

    if (DIFF_OBJECTS_NAME,) not in tables:
        log.debug("CREATE TABLE %s (space_name text, object_name text, content text)"
                  % (DIFF_OBJECTS_NAME))
        c.execute("CREATE TABLE %s (space_name text, object_name text, content text)"
                  % (DIFF_OBJECTS_NAME))

    if (LAST_REQUESTED_OBJECTS_NAME,) not in tables:
        log.debug("CREATE TABLE %s (space_name text, object_name text, content text)"
                  % (LAST_REQUESTED_OBJECTS_NAME))
        c.execute("CREATE TABLE %s (space_name text, object_name text, content text)"
                  % (LAST_REQUESTED_OBJECTS_NAME))

    conn.close()


def update_object(table, space_name, object_name, content):
    log.debug("Update %s of object %s from space %s:\n%s"
              % (table, object_name, space_name, content))

    try:
        conn = sqlite3.connect(MONITORING_DB_NAME)
        c = conn.cursor()

        c.execute("SELECT * FROM %s WHERE space_name = '%s' AND object_name = '%s'"
                  % (table, space_name, object_name))
        if not c.fetchall():
            c.execute("INSERT INTO %s VALUES ('%s', '%s', '%s')"
                      % (table, space_name, object_name, content))
        else:
            c.execute("UPDATE %s SET content = '%s' "
                      "WHERE space_name = '%s' AND object_name = '%s'"
                      % (table, content, space_name, object_name))

        conn.commit()
    except Exception as e:
        print("Failed for %s (update_object): %s: %s "
              % (table, type(e).__name__, e))
    finally:
        conn.close()


def get_object(table, space_name, object_name):
    log.debug("Get %s of object %s from space %s" % (table, object_name, space_name))

    response = None

    try:
        conn = sqlite3.connect(MONITORING_DB_NAME)
        c = conn.cursor()

        c.execute("SELECT content FROM %s "
                  "WHERE space_name = '%s' AND object_name = '%s'"
                  % (table, space_name, object_name))
        response = c.fetchall()
        conn.close()

    except Exception as e:
        print("Failed for %s (get_object): %s: %s "
              % (table, type(e).__name__, e))
    finally:
        conn.close()

    return response


def get_full(table):
    log.debug("Get full %s" % (table))

    try:
        conn = sqlite3.connect(MONITORING_DB_NAME)
        c = conn.cursor()

        c.execute("SELECT space_name, object_name, content FROM %s" % (table))
        response = c.fetchall()
        conn.close()

    except Exception as e:
        print("Failed for %s (get_object): %s: %s "
              % (table, type(e).__name__, e))
    finally:
        conn.close()

    return response


# ### LAST ###


def update_last_version_object(space_name, object_name, content):
    update_object(LAST_VERSION_OBJECTS_NAME, space_name, object_name, content)


def get_last_version_object(space_name, object_name):
    return get_object(LAST_VERSION_OBJECTS_NAME, space_name, object_name)


def get_full_last_version():
    return get_full(LAST_VERSION_OBJECTS_NAME)


# ### DIFF ###


def update_diff_object(space_name, object_name, content):
    update_object(DIFF_OBJECTS_NAME, space_name, object_name, content)


def get_diff_object(space_name, object_name):
    return get_object(DIFF_OBJECTS_NAME, space_name, object_name)


def get_full_diff():
    return get_full(DIFF_OBJECTS_NAME)


# ### LAST REQUESTED ###


def update_last_requested_object(space_name, object_name, content):
    update_object(LAST_REQUESTED_OBJECTS_NAME, space_name, object_name, content)


def get_last_requested_object(space_name, object_name):
    return get_object(LAST_REQUESTED_OBJECTS_NAME, space_name, object_name)


def get_full_last_requested():
    return get_full(LAST_REQUESTED_OBJECTS_NAME)


def update_last_requested_from_last_version():
    log.debug("Update last requested from last version")

    try:
        conn = sqlite3.connect(MONITORING_DB_NAME)
        c = conn.cursor()

        c.execute("DELETE FROM %s" % (LAST_REQUESTED_OBJECTS_NAME))
        c.execute("INSERT INTO %s SELECT * FROM %s"
                  % (LAST_REQUESTED_OBJECTS_NAME, LAST_VERSION_OBJECTS_NAME))
        c.execute("DELETE FROM %s" % (DIFF_OBJECTS_NAME))

        conn.commit()
    except Exception as e:
        print("Failed for update_last_requested: %s: %s "
              % (type(e).__name__, e))
    finally:
        conn.close()


def create_empty_monitoring_db():
    """Remove db and just create new one. Use it for tests only!"""

    if os.path.isfile(MONITORING_DB_NAME):
        os.remove(MONITORING_DB_NAME)
    create_monitoring_db()
