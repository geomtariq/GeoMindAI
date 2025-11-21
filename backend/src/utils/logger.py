import logging

# TODO: Configure a proper logging setup that sends logs to Loki.
# This will likely involve using a library like 'py-loki-handler'.

def get_logger(name: str):
    return logging.getLogger(name)
