"""Module for converting rawfiles to htrms using Spectronaut in command line mode.

TODO:
    - Check if the htrms files already exist and skip conversion if so.
    - Allow optional command to overwrite existing .htrms files.
"""

import logging
import pathlib
import subprocess
import time

LOGGER = logging.getLogger(__name__)


def convert_to_htrms(
    binary: pathlib.Path | str,
    source: pathlib.Path | str,
    destination: pathlib.Path | str | None = None,
    verbose: bool = False,
) -> bool:
    """Convert rawfiles to .htrms format using Spectronaut's command line interface.

    Note that to use Spectronaut for conversion, the Spectronaut license must be
    activated on the machine where the conversion is performed. If this is not the case,
    the conversion will simply not happen but not error will be raised.

    Args:
        binary: Path to the EXE or DLL of either the HTRMSconverter or Spectronaut,
            which will be used to perform the conversion.
        source: Path to the source directory containing rawfiles to convert.
        destination: Optional path to the destination directory where converted
            .htrms files will be saved. If None, files will be saved in the source
            directory.
        verbose: Whether to enable logging of the converter output. This works only if
            the DLL is used for conversion and not the EXE. Default is False.

    Returns:
        True if the conversion completed successfully, False otherwise.

    Raises:
        FileNotFoundError: If the Spectronaut executable file or source directory is
            not found.
    """
    allowed_binaries = [
        "spectronaut",
        "spectronaut.exe",
        "spectronaut.dll",
        "htrmsconverter.exe",
        "htrmsconverter.dll",
    ]

    binary_path = pathlib.Path(binary)
    if not binary_path.exists():
        raise FileNotFoundError(
            f"Binary file not found at {binary_path}. Please check the path."
        )
    if binary_path.name.lower() not in allowed_binaries:
        raise ValueError(
            f"Invalid binary '{binary_path.name}'. Must be one of: "
            f"{', '.join(allowed_binaries)}"
        )

    source_path = pathlib.Path(source)
    if not source_path.exists():
        raise FileNotFoundError(f"Source directory '{source}' does not exist.")

    if destination is None:
        if source_path.is_dir():
            destination_path = source_path
        else:
            destination_path = source_path.parent
    else:
        destination_path = pathlib.Path(destination)

    if binary_path.suffix.lower() == ".dll":
        cmd = ["dotnet"]
    else:
        cmd = []
    cmd.extend(
        [
            binary_path.resolve().as_posix(),
            "-convert",
            "-i",
            source_path.resolve().as_posix(),
            "-o",
            destination_path.resolve().as_posix(),
        ]
    )
    if binary_path.name.lower().startswith("htrmsconverter"):
        cmd.append("-nogui")

    LOGGER.info(f"Converting '{source_path}' to .htrms format.")
    LOGGER.debug(f"HTRMS conversion command: {' '.join(cmd)}")
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
        if verbose and result.stdout:
            LOGGER.debug(result.stdout.strip())
        LOGGER.info(f"HTRMS conversion completed in {duration:.2f} minutes.")
        return True
    except subprocess.CalledProcessError as e:
        LOGGER.error(
            f"Error running HTRMS conversion: {e}\n"
            f"Exit Code: {e.returncode}\n"
            f"STDOUT (if available):\n{e.stdout.strip() if e.stdout else 'N/A'}\n"
            f"STDERR:\n{e.stderr.strip()}"
        )
        return False
