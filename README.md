## NextPathQC: a simple Nextflow pipeline for Digital Pathology Quality Control

This small nextflow pipeline is intended to combine tools, provide an easy containerized wrapper and computational resource management for QC of digital pathology Whole Slide Images.

The pipeline performs the following steps:

First Quality Control using [HistoQC](https://github.com/choosehappy/HistoQC)

Blur detection using [HistoBlur](https://github.com/choosehappy/HistoBlur)

Returns a directory with all binary masks without artefacts and two tsv files, one containing the blur metrics for each slide and one containing the HistoQC metrics

The binary masks can be used in downstream analysis to exclude regions with artefacts. The tsv files can be used to identify problematic slides.

We recommend you read into the two tools individually to understand their use

# Requirement

Nvidia GPU with vram > 10Gb

# Installation
To install the necessary dependencies, the use of anaconda is highly recommended.
The only necessary dependencies to run this pipeline are:

Nextflow,
Docker,
CUDA drivers for GPU support,
Nvidia Docker



Alternatively, singularity can also be used.

Using conda, these tools can be installed as follows:

```
conda create --name NextPathQC
conda activate NextPathQC
conda install -c bioconda nextflow
```

Once nextflow has been installed, make sure to update to the latest version:

```
nextflow self-update
```


This installation command assumes that you have Nvidia docker and CUDA [installed](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

Alternatively, you can also use the singularity container engine (CUDA also required)

```
conda install -c conda-forge singularity
```

# Preparation

Before running the pipeline you need to edit the sample sheet and add the information in the corresponding columns.
The last column is mrxs file specific and requires the data directory of the mrxs slide. For non mrxs files, you can simply add the
path to the directory where the slides are located.

For an mrxs file the sample sheet will look something like this:
```
test_mrxs,      H&E,       basename.mrxs,       /path/to/mrxs/basename.mrxs,        /path/to/mrxs/basename/
```
For other files the sample sheet will look something like this:
```
test_svs,       H&E,       basename.svs,       /path/to/svs/basename.svs,        /path/to/svs/
```

We recommend training a HistoBlur model for your specific H&E type by following the tutorial available [here](histoblur.com)

For testing purposes, a HistoBlur model has also been provided in the assests subdirectory of this pipeline

The config file for HistoQC is also provided in the assests subdirectory of this pipeline and can be edited by the user.

Then, you will need to adjust the paths to the model and config file accordingly in the *nextflow.config* file.

You can also adjust the resource to use for the analysis accordingly in the "Max resource options"

# Usage

To run the pipeline, you can use the following command:

For help menu

```
nextflow run main.nf --help
```

With Docker

```
nextflow run main.nf --input sample_sheet.csv --outdir qc_results -profile docker
```

With singularity

```
nextflow run main.nf --input sample_sheet.csv --outdir qc_results -profile singularity
```

