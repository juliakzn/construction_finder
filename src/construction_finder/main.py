from construction_finder import config, workspace
from construction_finder.construction_finder_logger import logger

if __name__ == "__main__":
    logger.info("Loaded spacy NLP")
    to_sample_text = "And they gave some of the most wonderful gifts to everyone"

    work_space = workspace.WorkSpace.from_nlp_and_txt(config.nlp, to_sample_text)
    active_frames = work_space.run()
    logger.info(f"Active frames:\n {str(work_space.active_frames)}")

    # dative_sample_text = "Don’t give me that."
    # work_space = workspace.WorkSpace.from_nlp_and_txt(nlp, dative_sample_text)
    # active_frames = work_space.run()
    # logger.info(f"Active frames:\n {str(work_space.active_frames)}")

    # Next test sentences: You can fool some of the people all of the time, and all of the people some of the time, but you can not fool all of the people all of the time.
    # With all of the injuries and COVID-19 issues, the Ravens are just a shorthanded squad fighting above its weight class.
    # The height of the Michigan players averages six feet five, and nearly everyone of them weighs over two hundred pounds.
