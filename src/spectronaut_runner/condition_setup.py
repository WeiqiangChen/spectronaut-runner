import logging
import pathlib
from typing import Iterable, Sequence

import pandas as pd

logger = logging.getLogger(__name__)

SUPPORTED_FILE_FORMATS = ["raw", "d", "wiff", "tdf", "baf", "d.tar", "htrms", "bgms"]
CONDITION_SETUP_COLUMN_ORDER = [
    "#",
    "Reference",
    "Run Label",
    "Condition",
    "Fraction",
    "Replicate",
    "Quantity Correction Factor",
    "Label",
    "Color",
    "File Name",
]
CONDITION_COLORS = [
    "#80b1d3",
    "#fdb462",
    "#8dd3c7",
    "#bebada",
    "#fb8072",
    "#b3de69",
    "#fccde5",
    "#d9d9d9",
    "#bc80bd",
    "#ccebc5",
]


def sdrf_to_condition_setup(
    sdrf_filepath: pathlib.Path | str,
    condition_filepath: pathlib.Path | str | None = None,
    condition_filename: str = "ConditionSetup.tsv",
    condition_field: str = "comment[data file]",
    replicate_field: str = "characteristics[biological replicate]",
) -> None:
    """Convert an SDRF file to a Spectronaut-compatible condition setup file.

    Args:
        sdrf_filepath: Path to the SDRF file.
        condition_filepath: Filepath to save the FragPipe manifest file. If None, saves
            to the same directory as the SDRF file using the 'condition_filename'.
        condition_filename: Filename to use for the created manifest if
            'condition_filepath' is None. Default is "ConditionSetup.tsv".
        condition_field: Name of the SDRF column to use for the condition information.
        replicate_field: Name of the SDRF column to use for the replicate information.
    """
    logger.info(
        f"Converting SDRF file '{sdrf_filepath}' to Spectronaut condition setup file."
    )
    if condition_filepath is None:
        output_filepath = pathlib.Path(sdrf_filepath).parent / condition_filename
    else:
        output_filepath = pathlib.Path(condition_filepath)

    sdrf_table = pd.read_csv(sdrf_filepath, sep="\t")
    condition_setup = (
        pd.DataFrame(
            {
                "File Name": sdrf_table["comment[data file]"],
                "Condition": sdrf_table[condition_field],
                "Replicate": sdrf_table[replicate_field],
            }
        )
        .drop_duplicates()
        .reset_index(drop=True)
        .reset_index(names="#")
    )

    condition_setup["File Name"] = _remove_file_extension(
        condition_setup["File Name"], SUPPORTED_FILE_FORMATS
    )
    condition_setup["Run Label"] = (
        condition_setup["Condition"] + "_" + condition_setup["Replicate"].astype(str)
    )
    condition_setup["Color"] = _conditions_to_colors(
        condition_setup["Condition"], CONDITION_COLORS
    )
    condition_setup["Label"] = condition_setup["Run Label"]
    condition_setup["Reference"] = "FALSE"
    condition_setup["Fraction"] = "NA"
    condition_setup["Quantity Correction Factor"] = 1
    condition_setup = condition_setup[CONDITION_SETUP_COLUMN_ORDER]

    logger.debug(f"Writing Spectronaut condition setup file to '{output_filepath}'")
    output_filepath.parent.mkdir(parents=True, exist_ok=True)
    condition_setup.to_csv(output_filepath, sep="\t", index=False, header=True)


def get_rawfile_paths(
    condition_setup_filepath: pathlib.Path | str,
    rawfile_directory: pathlib.Path | str | None = None,
    prioritize_htrms: bool = True,
) -> list[pathlib.Path]:
    """Find and return the rawfile paths from the Spectronaut condition setup file.

    Args:
        condition_setup_filepath: Path to the Spectronaut condition setup file.
        rawfile_directory: Directory where the rawfiles are located. If None, uses the
            directory of the condition setup file.
        prioritize_htrms: If True, prioritize .htrms files when multiple formats exist.
            Default is True.

    Returns:
        List of pathlib.Path objects for the found rawfiles.
    """
    if rawfile_directory is None:
        rawfile_directory = pathlib.Path(condition_setup_filepath).parent
    rawfile_directory = pathlib.Path(rawfile_directory).resolve()

    condition_setup = pd.read_csv(condition_setup_filepath, sep="\t")
    extensions = SUPPORTED_FILE_FORMATS.copy()
    if prioritize_htrms:
        extensions.remove("htrms")
        extensions = ["htrms"] + extensions

    rawfile_paths = []
    for filename in condition_setup["File Name"]:
        found = False
        for ext in extensions:
            candidate_path = rawfile_directory / f"{filename}.{ext}"
            if candidate_path.exists():
                rawfile_paths.append(candidate_path)
                found = True
                break
        if not found:
            logger.warning(
                f"Rawfile for '{filename}' not found in '{rawfile_directory}'."
            )
    return rawfile_paths


def _remove_file_extension(
    filenames: Iterable[str], extensions: Iterable[str]
) -> list[str]:
    cleaned_filenames = []
    for filename in filenames:
        for ext in extensions:
            if filename.lower().endswith(f".{ext.lower()}"):
                filename = filename[: -(len(ext) + 1)]
                break
        cleaned_filenames.append(filename)
    return cleaned_filenames


def _conditions_to_colors(
    conditions: Iterable[str], color_palette: Sequence[str]
) -> list[str]:
    unique_conditions = sorted(set(conditions))
    condition_color_map = {}
    for idx, condition in enumerate(unique_conditions):
        color = color_palette[idx % len(color_palette)]
        condition_color_map[condition] = color
    return [condition_color_map[c] for c in conditions]
