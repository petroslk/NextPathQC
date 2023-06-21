process MERGE_QC{
    
    label 'process_single'

    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/python:3.8.3' :
        'quay.io/biocontainers/python:3.8.3' }"

    publishDir "${params.outdir}/final_QC_results", mode: 'copy'

    input:
    path(histoblur_csvs)
    path(histoqc_csvs)
    path(masks_to_use)

    output:
    path("./merged_histoblur_metrics.csv"), emit: merged_csv_histoblur
    path("./merged_histoqc_metrics.tsv"), emit: merged_tsv_histoqc
    path("./masks_to_use"), emit: merged_results

    shell:
    
    '''
    touch merged_histoblur_metrics.csv merged_histoqc_metrics.tsv

    echo " ,total_blurry_perc,mildly_blurry_perc,highly_blurry_perc,70_perc_white,50_perc_white,30_perc_white,10_perc_white,patch_size_used,native_magnification_level,blur_detection_magnification,npixels_at_8μpp,processing_time,file_path" > merged_histoblur_metrics.csv

    for file in !{histoblur_csvs}
    do
        tail -n +2 $file >> merged_histoblur_metrics.csv
    done

    is_first_file=true

    for file in !{histoqc_csvs}
    do
    if $is_first_file ; then
        # If it's the first file, get all the first 7 lines (metadata + header)
        head -7 $file > merged_histoqc_metrics.tsv
        is_first_file=false
    else
        # If it's not the first file, only get the 7th line (header)
        sed -n '7p' $file >> merged_histoqc_metrics.tsv
    fi
    done

    mkdir masks_to_use
    cp !{masks_to_use} masks_to_use/
    '''
}