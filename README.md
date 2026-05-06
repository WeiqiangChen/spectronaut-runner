# Spectronaut-Runner

## About

A Python library to simplify and support the execution of Spectronaut when running in command-line mode.

### Example usage

#### install the package

``` bash
uv pip install git+https://github.com/maxperutzlabs-ms/spectronaut-runner.git
```


#### Convert rawfiles to .htrms format.

```python
from spectronaut_runner import convert_to_htrms
convert_to_htrms(
    binary= r"C:\Program Files (x86)\Biognosys\HTRMS Converter\HTRMSConverter.exe",
    source="path/to/rawfiles",
    destination="path/to/htrms"
)
```


#### 5/6-step library-based DIA search for parralel/batch processing.

###### step 1.1 : generate spectral library from each .htrms files. (parralel/batch processing is optional)

```python
from spectronaut_runner import run_spectral_library_generation

run_spectral_library_generation(
            spectronaut_exec_path= r"C:\Program Files (x86)\Biognosys\Spectronaut205\bin\Spectronaut.exe",
            output_dir="path/to/output",
            search_name="Step1.1_generate_spectral_lib_from_each_htrms",
            settings_path=r"../data/settings/SN205_Library_generation_Settings.prop", 
            fasta_paths=[r"path/to/fasta1", r"path/to/fasta2"],
            htrms_paths=[r"path/to/htrms1", r"path/to/htrms2"],
            search_settings_path = r"path/to/settings/SN205_Pulsar_search_Settings.prop",
            skip_library_generation = True,
            extra_cmd_args = ["--pulsarStage", "pulsarStep1"],
        ) 
```

###### step 1.2 : generate .qsp files from all .psar files.

```python
from spectronaut_runner import run_spectral_library_generation

run_spectral_library_generation(
    spectronaut_exec_path = r"C:\Program Files (x86)\Biognosys\Spectronaut205\bin\Spectronaut.exe",
    output_dir = "path/to/output",
    search_name = "Step1.2_generate_qsp_from_all_psar_files",
    settings_path = r"../data/settings/SN205_Library_generation_Settings.prop", 
    fasta_paths = [r"path/to/fasta1", r"path/to/fasta2"],
    htrms_paths = None,
    search_settings_path = r"../data/settings/SN205_Pulsar_search_Settings.prop",
    search_archive_paths = [r"path/to/psar1", r"path/to/psar2"],
    skip_library_generation = False,
    extra_cmd_args = ["--pulsarStage", "pulsarStep2"],
) 
```

###### step 1.3 : generate final .psar files using all .htrms, .psar and .qsp files. (parralel/batch processing is optional)

```python
from spectronaut_runner import run_spectral_library_generation

run_spectral_library_generation(
    spectronaut_exec_path = r"C:\Program Files (x86)\Biognosys\Spectronaut205\bin\Spectronaut.exe",
    output_dir = "path/to/output",
    search_name = "Step1.3_generate_final_psar_files_using_all_htrms_psar_and_qsp_files",
    settings_path = r"../data/settings/SN205_Library_generation_Settings.prop", 
    fasta_paths = [r"path/to/fasta1", r"path/to/fasta2"],
    htrms_paths = [r"path/to/htrms1", r"path/to/htrms2"],
    search_settings_path = r"../data/settings/SN205_Pulsar_search_Settings.prop",
    search_archive_paths = [r"path/to/psar1", r"path/to/psar2"],
    skip_library_generation = True,
    extra_cmd_args = ["--pulsarStage", "pulsarStep3", "--optimizedModels", r"path/to/qsp_file"],
) 
```
###### step 1.4 : enerate .kit SL from all FINAL .psar files.

```python
from spectronaut_runner import run_spectral_library_generation

run_spectral_library_generation(
    spectronaut_exec_path= r"C:\Program Files (x86)\Biognosys\Spectronaut205\bin\Spectronaut.exe",
    output_dir= r"path/to/output",
    search_name= r"Step1.4_generate_kit_SL_from_all_final_psar_files",
    settings_path=r"../data/settings/SN205_Library_generation_Settings.prop", 
    fasta_paths= [r"path/to/fasta1", r"path/to/fasta2"],
    htrms_paths=None,
    search_settings_path = r"../data/settings/SN205_Pulsar_search_Settings.prop",
    skip_library_generation = False,  
    search_archive_paths = [r"path/to/final_psar1", r"path/to/final_psar2"],
    library_path = r"path/to/output/Step1.4_generate_kit_SL_from_all_final_psar_files.kit"
)
```
###### step 2 : DIA analysis using the library 

###### step 2.1 : generate SNE for each batch or all at once.

```python
from spectronaut_runner import run_dia_search

run_dia_search(
    spectronaut_exec_path = r"C:\Program Files (x86)\Biognosys\Spectronaut205\bin\Spectronaut.exe",
    output_dir = r"path/to/output",
    search_name = r"Step2_dia_analysis_using_the_library",
    settings_path = r"../data/settings/SN205_diaAnalysis_noNorm_noPost.prop", 
    fasta_paths = [r"path/to/fasta1", r"path/to/fasta2"],
    htrms_paths = [r"path/to/htrms1", r"path/to/htrms2"],
    condition_setup_path=r"path/to/ConditionSetup.tsv",
    library_path = r"path/to/output/Step1.4_generate_kit_SL_from_all_final_psar_files.kit",
    report_schema_paths=[r"path/to/report_scheme1", r"path/to/report_scheme2"],
)
```
###### step 2.2 combining .sne files and generate reports (optional if step 2.1 was run in batch and generate multiple .sne files)

```python
from spectronaut_runner import run_combine_sne_files

run_combine_sne_files(
# to be implemented in execute.py
)
```


#### 1-step directDIA+ search.

```python
from spectronaut_runner import run_directdia_search

run_directdia_search(
    spectronaut_exec_path= r"C:\Program Files (x86)\Biognosys\Spectronaut205\bin\Spectronaut.exe",
    output_dir= r"path/to/output",
    search_name= r"1_step_directDIA_plus_search",
    settings_path=r"../data/settings/SN205_diaAnalysis_noNorm_noPost.prop",
    fasta_paths= [r"path/to/fasta1", r"path/to/fasta2"],
    htrms_paths= [r"path/to/htrms1", r"path/to/htrms2"],
    condition_setup_path=r"path/to/ConditionSetup.tsv",
    report_schema_paths=[r"path/to/report_scheme1", r"path/to/report_scheme2"],
)
```
