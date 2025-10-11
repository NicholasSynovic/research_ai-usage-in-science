import json
import pickle
import re
from json.decoder import JSONDecodeError
from os import listdir
from pathlib import Path

from pandas import DataFrame, Series
from progress.bar import Bar
from requests import Response

MAGIC_PATH: Path = Path("../data/pickles/pickle_full_parts_0").resolve()


def load_zip(fp: Path) -> DataFrame:
    data: dict[str, list] = {"model": [], "obj": []}

    pickle_paths: list[Path] = sorted([Path(fp, name) for name in listdir(fp)])
    with Bar("Loading pickles...", max=len(pickle_paths)) as bar:
        pp: Path
        for pp in pickle_paths:
            model_name: str = pp.stem.split(sep="_")[0]
            obj = pickle.load(file=pp.open(mode="rb"))

            data["model"].append(model_name)
            data["obj"].append(obj)

            bar.next()

    return DataFrame(data=data)


def get_total_papers_analyzed(model: str, df: DataFrame) -> int:
    model_df: DataFrame = df[df["model"] == model]

    paper_count: int = 0
    row: Series
    for _, row in model_df.iterrows():
        paper_count += row["obj"].shape[0]

    return paper_count


def decode_json(json_string: str) -> dict:
    cleaned: str = json_string.replace(" ", "").replace("\n", "")
    result_str: str = cleaned[1:15].replace(",", "")
    prose_str: str = cleaned[22:30].replace("}", "").replace('"', "").replace(":", "")

    if prose_str == "":
        prose_str = "null"

    prose_dict: dict = json.loads(s='{"prose": "' + prose_str + '"}')
    result_dict: dict = json.loads("{" + result_str + "}")
    json_data = prose_dict | result_dict
    if json_data["prose"] == "null":
        json_data["prose"] = None

    return json_data


def count_papers_using_dl(model: str, df: DataFrame) -> tuple[int, int]:
    use_dl: int = 0
    no_dl: int = 0

    model_df: DataFrame = df[df["model"] == model]

    paper_count: int = 0
    row: Series
    for _, row in model_df.iterrows():
        _df: DataFrame = row["obj"]

        for _, subrow in _df.iterrows():
            resp: Response = subrow["response_obj"]
            llm_response = resp.json()["response"]

            json_data: dict = {}
            try:
                json_data = json.loads(s=llm_response)
            except JSONDecodeError:
                # json_data = decode_json(json_string=llm_response)

                # print(llm_response)
                # input()

                # {
                #     "prose": bool,
                #     "result": string
                # }

                continue

            # print(json_data)

            try:
                if json_data["result"] == True and json_data["prose"] != None:
                    use_dl += 1
                else:
                    no_dl += 1
            except KeyError:
                no_dl += 1

    return (use_dl, no_dl)


def main() -> None:
    # Read in objects from the pickle files
    objs: DataFrame = load_zip(fp=MAGIC_PATH)

    # Print the number of papers analyzed
    print("gpt-oss:", get_total_papers_analyzed(model="gpt-oss", df=objs))
    print("magistral:", get_total_papers_analyzed(model="magistral", df=objs))
    print("phi3:", get_total_papers_analyzed(model="phi3", df=objs))

    # Count the number of papers that use dl by if they return true and have prose
    # print(count_papers_using_dl(model="magistral", df=objs))
    # print(count_papers_using_dl(model="gpt-oss", df=objs))
    print(count_papers_using_dl(model="phi3", df=objs))


if __name__ == "__main__":
    main()
