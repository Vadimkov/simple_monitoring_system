import sqlite3
import re
import os
from logger import log


MONITORING_DB_NAME = "center_monitoring.db"
FILES_TABLE_NAME = 'lastVersionFiles'
AGENT_TABLE_NAME = 'activeAgents'


def create_monitoring_db():
    log.info("Create DB")

    conn = sqlite3.connect(MONITORING_DB_NAME)

    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = c.fetchall()
    log.info("Detected tables: %s" % (str(tables)))

    try:
        if (FILES_TABLE_NAME,) not in tables:
            log.info("Create table")
            c.execute("CREATE TABLE %s "
                      "(agentname text, dirname text, "
                      "filename text, content text)"
                      % (FILES_TABLE_NAME))
    except Exception as e:
        print("Failed for %s (create table): %s: %s "
              % (FILES_TABLE_NAME, type(e).__name__, e))

    try:
        if (AGENT_TABLE_NAME,) not in tables:
            log.info("Create table")
            c.execute("CREATE TABLE %s "
                      "(agenthost text, agentport int)"
                      % (AGENT_TABLE_NAME))
    except Exception as e:
        print("Failed for %s (create table): %s: %s "
              % (FILES_TABLE_NAME, type(e).__name__, e))

    conn.close()


def update_file(agentname, dirname, filename, content):
    log.debug("Update file %s for %s from dir %s:\n%s"
              % (filename, agentname, dirname, content))
    table = FILES_TABLE_NAME

    try:
        conn = sqlite3.connect(MONITORING_DB_NAME)
        c = conn.cursor()

        c.execute("SELECT * FROM %s "
                  "WHERE dirname = '%s' "
                  "AND filename = '%s' "
                  "AND agentname = '%s' "
                  % (table, dirname, filename, agentname))

        if not c.fetchall():
            c.execute("INSERT INTO %s VALUES ('%s', '%s', '%s', '%s')"
                      % (table, agentname, dirname, filename, content))
        else:
            c.execute("UPDATE %s SET content = '%s' "
                      "WHERE dirname = '%s' "
                      "AND filename = '%s' "
                      "AND agentname = '%s' "
                      % (table, content, dirname, filename, agentname))

        conn.commit()
    except Exception as e:
        print("Failed for %s (update_file): %s: %s "
              % (table, type(e).__name__, e))
    finally:
        conn.close()


def get_full():
    log.debug("Get full")
    table = FILES_TABLE_NAME
    response = None

    try:
        conn = sqlite3.connect(MONITORING_DB_NAME)
        c = conn.cursor()

        c.execute("SELECT agentname, dirname, filename, content FROM %s"
                  % (table))
        response = c.fetchall()
        conn.close()

    except Exception as e:
        print("Failed action get_full: %s: %s " % (type(e).__name__, e))
    finally:
        conn.close()

    return response


def get_records_by_type(record_type):
    return get_full()


def get_matched_records(record_type, expression):
    report = []

    records_by_type = get_records_by_type(record_type)
    pattern = re.compile(expression)
    for record in records_by_type:
        if pattern.findall(record[3]):
            report.append(record)

    return report


def add_active_agent(agent_host, agent_port):
    log.debug("Try to add agent %s:%s to active_agents_list"
              % (agent_host, agent_port))
    table = AGENT_TABLE_NAME

    try:
        conn = sqlite3.connect(MONITORING_DB_NAME)
        c = conn.cursor()

        if not is_agent_exist(agent_host, agent_port):
            c.execute("INSERT INTO %s VALUES ('%s', '%r')"
                      % (table, agent_host, agent_port))
        else:
            return False

        conn.commit()
    except Exception as e:
        print("Failed add agent %s:%s to DB: %s: %s "
              % (agent_host, agent_port, table, type(e).__name__, e))
    finally:
        conn.close()

    return True


def is_agent_exist(agent_host, agent_port):
    agents = get_all_agents()
    return (agent_host, agent_port) in agents


def get_all_agents():
    log.debug("Get all agents")
    table = AGENT_TABLE_NAME
    response = None

    try:
        conn = sqlite3.connect(MONITORING_DB_NAME)
        c = conn.cursor()

        c.execute("SELECT agenthost, agentport FROM %s" % (table))
        response = c.fetchall()
        conn.close()

    except Exception as e:
        print("Failed action get_all_agents: %s: %s " % (type(e).__name__, e))
    finally:
        conn.close()

    return response


def remove_active_agent(agent_host, agent_port):
    log.debug("Delete agent %s:%s" % (agent_host, agent_port))
    table = AGENT_TABLE_NAME

    try:
        conn = sqlite3.connect(MONITORING_DB_NAME)
        c = conn.cursor()

        c.execute("DELETE FROM %s WHERE agenthost='%s' AND agentport='%s'"
                  % (table, agent_host, agent_port))
        conn.commit()
        conn.close()

    except Exception as e:
        print("Failed remove_active_agent: %s: %s " % (type(e).__name__, e))
    finally:
        conn.close()


def create_empty_monitoring_db():
    """Remove db and just create new one. Use it for tests only!"""

    if os.path.isfile(MONITORING_DB_NAME):
        os.remove(MONITORING_DB_NAME)
    create_monitoring_db()
