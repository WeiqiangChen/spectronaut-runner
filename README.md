# Spectronaut-Runner

## About

A Python library to simplify and support the execution of Spectronaut when running in command-line mode.

**IMPORTANT NOTE**: this library was tested using Spectronaut version >=20.3 in windows operating system, and may not be compatible with other versions, or operating systems. users are recommended to use it at their own risk.

### Example usage

#### install the package

``` bash
uv pip install git+https://github.com/maxperutzlabs-ms/spectronaut-runner.git
```


#### Convert rawfiles to .htrms format.

```python
from spectronaut_runner import convert_to_htrms
convert_to_htrms(
    binary= r"C:\Program Files (x86)\Biognosys\HTRMS Converter\HTRMSConverter.dll",
    source="path/to/rawfiles",
    destination="path/to/htrms"
)
```


#### 5/6-step library-based DIA search for parralel/batch processing.

###### step 1.1 : generate initial search archive from each .htrms files. (parralel/batch processing is optional)

```python
from spectronaut_runner import create_initial_search_archive

create_initial_search_archive(
            spectronaut_exec_path= r"C:\Program Files (x86)\Biognosys\Spectronaut205\bin\Spectronaut.dll",
            output_dir="path/to/output",
            search_settings_path = r"path/to/settings/SN205_Pulsar_search_Settings.prop",
            fastas=[r"path/to/fasta1", r"path/to/fasta2"],
            rawfiles=[r"path/to/raw1", r"path/to/raw2"],
            search_name="Step1.1_generate_initial_search_archive",
        ) 
```

###### step 1.2 : generate models (optimized .qsp files) from all initial search archives.

```python
from spectronaut_runner import create_model_qsp

create_model_qsp(
    spectronaut_exec_path= r"C:\Program Files (x86)\Biognosys\Spectronaut205\bin\Spectronaut.dll",
    output_dir="path/to/output",
    search_settings= r"path/to/settings/SN205_Pulsar_search_Settings.prop",
    search_archives = [r"path/to/psar1", r"path/to/psar2"],
    search_name="Step1.2_generate_model_qsp",
) 
```

###### step 1.3 : generate final search archive from all .htrms, .psar and .qsp files. (parralel/batch processing is optional)

```python
from spectronaut_runner import create_final_search_archive

create_final_search_archive(
    spectronaut_exec_path = r"C:\Program Files (x86)\Biognosys\Spectronaut205\bin\Spectronaut.dll",
    output_dir = "path/to/output",
    rawfiles = [r"path/to/htrms1", r"path/to/htrms2"],
    search_archives = [r"path/to/psar1", r"path/to/psar2"],
    qsp_file = r"path/to/qsp_file",
    search_settings = r"../data/settings/SN205_Library_generation_Settings.prop", 
    search_name = "Step1.3_generate_final_search_archive",
) 
```


###### step 1.4 : generate .kit SL from all FINAL .psar files.

```python
from spectronaut_runner import create_spectral_library

create_spectral_library(
    spectronaut_exec_path= r"C:\Program Files (x86)\Biognosys\Spectronaut205\bin\Spectronaut.dll",
    output_dir= r"path/to/output",
    library_settings=r"../data/settings/SN205_Library_generation_Settings.prop", 
    search_archives = [r"path/to/final_psar1", r"path/to/final_psar2"],
    search_name= r"Step1.4_generate_kit_SL_from_all_final_psar_files",
)
```
###### step 2 : DIA analysis using the library 

###### step 2.1 : generate SNE for each batch of rawfiles or all rawfiles.

```python
from spectronaut_runner import dia_search

dia_search(
    spectronaut_exec_path = r"C:\Program Files (x86)\Biognosys\Spectronaut205\bin\Spectronaut.dll",
    output_dir = r"path/to/output",
    settings = r"../data/settings/SN205_diaAnalysis_noNorm_noPost.prop", 
    rawfiles = [r"path/to/htrms1", r"path/to/htrms2"],
    condition_setup=r"path/to/ConditionSetup.tsv",
    library = r"path/to/output/Step1.4_generate_kit_SL_from_all_final_psar_files.kit",
    report_schemas=[r"path/to/report_scheme1", r"path/to/report_scheme2"],
    write_parquet= True,
    search_name = r"Step2_dia_analysis_using_the_library",
)
```
###### step 2.2 merging .sne files and generate reports (optional if step 2.1 was run in batch and generate multiple .sne files) 

**IMPORTANT**: only SNE files from the same spectral library can be merged.

```python
from spectronaut_runner import sne_merge

sne_merge(
    spectronaut_exec_path= r"C:\Program Files (x86)\Biognosys\Spectronaut205\bin\Spectronaut.dll",
    output_dir= r"path/to/output",
    snes= [r"path/to/sne1", r"path/to/sne2"],
    condition_setup=r"path/to/ConditionSetup.tsv",
    report_schemas=[r"path/to/report_scheme1", r"path/to/report_scheme2"],
    write_parquet= True,
    search_name= r"Step2.2_merging_SNE_files",
)
```
###### step 2.3 combining .sne files and generate reports (optional if step 2.1 was run in batch and generate multiple .sne files) 

**IMPORTANT**: for large experiments (typically greater than 500 samples), merging them may exceed available memory and disk space (could be greater than a terabyte for each). In such a scenario, use the    combine command instead.

```python
from spectronaut_runner import sne_combine

sne_combine(
    spectronaut_exec_path= r"C:\Program Files (x86)\Biognosys\Spectronaut205\bin\Spectronaut.dll",
    output_dir= r"path/to/output",
    snes= [r"path/to/sne1", r"path/to/sne2"],
    report_schemas=[r"path/to/report_scheme1", r"path/to/report_scheme2"], ### ONLY long format report for SN20.5!!! 
    write_parquet= True,
    search_name= r"Step2.3_combining_SNE_files",
)
```


#### 1-step directDIA+ search.

```python
from spectronaut_runner import directdia_search

directdia_search(
    spectronaut_exec_path= r"C:\Program Files (x86)\Biognosys\Spectronaut205\bin\Spectronaut.dll",
    output_dir= r"path/to/output",
    settings=r"../data/settings/SN205_directDIA+_noNorm_noPost.prop",
    fasta= [r"path/to/fasta1", r"path/to/fasta2"],
    rawfiles= [r"path/to/raw1", r"path/to/raw2"],
    condition_setup=r"path/to/ConditionSetup.tsv",
    report_schemas=[r"path/to/report_scheme1", r"path/to/report_scheme2"],
    write_parquet= True,
    search_name= r"1_step_directDIA_plus_search",
)
```
