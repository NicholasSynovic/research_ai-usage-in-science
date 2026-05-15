#!/usr/bin/env python3

import argparse
import csv
import re
from pathlib import Path


def normalize_key(value: str) -> str:
    value = value.strip().lower()
    value = value.replace("_", " ")
    value = value.replace("/", " ")
    value = value.replace("-", " ")
    value = value.replace("(", " ").replace(")", " ")
    value = re.sub(r"[^a-z0-9. ]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


EXACT_RULES: list[tuple[str, str]] = [
    ("af2", "alphafold2"),
    ("af2 multimer", "alphafold2 multimer"),
    ("af3", "alphafold3"),
    ("alpha fold", "alphafold"),
    ("alphafold af", "alphafold"),
    ("alphafold af2", "alphafold2"),
    ("alphafold af3", "alphafold3"),
    ("alphafold database", "alphafold"),
    ("alphafold multimer", "alphafold2 multimer"),
    ("alphafold multimer v2.3", "alphafold2 multimer"),
    ("alphafold 2", "alphafold2"),
    ("alphafold 2 method", "alphafold2"),
    ("alphafold 3", "alphafold3"),
    ("alphafold version 2.1.0", "alphafold2"),
    ("alphafold v2.0.1", "alphafold2"),
    ("alphafold v2.1.1", "alphafold2"),
    ("alphafold2 multimer", "alphafold2 multimer"),
    ("alphafold2 v2.1", "alphafold2"),
    ("alphafold2 af2", "alphafold2"),
    ("alphafold (af2)", "alphafold2"),
    ("alphafold (af3)", "alphafold3"),
    ("alphafold (v2.1.1)", "alphafold2"),
    ("alphafold-multimer", "alphafold2 multimer"),
    (
        "alphafold2-multimer (alphafold2 version 2.3) as implemented on colabfold",
        "alphafold2 multimer",
    ),
    ("af multimer", "alphafold2 multimer"),
    ("alphafold3 af3", "alphafold3"),
    ("attention unet", "u-net"),
    ("attention unet 2", "u-net"),
    ("attention u net", "u-net"),
    ("bert base", "bert-base"),
    ("bert base uncase", "bert-base-uncased"),
    ("bert base uncased", "bert-base-uncased"),
    ("bert basic", "bert-base"),
    ("biobert base v1.0", "biobert"),
    ("clinical bert", "clinicalbert"),
    ("convolutional neural network (cnn)", "cnn"),
    ("cornet-s", "cornet s"),
    ("cornet-z", "cornet z"),
    ("d-script", "d script"),
    ("2d u net", "u-net"),
    ("3d u net", "u-net"),
    ("colabfold", "colabfold"),
    ("colabfold 1.5.2", "colabfold"),
    ("contrastive alexnet", "alexnet"),
    ("deepbrain extractor pre trained 3d u net", "u-net"),
    ("deeplab v2 resnet 101", "deeplabv2"),
    ("deeplab v3", "deeplabv3"),
    ("deeplab v3+", "deeplabv3"),
    ("deeplabv3", "deeplabv3"),
    ("deeplabv3+", "deeplabv3"),
    ("deeplabcut 2.2", "deeplabcut"),
    ("deeploc 1.0", "deeploc"),
    ("deeploc 2.0", "deeploc"),
    ("deeploc2.0", "deeploc"),
    ("deep variant", "deepvariant"),
    ("deepvariant v1.2.0", "deepvariant"),
    ("distilled roberta model", "roberta"),
    ("en core web lg", "spacy en_core_web_lg"),
    ("esm 1b", "esm-1b"),
    ("esm 1b ts", "esm-1b"),
    ("esm 1b transformer", "esm-1b"),
    ("esm 2", "esm-2"),
    ("esm 2 650m", "esm-2"),
    ("esm 2 3b", "esm-2"),
    ("esm inverse folding esm if", "esm-if"),
    ("esm if1", "esm-if"),
    ("esm2 t12 35m ur50d", "esm-2"),
    ("faster r cnn", "faster r-cnn"),
    ("faster rcnn", "faster r-cnn"),
    ("frcnnr50", "faster r-cnn"),
    ("google inception", "googlenet"),
    ("google inception v3", "inception v3"),
    ("inception net", "inception"),
    ("inception net v3", "inception v3"),
    ("inception-v2", "inception v2"),
    ("inception-v4", "inception v4"),
    ("inception resnet", "inception-resnet-v2"),
    ("inception resnet v2", "inception-resnet-v2"),
    ("inceptionresnetv2", "inception-resnet-v2"),
    ("inceptionv3", "inception v3"),
    ("mask r cnn", "mask r-cnn"),
    ("mask rcnn", "mask r-cnn"),
    ("mask rcnn x 101 32x8d fpn 3x", "mask r-cnn"),
    ("mobile net", "mobilenet"),
    ("mobilenet v1", "mobilenet"),
    ("mobilenet v2", "mobilenetv2"),
    ("mobilenet v3", "mobilenetv3"),
    ("mobilenet v3 large", "mobilenetv3-large"),
    ("mobilenet v3 small", "mobilenetv3-small"),
    ("mobilenetv2", "mobilenetv2"),
    ("mobilenetv3 large", "mobilenetv3-large"),
    ("mobilenetv3 small", "mobilenetv3-small"),
    ("multiunet", "u-net"),
    ("nnu net", "u-net"),
    ("nnunet", "u-net"),
    ("restnet 34", "resnet34"),
    ("restnet 50", "resnet50"),
    ("restnet34", "resnet34"),
    ("restnet50", "resnet50"),
    ("rnet18", "resnet18"),
    ("stardist versatile fluorescent nuclei built in model within fiji", "stardist"),
    ("standard u net", "u-net"),
    ("v net", "v-net"),
    ("vgg 16 19", "vgg16"),
    ("swin b", "swin transformer"),
    ("swin t", "swin transformer"),
    ("swin transformer st", "swin transformer"),
    ("swinunet", "swin u-net"),
    ("swin u net", "swin u-net"),
    ("u net", "u-net"),
    ("u net plus plus", "u-net++"),
    ("unet", "u-net"),
    ("unet plus plus", "u-net++"),
    ("vgg 11", "vgg11"),
    ("vgg 13", "vgg13"),
    ("vgg 16", "vgg16"),
    ("vgg 16 bn", "vgg16"),
    ("vgg 16 imagenet", "vgg16"),
    ("vgg 19", "vgg19"),
    ("vgg 54", "vgg54"),
    ("vgg face", "vggface"),
    ("vgg net", "vgg"),
    ("vgg net 16", "vgg16"),
    ("vggnet", "vgg"),
    ("vggnet 16", "vgg16"),
    ("vgg 16 19", "vgg16"),
    ("word2vec (skip-gram)", "word2vec"),
    ("skip-gram model", "word2vec"),
    ("spot-rna", "spot-rna"),
    ("swin-transformer", "swin transformer"),
    ("r(2+1)d", "r(2+1)d"),
    ("xlm-roberta base", "xlm-roberta"),
    ("vision transformer", "vision transformer"),
    ("vision transformer vit", "vision transformer"),
    ("vit", "vision transformer"),
    ("vit base patch16 224", "vision transformer"),
    ("vit b", "vision transformer"),
    ("vit b16", "vision transformer"),
    ("vit b32", "vision transformer"),
    ("vit encoder", "vision transformer"),
    ("vit l", "vision transformer"),
    ("vit l16", "vision transformer"),
    ("vit l32", "vision transformer"),
    ("vit large", "vision transformer"),
    ("yolo", "yolo"),
    ("yolo v2", "yolov2"),
    ("yolo v3", "yolov3"),
    ("yolo v4", "yolov4"),
    ("yolo v5", "yolov5"),
    ("yolo v5 cact", "yolov5"),
    ("yolo v5 small", "yolov5s"),
    ("yolo v5s", "yolov5s"),
    ("yolo v5l", "yolov5l"),
    ("yolo v7", "yolov7"),
    ("yolo v7x pt", "yolov7x"),
    ("yolov7x.pt", "yolov7x"),
    ("yolo v8", "yolov8"),
    ("yolo v8n", "yolov8n"),
    ("yolo v8s", "yolov8s"),
    ("yolo v8m", "yolov8m"),
    ("yolo v8l", "yolov8l"),
    ("yolo v8x", "yolov8x"),
    ("yolox", "yolox"),
    ("yolox nano", "yolox-nano"),
    ("yolox tiny", "yolox-tiny"),
    ("yolox s", "yolox-s"),
    ("yolox m", "yolox-m"),
    ("yolox l", "yolox-l"),
    ("yolox x", "yolox-x"),
]


REGEX_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^af3$"), "alphafold3"),
    (re.compile(r"^alphafold$"), "alphafold"),
    (re.compile(r"^alphafold ?3$"), "alphafold3"),
    (re.compile(r"^alphafold3(?:\.?\d+)?$"), "alphafold3"),
    (re.compile(r"^alphafold(?: v)? ?2(?:\.\d+)*$"), "alphafold2"),
    (re.compile(r"^alphafold2(?:\.\d+)*$"), "alphafold2"),
    (re.compile(r"^alphafold monomer v2(?:\.\d+)*$"), "alphafold monomer v2"),
    (re.compile(r"^alphafoldmultimer(?: afm)?$"), "alphafold2 multimer"),
    (
        re.compile(r"^alphafold2 multimer(?: v\.?\d+(?:\.\d+)*)?$"),
        "alphafold2 multimer",
    ),
    (re.compile(r"^alex cnn model$"), "alexnet"),
    (
        re.compile(r"^antimicrobial peptide scanner vr ?2$"),
        "antimicrobial peptide scanner v2",
    ),
    (re.compile(r"^cnn pretrained on cifar10$"), "cnn"),
    (re.compile(r"^convolutional neural network cnn$"), "cnn"),
    (re.compile(r"^weaklysupervised convolutional neural network cnn$"), "cnn"),
    (
        re.compile(r"^deep convolutional neural network model$"),
        "deep convolutional neural network",
    ),
    (re.compile(r"^deep learning model$"), "deep learning model"),
    (
        re.compile(r"^geometric encoder message passing neural network$"),
        "message passing neural network",
    ),
    (re.compile(r"^parallel convolutional neural network pcnn$"), "pcnn"),
    (re.compile(r"^restricted boltzmann machine rbm$"), "restricted boltzmann machine"),
    (re.compile(r"^segment anything model sam$"), "segment anything model"),
    (re.compile(r"^sam resnet$"), "sam-resnet"),
    (
        re.compile(r"^temporal convolutional network tcn$"),
        "temporal convolutional network",
    ),
    (re.compile(r"^variational autoencoder vae$"), "variational autoencoder"),
    (re.compile(r"^vision transformer vit$"), "vision transformer"),
    (re.compile(r"^chat gpt 4o$"), "chatgpt-4o"),
    (re.compile(r"^inception(?:net)?(?: ?v3)?$"), "inception"),
    (re.compile(r"^inception(?:net)? ?v3$"), "inception v3"),
    (re.compile(r"^inception v2$"), "inception v2"),
    (re.compile(r"^inception v4$"), "inception v4"),
    (re.compile(r"^inceptionresnet(?: ?|-)?v2$"), "inception-resnet-v2"),
    (re.compile(r"^inception(?: ?|-)?resnet(?: ?|-)?v2$"), "inception-resnet-v2"),
    (re.compile(r"^mask ?r ?cnn(?: .*)?$"), "mask r-cnn"),
    (re.compile(r"^faster ?r ?cnn(?: .*)?$"), "faster r-cnn"),
    (re.compile(r"^r ?cnn$"), "faster r-cnn"),
    (re.compile(r"^unet(?:\+\+)?$"), "u-net"),
    (re.compile(r"^u net(?:\+\+)?$"), "u-net"),
    (re.compile(r"^signalp(?: ?|-)?5(?:\.0)?$"), "signalp 5"),
    (re.compile(r"^signalp(?: ?|-)?6(?:\.0)?$"), "signalp 6"),
    (re.compile(r"^stable diffusion version 1\.5$"), "stable diffusion v1"),
    (re.compile(r"^stablediffusion v1\.4$"), "stable diffusion v1"),
    (re.compile(r"^net ?mhc ?4(?:\.0)?$"), "netmhc 4"),
    (re.compile(r"^net ?mhc ?3(?:\.4)?$"), "netmhc 3"),
    (re.compile(r"^net ?mhcpan ?4(?:\.1)?$"), "netmhcpan 4"),
    (re.compile(r"^net ?mhcpan el 4(?:\.0)?$"), "netmhcpan 4"),
    (re.compile(r"^net ?mhciipan ?4(?:\.0)?$"), "netmhciipan 4"),
    (re.compile(r"^netsurfp ?2(?:\.0)?$"), "netsurfp 2"),
    (
        re.compile(r"^resnet(?: ?|-)?(1d|9|18|26|34|50|101|152|200)$"),
        lambda m: f"resnet{m.group(1)}",
    ),
    (re.compile(r"^resnet(?: ?|-)?50v2$"), "resnet50"),
    (re.compile(r"^resnet(?: ?|-)?152v2$"), "resnet152"),
    (re.compile(r"^resnet(?: ?|-)?v1 ?50$"), "resnet50"),
    (re.compile(r"^resnet(?: ?|-)?v2$"), "resnet"),
    (
        re.compile(r"^restnet(?: ?|-)?(18|34|50|101|152)$"),
        lambda m: f"resnet{m.group(1)}",
    ),
    (re.compile(r"^rnet18$"), "resnet18"),
    (
        re.compile(r"^wide resnet(?: ?|-)?(50|101)(?: .*)?$"),
        lambda m: f"resnet{m.group(1)}",
    ),
    (re.compile(r"^se resnet(?: ?|-)?101$"), "resnet101"),
    (re.compile(r"^resnext(?: ?|-)?(101|50)$"), lambda m: f"resnext{m.group(1)}"),
    (re.compile(r"^resnext101(?: _32 x 8d)?$"), "resnext101"),
    (re.compile(r"^vgg(?: ?|-)?(11|13|16|19|54)$"), lambda m: f"vgg{m.group(1)}"),
    (re.compile(r"^vgg(?: ?|-)?16 bn$"), "vgg16"),
    (re.compile(r"^vgg(?: ?|-)?16 imagenet$"), "vgg16"),
    (re.compile(r"^vgg(?: ?|-)?net(?: ?|-)?(16)$"), "vgg16"),
    (re.compile(r"^vgg(?: ?|-)?net$"), "vgg"),
    (
        re.compile(r"^densenet(?: ?|-)?(121|169|201|161|50|109)$"),
        lambda m: f"densenet{m.group(1)}",
    ),
    (re.compile(r"^densenet(?: ?|-)? m161$"), "densenet161"),
    (re.compile(r"^densnet(?: ?|-)?121$"), "densenet121"),
    (re.compile(r"^mobilenet(?: ?|-)?v?1$"), "mobilenet"),
    (re.compile(r"^mobilenet(?: ?|-)?v?2$"), "mobilenetv2"),
    (re.compile(r"^mobilenet(?: ?|-)?v?3(?: ?|-)?small$"), "mobilenetv3-small"),
    (re.compile(r"^mobilenet(?: ?|-)?v?3(?: ?|-)?large$"), "mobilenetv3-large"),
    (re.compile(r"^mobilenetv3(?: ?|-)?small$"), "mobilenetv3-small"),
    (re.compile(r"^mobilenetv3(?: ?|-)?large$"), "mobilenetv3-large"),
    (
        re.compile(r"^efficientnet(?: ?|-)?(b?0|0\.5|0\.25|b?1|b?2|b?3|b?4|b?6|b?7)$"),
        lambda m: f"efficientnet{m.group(1)}",
    ),
    (re.compile(r"^efficientnetv2(?: ?|-)?small$"), "efficientnetv2"),
    (re.compile(r"^efficientnetv2$"), "efficientnetv2"),
    (re.compile(r"^deeplab(?: ?|-)?v2(?: .*)?$"), "deeplabv2"),
    (re.compile(r"^deeplab(?: ?|-)?v3\+?$"), "deeplabv3"),
    (re.compile(r"^deeplabcut(?: .*)?$"), "deeplabcut"),
    (re.compile(r"^deep tmhmm(?: .*)?$"), "deeptmhmm"),
    (re.compile(r"^deeptmhmm(?: .*)?$"), "deeptmhmm"),
    (re.compile(r"^deepvariant(?: .*)?$"), "deepvariant"),
    (re.compile(r"^cellpose(?: .*)?$"), "cellpose"),
    (re.compile(r"^stardist(?: .*)?$"), "stardist"),
    (re.compile(r"^stable diffusion(?: .*)?$"), "stable diffusion"),
    (
        re.compile(r"^chat ?gpt ?(3\.5|4|4o)(?: .*)?$"),
        lambda m: f"chatgpt-{m.group(1)}",
    ),
    (re.compile(r"^gpt ?(2|3|4)(?:\.5)?(?: .*)?$"), lambda m: f"gpt-{m.group(1)}"),
    (re.compile(r"^bert(?: .*)?$"), "bert"),
    (re.compile(r"^roberta(?: .*)?$"), "roberta"),
    (re.compile(r"^distilroberta(?: .*)?$"), "roberta"),
    (re.compile(r"^clinicalbert(?: .*)?$"), "clinicalbert"),
    (re.compile(r"^biobert(?: .*)?$"), "biobert"),
    (re.compile(r"^pubmedbert(?: .*)?$"), "pubmedbert"),
    (re.compile(r"^scibert(?: .*)?$"), "scibert"),
    (re.compile(r"^electra(?: .*)?$"), "electra"),
    (re.compile(r"^macbert(?: .*)?$"), "macbert"),
    (re.compile(r"^dnabert(?: .*)?$"), "dnabert"),
    (re.compile(r"^protbert(?: .*)?$"), "protbert"),
    (re.compile(r"^protbert bfd(?: .*)?$"), "protbert-bfd"),
    (re.compile(r"^esm(?: ?|-)?1b(?: .*)?$"), "esm-1b"),
    (re.compile(r"^esm(?: ?|-)?2(?: .*)?$"), "esm-2"),
    (re.compile(r"^esmfold(?: .*)?$"), "esmfold"),
    (re.compile(r"^esm if(?: .*)?$"), "esm-if"),
    (re.compile(r"^prot ?t?5(?: .*)?$"), "prott5"),
    (re.compile(r"^proteinmpnn(?: .*)?$"), "proteinmpnn"),
    (re.compile(r"^abmpnn(?: .*)?$"), "abmpnn"),
    (re.compile(r"^mxfold2(?: .*)?$"), "mxfold2"),
    (re.compile(r"^colabfold(?: .*)?$"), "colabfold"),
    (re.compile(r"^rosettafold2na(?: .*)?$"), "rosettafold2na"),
    (re.compile(r"^rosettafold(?: .*)?$"), "rosettafold"),
    (re.compile(r"^alphalink(?: .*)?$"), "alphalink"),
    (re.compile(r"^af multimer(?: .*)?$"), "alphafold2 multimer"),
    (
        re.compile(r"^yolov?(1|2|3|4|5|7|8)(?:[snmlx])?(?:\.pt)?(?: .*)?$"),
        lambda m: f"yolov{m.group(1)}",
    ),
    (
        re.compile(r"^yolo(?: ?|-)?v?(1|2|3|4|5|7|8)(?:[snmlx])?(?:\.pt)?(?: .*)?$"),
        lambda m: f"yolov{m.group(1)}",
    ),
    (
        re.compile(r"^yolox(?: ?|-)?(nano|tiny|s|m|l|x)?(?: .*)?$"),
        lambda m: f"yolox-{m.group(1)}" if m.group(1) else "yolox",
    ),
    (re.compile(r"^ssd(?: .*)?$"), "ssd"),
    (re.compile(r"^fcn(?: .*)?$"), "fcn"),
    (re.compile(r"^xception(?: \d+)?$"), "xception"),
    (re.compile(r"^xlm roberta base$"), "xlm-roberta"),
    (re.compile(r"^skip gram model$"), "word2vec"),
    (re.compile(r"^word2vec skip gram$"), "word2vec"),
    (re.compile(r"^spot rna$"), "spot-rna"),
    (re.compile(r"^swin transformer(?: .*)?$"), "swin transformer"),
    (re.compile(r"^swin transformer$"), "swin transformer"),
    (re.compile(r"^r 2 1 d$"), "r(2+1)d"),
    (re.compile(r"^d script$"), "d-script"),
    (re.compile(r"^cornet s$"), "cornet-s"),
    (re.compile(r"^cornet z$"), "cornet-z"),
    (re.compile(r"^inception-v2$"), "inception v2"),
    (re.compile(r"^inception-v4$"), "inception v4"),
    (re.compile(r"^convnext(?: .*)?$"), "convnext"),
    (re.compile(r"^swin(?: .*)?$"), "swin transformer"),
    (re.compile(r"^maxvit(?: .*)?$"), "maxvit"),
    (re.compile(r"^vit(?: .*)?$"), "vision transformer"),
    (re.compile(r"^gem-unet$"), "u-net"),
    (re.compile(r"^nnunet(?: .*)?$"), "u-net"),
    (re.compile(r"^nnu net(?: .*)?$"), "u-net"),
    (re.compile(r"^u net(?: .*)?$"), "u-net"),
    (re.compile(r"^mask textspotter v3$"), "mask textspotter v3"),
    (re.compile(r"^cellvit(?: .*)?$"), "cellvit"),
    (re.compile(r"^dino(?: .*)?$"), "dino"),
    (re.compile(r"^caffenet(?: .*)?$"), "caffenet"),
    (re.compile(r"^googlenet(?: .*)?$"), "googlenet"),
    (re.compile(r"^lenet(?: ?|-)?5$"), "lenet5"),
    (re.compile(r"^transformer model from vaishnav et al$"), "transformer"),
    (re.compile(r"^convolutional model from vaishnav et al$"), "cnn"),
    (
        re.compile(r"^pretrained image classifier algorithm$"),
        "pretrained image classifier",
    ),
]


def normalize_name(value: str) -> str:
    key = normalize_key(value)

    for raw_value, replacement in EXACT_RULES:
        if key == raw_value:
            return replacement

    for pattern, replacement in REGEX_RULES:
        match = pattern.fullmatch(key)
        if not match:
            continue

        if callable(replacement):
            return replacement(match)

        if "\\" in replacement:
            return match.expand(replacement)

        return replacement

    return key


def load_models(input_path: Path) -> list[str]:
    with input_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [normalize_name(row["models"]) for row in reader if row.get("models")]


def write_models(models: list[str], output_path: Path | None) -> None:
    output = "\n".join(models)
    if output:
        output += "\n"

    if output_path is None:
        print(output, end="")
        return

    output_path.write_text(output, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize PTM/model names.")
    parser.add_argument(
        "input",
        nargs="?",
        default="data/ptms.csv",
        help="Path to the CSV file with a single 'models' column.",
    )
    parser.add_argument(
        "--output",
        help="Optional output file. Defaults to stdout.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else None

    models = load_models(input_path)
    write_models(models, output_path)


if __name__ == "__main__":
    main()
