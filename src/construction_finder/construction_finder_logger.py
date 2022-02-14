import logging

# Create logger
logger = logging.getLogger(f"construction_finder")
logger.setLevel(logging.DEBUG)

# Create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d,%H:%M:%S"
)

# Add formatter to ch
ch.setFormatter(formatter)

# Add ch to logger
logger.addHandler(ch)


def log_bonding(logger, frame, slot_id, candidate, bonded_text):
    logger_frame_message = f"Frame {frame} slot {slot_id} bonded to "
    logger_bond_message = f"{[candidate]}"
    logger_message = f"{logger_frame_message}{logger_bond_message}: {bonded_text}"
    logger.info(logger_message)
