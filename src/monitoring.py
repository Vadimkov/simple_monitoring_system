import logging
from multiprocessing import Process
from logger import log
from monitoring_lib import run_monitoring
from monitoring_agent import run_agent


def main():
    p = Process(target=run_agent)
    p.start()

    dirnames = ("monitoring", "monitoring1", "monitoring2")
    monitoringProc = Process(target=run_monitoring, args=(dirnames,))
    monitoringProc.start()


if __name__ == "__main__":
    log.setLevel(logging.INFO)
    main()
