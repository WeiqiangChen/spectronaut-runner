"""Module for executing Spectronaut in command line mode."""

import logging
import pathlib
import shutil
import subprocess
import time
from typing import Iterable

LOGGER = logging.getLogger(__name__)


def run_spectronaut(
    spectronaut_exec_path: pathlib.Path | str,
    output_dir: pathlib.Path | str,
    search_name: str,
    settings_path: pathlib.Path | str,
    condition_setup_path: pathlib.Path | str,
    fasta_paths: Iterable[pathlib.Path | str],
    rawfile_paths: Iterable[pathlib.Path | str],
    report_schema_paths: Iterable[pathlib.Path | str] | None = None,
    logger: logging.Logger | None = None,
) -> bool:
    """Run Spectronaut directDIA in command line mode with the specified parameters.

    Args:
        spectronaut_exec_path: Path to the Spectronaut executable.
        output_dir: Directory where the Spectronaut search results will be saved.
        search_name: Name of the Spectronaut search.
        settings_path: Path to the Spectronaut settings file.
        condition_setup_path: Path to the Spectronaut condition setup file.
        fasta_paths: Iterable of paths to the FASTA files to be used in the search. The
            FASTA files can either be in .fasta or .bgsfasta format.
        rawfile_paths: Iterable of paths to the rawfiles to be searched. The rawfiles
            must correspond to the files listed in the condition setup file.
        report_schema_paths: Optional iterable of paths to the report schema files to
            be used for generating reports. if None, only the report schemas defined in
            the settings file will be used.
        logger: Optional logger to use for logging messages. If None, the module-level
            logger will be used.

    Returns:
        True if the Spectronaut search completed successfully, False otherwise.

    Raises:
        FileNotFoundError: If the Spectronaut executable file is not found.
    """
    if logger is None:
        logger = LOGGER
    if not pathlib.Path(spectronaut_exec_path).exists():
        raise FileNotFoundError(
            f"Spectronaut executable file not found at {spectronaut_exec_path}. "
            "Please check the path."
        )
    _fasta_paths = [pathlib.Path(p) for p in fasta_paths]
    if any(not fp.exists() for fp in _fasta_paths):
        logger.error("One or more FASTA files do not exist.")
        return False
    _rawfile_paths = [pathlib.Path(p) for p in rawfile_paths]
    if any(not rp.exists() for rp in _rawfile_paths):
        logger.error("One or more rawfiles do not exist.")
        return False

    cmd = [
        pathlib.Path(spectronaut_exec_path).as_posix(),
        "-direct",
        "-s",
        pathlib.Path(settings_path).resolve().as_posix(),
        "-con",
        pathlib.Path(condition_setup_path).resolve().as_posix(),
        "-n",
        search_name,
        "-o",
        pathlib.Path(output_dir).resolve().as_posix(),
    ]
    for fasta_path in _fasta_paths:
        cmd.extend(["-fasta", fasta_path.resolve().as_posix()])
    for rawfile_path in _rawfile_paths:
        cmd.extend(["-r", rawfile_path.resolve().as_posix()])
    if report_schema_paths is not None:
        for schema_path in report_schema_paths:
            cmd.extend(["-rs", pathlib.Path(schema_path).resolve().as_posix()])
    logger.info(f"Running Spectronaut with output directory '{output_dir}'")
    logger.debug(f"Spectronaut command: {' '.join(cmd)}")

    try:
        start_time = time.time()
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
        )
        duration = (time.time() - start_time) / 60
        logger.info(f"Spectronaut completed successfully in {duration:.2f} minutes.")

        search_folder_path = _identify_spectronaut_search_folder(
            search_name, output_dir, result.stdout
        )
        _move_and_replace_folder_contents(search_folder_path, output_dir)
        logger.debug(f"Moved Spectronaut output to '{output_dir}'")

        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running Spectronaut: {e}\nError output:\n{e.stderr}\n")
        return False


def search_results_exist(output_dir: pathlib.Path | str) -> bool:
    """Check if Spectronaut search results exist in the specified output directory.

    Checks for the presence of a Spectronaut ConditionSetup file or a .sne file.

    Args:
        output_dir: Path to Spectronaut output directory

    Returns:
        True if search results exist, False otherwise
    """
    output_dir = pathlib.Path(output_dir)
    if not output_dir.exists():
        return False

    condition_setup_files = list(output_dir.glob("*ConditionSetup.tsv"))
    sne_files = list(output_dir.glob("*.sne"))
    if not (condition_setup_files or sne_files):
        return False

    return True


def _identify_spectronaut_search_folder(
    search_name: str, output_dir: pathlib.Path | str, stdout: str = ""
) -> pathlib.Path:
    """Attempts to identify the Spectronaut search folder within the given directory.

    If `stdout` is provided, it will be parsed to find the definitive output path set by
    Spectronaut. The output path must be a directory that ends with the `search_name`
    and is located directly within the `output_dir`.

    If the search folder cannot be found in the stdout or no stdout is provided, and
    multiple folders ending with the search name exist in the output directory, the
    newest one according to the timestamp prefix will be returned.

    Args:
        search_name: The search name to look for in the folder names of the output
            directory. Spectronaut generates result folders by prefixing the search name
            with a timestamp in the format "YYYYMMDD_HHMMSS_".
        output_dir: The directory where the search folder is expected to be found.
        stdout: Optional stdout string from Spectronaut execution to parse for the
            definitive output path.

    Returns:
        The path to the identified Spectronaut search folder.

    Raises:
        FileNotFoundError: If no folder ending with the search name is found in the
            output directory.
    """
    time_stamp_length = len("YYYYMMDD_HHMMSS_")
    output_path = pathlib.Path(output_dir).resolve()
    if stdout:
        for line in stdout.splitlines():
            if "Set output destination to:" in line:
                path_str = line.split("Set output destination to:")[-1].strip()
                potential_path = pathlib.Path(path_str).resolve()
                if not potential_path.is_dir():
                    break
                if not potential_path.name[time_stamp_length:] == search_name:
                    break
                if not potential_path.parent == output_path:
                    break
                return potential_path

    candidate_folders = [
        p
        for p in output_path.iterdir()
        if p.is_dir() and p.name[time_stamp_length:] == search_name
    ]
    if not candidate_folders:
        raise FileNotFoundError(
            f"No folder ending with '{search_name}' found in '{output_dir}'"
        )
    latest_candidate_folder = sorted(candidate_folders)[-1]
    return latest_candidate_folder


def _move_and_replace_folder_contents(
    source_dir: pathlib.Path | str,
    destination_dir: pathlib.Path | str,
) -> None:
    """Moves the source directory to the destination directory, replacing existing
    files and merging folders as needed.

    Args:
        source_dir: Path of the source directory.
        destination_dir: Path of the destination directory.
    """
    source_path = pathlib.Path(source_dir)
    destination_path = pathlib.Path(destination_dir)
    destination_path.mkdir(parents=True, exist_ok=True)

    for item_path in source_path.iterdir():
        dest_item_path = destination_path / item_path.name

        if item_path.is_dir() and dest_item_path.is_dir():
            _move_and_replace_folder_contents(item_path, dest_item_path)
            item_path.rmdir()
            continue

        if dest_item_path.exists():
            if dest_item_path.is_dir():
                shutil.rmtree(dest_item_path)
            else:
                dest_item_path.unlink()

        shutil.move(item_path, dest_item_path)
    source_path.rmdir()
