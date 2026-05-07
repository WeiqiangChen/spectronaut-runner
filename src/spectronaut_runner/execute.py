"""Module for executing Spectronaut in command line mode."""

import logging
import pathlib
import shutil
import subprocess
import time
from typing import Iterable

LOGGER = logging.getLogger(__name__)


def run_spectral_library_generation(
    spectronaut_exec_path: pathlib.Path | str,
    output_dir: pathlib.Path | str,
    search_name: str,
    settings_path: pathlib.Path | str,
    fasta_paths: Iterable[pathlib.Path | str],
    search_settings_path: pathlib.Path | str,
    skip_library_generation: bool = True,  
    htrms_paths: Iterable[pathlib.Path | str] | None = None,
    search_archive_paths: Iterable[pathlib.Path | str] | None = None,
    library_path: pathlib.Path | str | None = None,
    extra_cmd_args: list[str] | None = None,
) -> bool:
    """Generate search archive .psar, .qsp, .final.psar and spectral library .kit
    using run_spectronaut() function.

    Args:
        spectronaut_exec_path: Path to the Spectronaut executable.
        output_dir: Directory where the Spectronaut search results will be saved.
        search_name: Name of the Spectronaut search.
        settings_path: Path to the Spectronaut settings file.
        fasta_paths: Iterable of paths to the FASTA files to be used in the search.
        search_settings_path: Path to the Spectronaut settings file for Pulsar search.
        skip_library_generation: Whether to skip the library generation step.
        htrms_paths: Optional iterable of paths to the .htrms files to be searched. Default is None.
        search_archive_paths: Optional iterable of paths to the pre-existing search archive files. 
            If None, will not consider previous search archives.
        library_path: Optional path to the spectral library file to generate. 
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
        "-rs",
        pathlib.Path(search_settings_path).resolve().as_posix(),
    ])
    if skip_library_generation:
        extra_cmd_args.append("--skip-library-generation") 

    if search_archive_paths is not None:
        for search_archive_path in search_archive_paths:
            extra_cmd_args.extend(["-sa", pathlib.Path(search_archive_path).resolve().as_posix()]) 
    
    if library_path is not None:
        extra_cmd_args.extend(["-k", pathlib.Path(library_path).resolve().as_posix()]) 

    return run_spectronaut(
        spectronaut_exec_path=spectronaut_exec_path,
        output_dir=output_dir,
        search_name=search_name,
        settings_path=settings_path,
        fasta_paths=fasta_paths,
        rawfile_paths=htrms_paths,
        condition_setup_path=None,
        report_schema_paths=None,
        search_type=["-lg", "-se", "Pulsar"],
        extra_cmd_args=extra_cmd_args,
        )


def run_dia_search(
    spectronaut_exec_path: pathlib.Path | str,
    output_dir: pathlib.Path | str,
    search_name: str,
    settings_path: pathlib.Path | str,
    fasta_paths: Iterable[pathlib.Path | str],
    htrms_paths: Iterable[pathlib.Path | str],
    condition_setup_path: pathlib.Path | str,
    library_path: pathlib.Path | str,
    report_schema_paths: Iterable[pathlib.Path | str],
    extra_cmd_args: list[str] | None = None,
) -> bool:
    """DIA library-based search using run_spectronaut() function.

    Args:
        spectronaut_exec_path: Path to the Spectronaut executable.
        output_dir: Directory where the Spectronaut search results will be saved.
        search_name: Name of the Spectronaut search.
        settings_path: Path to the Spectronaut settings file.
        fasta_paths: Iterable of paths to the FASTA files to be used in the search.
        htrms_paths: Iterable of paths to the .htrms files to be searched.
        condition_setup_path: Path to the Spectronaut condition setup file.
        library_path: Path to the spectral library .kit file to use for the search.
        report_schema_paths: Iterable of paths to the report schema files.
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
        pathlib.Path(library_path).resolve().as_posix()
    ])

    return run_spectronaut(
        spectronaut_exec_path=spectronaut_exec_path,
        output_dir=output_dir,
        search_name=search_name,
        settings_path=settings_path,
        fasta_paths=fasta_paths,
        rawfile_paths=htrms_paths,
        condition_setup_path=condition_setup_path,
        search_type=["diaanalysis"],
        report_schema_paths=report_schema_paths,
        extra_cmd_args=extra_cmd_args,
        )

def run_sne_merge(
    spectronaut_exec_path: pathlib.Path | str,
    output_dir: pathlib.Path | str,
    search_name: str,
    sne_paths: Iterable[pathlib.Path | str],
    condition_setup_path: pathlib.Path | str,
    report_schema_paths: Iterable[pathlib.Path | str],
) -> bool:
    """Merge SNE files from the same spectral library into ONE SNE files using run_spectronaut() function, also generate reports.
     Warning! For large experiments, it may exceed the available disk space and RAM.
         Use the combine command instead to generate combined reports WITHOUT generating SNE.
    Args:
        spectronaut_exec_path: Path to the Spectronaut executable.
        output_dir: Directory where the Spectronaut merge results will be saved.
        search_name: Name of the Spectronaut search.
        sne_paths: Iterable of paths to the SNE files to be used in the merge.
        report_schema_paths: Iterable of paths to the report schema files.

    Returns:
        True if the Spectronaut completed successfully, False otherwise.

    Raises:
        FileNotFoundError: If the Spectronaut executable file is not found.
    """

    extra_cmd_args = []
    for sne_path in sne_paths:
        extra_cmd_args.extend(["-sne", pathlib.Path(sne_path).resolve().as_posix()]) 

    return run_spectronaut(
        spectronaut_exec_path=spectronaut_exec_path,
        output_dir=output_dir,
        search_name=search_name,
        search_type=["manageSNE","--merge"],
        extra_cmd_args=extra_cmd_args,
        condition_setup_path=condition_setup_path,
        report_schema_paths=report_schema_paths,
        )

def run_sne_combine(
    spectronaut_exec_path: pathlib.Path | str,
    output_dir: pathlib.Path | str,
    search_name: str,
    sne_paths: Iterable[pathlib.Path | str],
    report_schema_paths: Iterable[pathlib.Path | str],
) -> bool:
    """Combine SNE files from the same spectral library to generate combined reports WITHOUT generating SNE.
    Args:
        spectronaut_exec_path: Path to the Spectronaut executable.
        output_dir: Directory where the Spectronaut combine results will be saved.
        search_name: Name of the Spectronaut search.
        sne_paths: Iterable of paths to the SNE files to be used in the combine.
        report_schema_paths: iterable of paths to the report schema files. 

    Returns:
        True if the Spectronaut completed successfully, False otherwise.

    Raises:
        FileNotFoundError: If the Spectronaut executable file is not found.
    """
    print("\n--- Warning!!!   currently in Spectronaut 20.5 only long format report works, pivot table reports are NOT correct!!!.\n")

    extra_cmd_args = []
    for sne_path in sne_paths:
        extra_cmd_args.extend(["-sne", pathlib.Path(sne_path).resolve().as_posix()]) 

    return run_spectronaut(
        spectronaut_exec_path=spectronaut_exec_path,
        output_dir=output_dir,
        search_name=search_name,
        search_type=["combine"],
        extra_cmd_args=extra_cmd_args,
        report_schema_paths=report_schema_paths
        )

def run_directdia_search(
    spectronaut_exec_path: pathlib.Path | str,
    output_dir: pathlib.Path | str,
    search_name: str,
    settings_path: pathlib.Path | str,
    fasta_paths: Iterable[pathlib.Path | str],
    htrms_paths: Iterable[pathlib.Path | str],
    condition_setup_path: pathlib.Path | str, 
    report_schema_paths: Iterable[pathlib.Path | str],
    extra_cmd_args: list[str] | None = None,
) -> bool:
    """A run_spectronaut() wrapper function to run directDIA+ search.

    Args:
        spectronaut_exec_path: Path to the Spectronaut executable.
        output_dir: Directory where the Spectronaut search results will be saved.
        search_name: Name of the Spectronaut search.
        settings_path: Path to the Spectronaut settings file.
        fasta_paths: Iterable of paths to the FASTA files to be used in the search.
        htrms_paths: Iterable of paths to the .htrms files to be searched.
        condition_setup_path: Path to the Spectronaut condition setup file.
        report_schema_paths: Iterable of paths to the report schema files.
        extra_cmd_args: Optional list of extra command line arguments.

    Returns:
        True if the Spectronaut search completed successfully, False otherwise.

    Raises:
        FileNotFoundError: If the Spectronaut executable file is not found.
    """

    return run_spectronaut(
        spectronaut_exec_path=spectronaut_exec_path,
        output_dir=output_dir,
        search_name=search_name,
        settings_path=settings_path,
        fasta_paths=fasta_paths,
        rawfile_paths=htrms_paths,
        condition_setup_path=condition_setup_path,
        report_schema_paths=report_schema_paths,
        search_type=["-direct"],
        extra_cmd_args=extra_cmd_args,
        )


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

    cmd.extend(["--noOutputSubfolder"]) # this line is added to avoid the nested output folder structure on SN20.5
    
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
