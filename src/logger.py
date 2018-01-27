import logging

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(filename)-18s %(funcName)-25s [%(process)-5s:%(thread)-15s] %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger("CenterLogger")
log.addHandler(handler)
log.setLevel(logging.DEBUG)
log.info("Log created")
