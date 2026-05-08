"""Module for executing Spectronaut in command line mode."""

import logging
import pathlib
import subprocess
import shutil
import time
from typing import Iterable

LOGGER = logging.getLogger(__name__)





def create_spectral_library(
    spectronaut_exec_path: pathlib.Path | str,
    output_dir: pathlib.Path | str,
    library_settings: pathlib.Path | str,
    search_archives: Iterable[pathlib.Path | str],
    search_name: str=None,
    extra_cmd_args: list[str] | None = None,
) -> bool:  
    """Generate spectral library from final search archive .psar using run_spectronaut() function.

    Args:
        spectronaut_exec_path: Path to the Spectronaut executable.
        output_dir: Directory where the Spectronaut search results will be saved.
        library_settings: Path to the Spectronaut library generation settings file. 
        search_archives: Iterable of paths to the pre-existing search archive files. 
        search_name: Optional name for the spectral library.
        extra_cmd_args: Optional list of extra command line arguments.

    Returns:
        True if the Spectronaut search completed successfully, False otherwise.

    Raises:
        FileNotFoundError: If the Spectronaut executable file is not found.
    """
    if extra_cmd_args is None:
        extra_cmd_args = []
    else:
        extra_cmd_args = list(extra_cmd_args)

    for search_archive_path in search_archives:
        extra_cmd_args.extend(["-sa", pathlib.Path(search_archive_path).resolve().as_posix()]) 
    
    extra_cmd_args.extend(["--noOutputSubfolder"])
    return run_spectronaut(
        spectronaut_exec_path=spectronaut_exec_path,
        output_dir=output_dir,
        settings_path=library_settings,
        search_type=["-lg", "-se", "Pulsar"],
        search_name=search_name,
        extra_cmd_args=extra_cmd_args,
        )


def dia_search(
    spectronaut_exec_path: pathlib.Path | str,
    output_dir: pathlib.Path | str,
    settings: pathlib.Path | str,
    fasta: Iterable[pathlib.Path | str],
    rawfiles: Iterable[pathlib.Path | str],
    condition_setup: pathlib.Path | str,
    library: pathlib.Path | str,
    report_schemas: Iterable[pathlib.Path | str],
    search_name: str | None = None,
    write_parquet: bool=False,  
    extra_cmd_args: list[str] | None = None,
) -> bool:
    """DIA library-based search using run_spectronaut() function.

    Args:
        spectronaut_exec_path: Path to the Spectronaut executable.
        output_dir: Directory where the Spectronaut search results will be saved.
        settings: Path to the Spectronaut settings file.
        fasta: Iterable of paths to the FASTA files to be used in the search.
        rawfiles: Iterable of paths to the raw files to be searched.
        condition_setup: Path to the Spectronaut condition setup file.
        library: Path to the spectral library .kit file to use for the search.
        report_schemas: Iterable of paths to the report schema files.
        search_name: Optional name of the Spectronaut search.
        write_parquet: Whether to write the search results to a Parquet file. (default: False)
        extra_cmd_args: Optional list of extra command line arguments.

    Returns:
        True if the Spectronaut search completed successfully, False otherwise.

    Raises:
        FileNotFoundError: If the Spectronaut executable file is not found.
    """
    if extra_cmd_args is None:
        extra_cmd_args = []
    else:
        extra_cmd_args = list(extra_cmd_args)

    extra_cmd_args.extend([
        "-a",
        pathlib.Path(library).resolve().as_posix()
    ])
    
    if write_parquet:
        extra_cmd_args.append("--writeParquet")
        
    extra_cmd_args.extend(["--noOutputSubfolder"])

    return run_spectronaut(
        spectronaut_exec_path=spectronaut_exec_path,
        output_dir=output_dir,
        search_name=search_name,
        settings_path=settings,
        fasta_paths=fasta,
        rawfile_paths=rawfiles,
        condition_setup_path=condition_setup,
        search_type=["diaanalysis"],
        report_schema_paths=report_schemas,
        extra_cmd_args=extra_cmd_args,
        )

def sne_merge(
    spectronaut_exec_path: pathlib.Path | str,
    output_dir: pathlib.Path | str,
    snes: Iterable[pathlib.Path | str],
    condition_setup: pathlib.Path | str,
    report_schemas: Iterable[pathlib.Path | str],
    write_parquet: bool=False,  
    search_name: str| None =None,
    extra_cmd_args: list[str] | None = None,
) -> bool:
    """Merge SNE files from the same spectral library into ONE SNE files using run_spectronaut() function, also generate reports.
     Warning! For large experiments, it may exceed the available disk space and RAM.
         Use the combine command instead to generate combined reports WITHOUT generating SNE.
    Args:
        spectronaut_exec_path: Path to the Spectronaut executable.
        output_dir: Directory where the Spectronaut merge results will be saved.
        snes: Iterable of paths to the SNE files to be used in the merge.
        condition_setup: Path to the Spectronaut condition setup file.
        report_schemas: Iterable of paths to the report schema files.
        write_parquet: Whether to write the reports in parquet format. (default: False)
        search_name: Optional name of the Spectronaut search.
        extra_cmd_args: Optional list of extra command line arguments.

    Returns:
        True if the Spectronaut completed successfully, False otherwise.

    Raises:
        FileNotFoundError: If the Spectronaut executable file is not found.
    """

    if extra_cmd_args is None:
        extra_cmd_args = []
    else:
        extra_cmd_args = list(extra_cmd_args)

    for sne_path in snes:
        extra_cmd_args.extend(["-sne", pathlib.Path(sne_path).resolve().as_posix()]) 

    if write_parquet:
        extra_cmd_args.extend(["--writeParquet"])
        
    extra_cmd_args.extend(["--noOutputSubfolder"])
    
    return run_spectronaut(
        spectronaut_exec_path=spectronaut_exec_path,
        output_dir=output_dir,
        search_type=["manageSNE","--merge"],
        extra_cmd_args=extra_cmd_args,
        condition_setup_path=condition_setup,
        report_schema_paths=report_schemas,
        search_name=search_name,
        )

def sne_combine(
    spectronaut_exec_path: pathlib.Path | str,
    output_dir: pathlib.Path | str,
    snes: Iterable[pathlib.Path | str],
    report_schemas: Iterable[pathlib.Path | str],
    write_parquet: bool=False,
    search_name: str| None =None,
    extra_cmd_args: list[str] | None = None,
) -> bool:
    """Combine SNE files from the same spectral library to generate combined reports WITHOUT generating SNE.
    Args:
        spectronaut_exec_path: Path to the Spectronaut executable.
        output_dir: Directory where the Spectronaut combine results will be saved.
        snes: Iterable of paths to the SNE files to be used in the combine.
        report_schemas: iterable of paths to the report schema files. 
        write_parquet: Whether to write the reports in parquet format. (default: False)
        search_name: Name of the Spectronaut search.
        extra_cmd_args: Optional list of extra command line arguments.

    Returns:
        True if the Spectronaut completed successfully, False otherwise.

    Raises:
        FileNotFoundError: If the Spectronaut executable file is not found.
    """
    print("\n--- Warning!!!   currently in Spectronaut 20.5 only long format report works, pivot table reports are NOT correct!!!.\n")
    
    if extra_cmd_args is None:
        extra_cmd_args = []
    else:
        extra_cmd_args = list(extra_cmd_args)

    for sne in snes:
        extra_cmd_args.extend(["-sne", pathlib.Path(sne).resolve().as_posix()]) 

    extra_cmd_args.extend(["--noOutputSubfolder"])

    if write_parquet:
        extra_cmd_args.extend(["--writeParquet"])

    return run_spectronaut(
        spectronaut_exec_path=spectronaut_exec_path,
        output_dir=output_dir,
        search_name=search_name,
        search_type=["combine"],
        report_schema_paths=report_schemas,
        extra_cmd_args=extra_cmd_args,
        )

def directdia_search(
    spectronaut_exec_path: pathlib.Path | str,
    output_dir: pathlib.Path | str,
    settings: pathlib.Path | str,
    fasta: Iterable[pathlib.Path | str],
    rawfiles: Iterable[pathlib.Path | str],
    condition_setup: pathlib.Path | str, 
    report_schemas: Iterable[pathlib.Path | str],
    write_parquet: bool = False,
    search_name: str | None = None,
    extra_cmd_args: list[str] | None = None,
) -> bool:
    """A run_spectronaut() wrapper function to run directDIA+ search.

    Args:
        spectronaut_exec_path: Path to the Spectronaut executable.
        output_dir: Directory where the Spectronaut search results will be saved.
        settings: Path to the Spectronaut settings file.
        fasta: Iterable of paths to the FASTA files to be used in the search.
        rawfiles: Iterable of paths to the raw files to be searched.
        condition_setup: Path to the Spectronaut condition setup file.
        report_schemas: Iterable of paths to the report schema files.
        write_parquet: Whether to write the search results to a Parquet file.
        search_name: Optional name of the Spectronaut search.
        extra_cmd_args: Optional list of extra command line arguments.

    Returns:
        True if the Spectronaut search completed successfully, False otherwise.

    Raises:
        FileNotFoundError: If the Spectronaut executable file is not found.
    """
    if extra_cmd_args is None:
        extra_cmd_args = []
    else:
        extra_cmd_args = list(extra_cmd_args)
        
    if write_parquet:
        extra_cmd_args.extend(["--writeParquet"])

    success = run_spectronaut(
        spectronaut_exec_path=spectronaut_exec_path,
        output_dir=output_dir,
        search_name=search_name,
        settings_path=settings,
        fasta_paths=fasta,
        rawfile_paths=rawfiles,
        condition_setup_path=condition_setup,
        report_schema_paths=report_schemas,
        search_type=["-direct"],
        extra_cmd_args=extra_cmd_args,
        )

    # identify the search sub-folder and move the contents to the output directory 
    if search_name is None:
        search_name = "Experiment1"

    if success:
        search_folder_path = _identify_spectronaut_search_folder(search_name, output_dir)
        _move_and_replace_folder_contents(search_folder_path, output_dir)

    return success



def run_spectronaut(
    spectronaut_exec_path: pathlib.Path | str,
    output_dir: pathlib.Path | str,
    search_name: str | None = None,
    settings_path: pathlib.Path | str | None = None,
    fasta_paths: Iterable[pathlib.Path | str] | None = None,
    rawfile_paths: Iterable[pathlib.Path | str] | None = None,
    search_type: list[str] | None = None,
    condition_setup_path: pathlib.Path | str | None = None,
    report_schema_paths: Iterable[pathlib.Path | str] | None = None,
    extra_cmd_args: list[str] | None = None,
    logger: logging.Logger | None = None,
) -> bool:
    """Run Spectronaut in command line mode with the specified parameters.

    Args:
        spectronaut_exec_path: Path to the Spectronaut executable.
        output_dir: Directory where the Spectronaut search results will be saved.
        search_name: Name of the Spectronaut search. If None, will not be added to the command line.
        settings_path: Path to the Spectronaut settings file. If None, will not be added to the command line.
        fasta_paths: Iterable of paths to the FASTA files to be used in the search. If None, will not be added to the command line.
        rawfile_paths: Iterable of paths to the rawfiles to be searched. Can be None for 
            library generation or search archive generation.
        search_type: Optional list of search types to run (e.g. ["-direct"] for directDIA+ search; 
            ["-lg", "-se", "Pulsar"] for library generation; or None for library-based DIA search). 
        condition_setup_path: Optional path to the Spectronaut condition setup file.
        report_schema_paths: Optional iterable of paths to the report schema files.
        extra_cmd_args: Optional list of extra command line arguments.
        logger: Optional logger to use for logging messages.

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
    if fasta_paths is not None:
        _fasta_paths = [pathlib.Path(p) for p in fasta_paths]
        if any(not fp.exists() for fp in _fasta_paths):
            logger.error("One or more FASTA files do not exist.")
            return False

    if rawfile_paths is not None:
        _rawfile_paths = [pathlib.Path(p) for p in rawfile_paths]
        if any(not rp.exists() for rp in _rawfile_paths):
            logger.error("One or more rawfiles do not exist.")
            return False

    cmd = ["dotnet", pathlib.Path(spectronaut_exec_path).as_posix()]
    if search_type is not None:
        cmd.extend(search_type)
    
    if search_name is not None:
        cmd.extend(["-n", search_name])

    if settings_path is not None:
        cmd.extend(["-s", pathlib.Path(settings_path).resolve().as_posix()])

    cmd.extend([
        "-o",
        pathlib.Path(output_dir).resolve().as_posix(),
    ])

    if fasta_paths is not None:
        for fasta_path in _fasta_paths:
            cmd.extend(["-fasta", fasta_path.resolve().as_posix()])
    if rawfile_paths is not None:    
        for rawfile_path in _rawfile_paths:
            cmd.extend(["-r", rawfile_path.resolve().as_posix()])
    if condition_setup_path is not None:
        cmd.extend(["-con", pathlib.Path(condition_setup_path).resolve().as_posix()])
    if report_schema_paths is not None:
        for schema_path in report_schema_paths:
            cmd.extend(["-rs", pathlib.Path(schema_path).resolve().as_posix()])
    if extra_cmd_args is not None:
        cmd.extend(extra_cmd_args)  
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