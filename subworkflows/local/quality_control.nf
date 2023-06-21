//
// Verify quality of slides and return mask of regions without artefacts
//

include { HISTOQC   } from '../../modules/local/histoqc'
include { HISTOBLUR } from '../../modules/local/histoblur'
include { MERGE_QC  } from '../../modules/local/merge_qc'

workflow QUALITY_CONTROL {
    take:
    slide

    main:
    HISTOQC(
        slide,
        params.histoqc_config
    )
    HISTOBLUR(
        HISTOQC.out.histoqc_mask,
        params.histoblur_model
    )

    MERGE_QC(
        HISTOBLUR.out.tsv_path.collect(),
        HISTOQC.out.tsv_path.collect(),
        HISTOBLUR.out.blurmask_path.collect()
    )

    emit:
    slide_qc = HISTOBLUR.out.histoblur_binmask
    merged_qc_out = MERGE_QC.out.merged_results
}