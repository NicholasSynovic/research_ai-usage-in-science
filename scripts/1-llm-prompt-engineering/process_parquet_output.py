import json
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import List

import click
import pandas
from pandas import DataFrame
from pydantic import BaseModel, RootModel, ValidationError


class UsesDLModel(BaseModel):
    result: bool = False
    prose: str = ""


class UsesPTMs(BaseModel):
    result: bool = False
    prose: str = ""


class IdentifyPTMs(BaseModel):
    model: str = ""
    prose: str = ""


class IdentifyPTMsList(RootModel[List[IdentifyPTMs]]):
    pass


class IdentifyReuse(BaseModel):
    model: str = ""
    form: str = ""
    classification: str = ""
    prose: str = ""


class IdentifyReuseList(RootModel[List[IdentifyReuse]]):
    pass


def resolve_json(json_str: str, model_str: str) -> dict:
    model: type[BaseModel]
    match model_str:
        case "uses_dl":
            model = UsesDLModel
        case "uses_ptms":
            model = UsesPTMs
        case "identify_ptms":
            model = IdentifyPTMsList
            sub_model = IdentifyPTMs
        case "identify_reuse":
            model = IdentifyReuseList
            sub_model = IdentifyReuse

    if json_str.strip() == "":
        # Handle RootModel types (like IdentifyPTMsList) properly
        if issubclass(model, RootModel):
            sub_model_data = sub_model().model_dump()
            json_str = model(root=[sub_model_data]).model_dump_json()
        else:
            json_str = model().model_dump_json()

    json_str = json_str.replace("```json", "").replace("```", "")

    data: dict
    try:
        data = json.loads(s=json_str)
    except JSONDecodeError:
        data = json.loads(s=json.dumps(obj=json_str))

    if issubclass(model, RootModel):
        try:
            model(root=data)
        except ValidationError:
            sub_model_data = sub_model().model_dump()
            data = model(root=[sub_model_data]).model_dump()
    else:
        model(data=data)

    return data


@click.command()
@click.option(
    "--input-fp",
    required=True,
    type=lambda x: Path(x).resolve(),
    help="Path to Apache Parquet file to convert to JSON",
)
@click.option(
    "--model",
    required=True,
    type=click.Choice(
        choices=["uses_dl", "uses_ptms", "identify_ptms", "identify_reuse"],
    ),
    help="Path to Apache Parquet file to convert to JSON",
)
def main(input_fp: Path, model: str) -> None:
    df: DataFrame = pandas.read_parquet(path=input_fp, engine="pyarrow")

    df["response_json"] = df["response_text"].apply(json.loads)

    # print(df["response_json"][0])
    # quit()

    df["model_response"] = df["response_json"].apply(
        lambda x: resolve_json(json_str=x["response"], model_str=model)
    )

    df["model_response"].to_json(
        path_or_buf=input_fp.with_suffix(suffix=".json"),
        index=False,
        indent=4,
    )


if __name__ == "__main__":
    main()
