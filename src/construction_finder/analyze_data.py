import pandas as pd
import spacy
import workspace
from construction_finder_logger import logger


def process_data(input_file, output_file, input_sep=",", input_encoding="latin-1"):

    data = pd.read_csv(input_file, sep=input_sep, encoding=input_encoding)
    data["Context"] = data["Context"].str.replace("Õ", "’")
    data["Context"] = data["Context"].str.replace("Ó", "")
    data["Context"] = data["Context"].str.replace("Ò", " ")

    return data


if __name__ == "__main__":
    data_file = "/Users/julia/Dropbox/Computing for Data Analysis/Dative_Genitive_Construction/datives-finalized2.csv"
    data = process_data(data_file, "")

    # TODO: create pandas dataframe for output
    # output =

    nlp = spacy.load("en_core_web_lg")
    logger.info("Loaded spacy NLP")

    for text in data["Context"][-2:]:
        work_space = workspace.WorkSpace.from_nlp_and_txt(nlp, text)
        active_frames = work_space.run()
        logger.info(f"Active frames:\n {str(work_space.active_frames)}")
