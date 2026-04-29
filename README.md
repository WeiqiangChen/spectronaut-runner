# Spectronaut-Runner

## About

A Python library to simplify and support the execution of Spectronaut when running in command-line mode.

### Example usage

Convert rawfiles to .htrms format using Spectronaut's command line interface:

```python
from spectronaut_runner import convert_to_htrms

rawfile_folder = '../data/raw'
htrms_folder = "../data/htrms"

convert_to_htrms(
    binary=r"C:\Program Files (x86)\Biognosys\HTRMS Converter\HTRMSConverter.exe",
    source=rawfile_folder,
    destination=htrms_folder,
    verbose=False,
)
```

### 5-step search using Spectronaut's command line interface:
#### 3-step.1/3: Build search archive from htrms (skip library generation):

```python
from spectronaut_runner import generate_search_archive

fasta_folder = '../data/fasta'
output_folder = "../data/processed"
report_scheme_folder = "../data/report"

def get_files(folder, tag):
    return [str(f) for f in pathlib.Path(folder).glob(f"*{tag}") ] 

fasta_files = get_files(fasta_folder, ".fasta")
htrms_files = get_files(htrms_folder,".htrms")
report_scheme_files = get_files(report_scheme_folder,".rs")

search_name = "generate_search_archive"
generate_search_archive(
    spectronaut_exec_path= r"C:\Program Files (x86)\Biognosys\Spectronaut205\bin\Spectronaut.exe",
    output_dir=f"{output_folder}/{search_name}",
    search_name=search_name,
    settings_path=r"../data/settings/SN205_Library_generation_Settings.prop", 
    fasta_paths=fasta_files,
    htrms_paths=[htrms_files[0]],
    search_settings_path = r"../data/settings/SN205_Pulsar_search_Settings.prop",
    skip_library_generation = True,  
) 
```
#### 3-step.2/3: Build spectral library from htrms and search archives:

```python
search_name = "generate_spectral_library"
search_archive_paths ="../data/processed/generate_search_archive"
search_archive_files = get_files(search_archive_paths,".psar")

generate_search_archive(
    spectronaut_exec_path= r"C:\Program Files (x86)\Biognosys\Spectronaut205\bin\Spectronaut.exe",
    output_dir=f"{output_folder}/{search_name}",
    search_name=search_name,
    settings_path=r"../data/settings/SN205_Library_generation_Settings.prop", 
    fasta_paths=fasta_files,
    htrms_paths=[htrms_files[1]],
    search_settings_path = r"../data/settings/SN205_Pulsar_search_Settings.prop",
    skip_library_generation = False,  
    search_archive_paths = search_archive_files,
    library_path = f"{output_folder}/{search_name}.kit"
)  

```
#### 3-step.3/3: DIA search from htrms and spectral library .kit:

```python
from spectronaut_runner import dia_search
search_name = "diaSearch_library_based"
dia_search(
    spectronaut_exec_path = r"C:\Program Files (x86)\Biognosys\Spectronaut205\bin\Spectronaut.exe",
    output_dir = f"{output_folder}/{search_name}",
    search_name = search_name,
    settings_path = r"../data/settings/SN205_diaAnalysis_noNorm_noPost.prop", 
    fasta_paths = fasta_files,
    htrms_paths = htrms_files,
    condition_setup_path=r"../data/20260420-test_ConditionSetup.tsv",
    library_path = "../data/processed/generate_spectral_library.kit",
    report_schema_paths=report_scheme_files,
)

```


### 1-step directDIA+ search using Spectronaut's command line interface:

```python
from spectronaut_runner import run_spectronaut
search_name = "directDIA_search_test_1htrms"
run_spectronaut(
        spectronaut_exec_path= r"C:\Program Files (x86)\Biognosys\Spectronaut205\bin\Spectronaut.exe",
        output_dir=f"{output_folder}/{search_name}",
        search_name=search_name,
        settings_path=r"../data/settings/SN205_directDIA+_noNorm_noPost.prop",
        fasta_paths=fasta_files,
        rawfile_paths=[htrms_files[1]],
        condition_setup_path=r"../data/20260420-test_ConditionSetup.tsv",
        report_schema_paths=report_scheme_files,
        search_type=["-direct"],
    )
```