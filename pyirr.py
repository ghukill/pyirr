"""
pyirr

Resources
    - http://www.nltk.org/api/nltk.metrics.html
    - https://learnaitech.com/how-to-compute-inter-rater-reliablity-metrics-cohens-kappa-fleisss-kappa-cronbach-alpha-kripndorff-alpha-scotts-pi-inter-class-correlation-in-python/
"""

import argparse
import uuid

from nltk import agreement
import numpy as np
import pandas as pd


def main(input_filepath, sheet_name, rater_cols, skiprows):

    """


    :param input_filepath:
    :return:
    """

    # read excel document into pandas dataframe
    df = pd.read_excel(input_filepath, sheet_name=sheet_name, skiprows=int(skiprows))
    print(df)

    # drop row where Code=='Totals'
    df = df[df.Code != "Totals"]

    # extract raters
    rater_scores = {}
    for col in rater_cols:
        r = df[col]
        r = r[~np.isnan(r)]
        rater_scores[f"{col}|{str(uuid.uuid4())}"] = r

    # integrity check
    print("integrity check for scores:")
    int_test = {k:len(v) for k,v in rater_scores.items()}
    print(int_test)

    # structure data
    nltk_structured_scores = []
    for k, v in rater_scores.items():
        nltk_structured_scores.extend([(k, i, s) for i, s in enumerate(v)])
    print(nltk_structured_scores)

    # run NLTK agreement
    agreements = agreement.AnnotationTask(data=nltk_structured_scores)

    # set to dataframe
    scores = {
        "Scotts_Pi": {"score": agreements.pi()},
        "Krippendorff": {"score": agreements.alpha()},
        "Cohen": {"score": agreements.kappa()},
        "Davies_and_Fleiss": {"score": agreements.multi_kappa()},
    }
    output_df = pd.DataFrame.from_dict(scores, orient="index")

    # print
    print(output_df.to_markdown())


if __name__ == "__main__":

    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ("yes", "true", "t", "y", "1"):
            return True
        elif v.lower() in ("no", "false", "f", "n", "0"):
            return False
        else:
            raise argparse.ArgumentTypeError("Boolean value expected.")

    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="input.xlsx")
    parser.add_argument("--sheet_name", default="my_data")
    parser.add_argument("--cols", nargs="+", default=["R1", "R2"])
    parser.add_argument("--skiprows", default=2)

    args = parser.parse_args()

    main(args.input, args.sheet_name, args.cols, args.skiprows)
