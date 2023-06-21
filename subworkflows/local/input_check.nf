//
// Check input samplesheet and get read channels
//

include { SAMPLESHEET_CHECK } from '../../modules/local/samplesheet_check'

workflow INPUT_CHECK {

    take:
    samplesheet // file: /path/to/samplesheet.csv

    main:
    SAMPLESHEET_CHECK ( samplesheet )
        .csv
        .splitCsv ( header: true, sep: ',' )
        .map { create_slide_channels(it) }
        .set { slide }

    emit:
    slide                                     // channel: [ val(meta), [ slide_path ] ]
    
}

// Function to get list of [ meta, [ tissue_positions_list, tissue_hires_image, \
// scale_factors, barcodes, features, matrix ] ]
def create_slide_channels(LinkedHashMap row) {
    def meta = [:]
    meta.id           = row.slide_name
    meta.stain        = row.stain
    meta.basename     = row.basename

    def array = []
    if (!file(row.filedir).exists()) {
        exit 1, "ERROR: Please check input samplesheet -> slide directory does not exist!\n${row.filedir}"
    }
    if (!file(row.filename).exists()) {
        exit 1, "ERROR: Please check input samplesheet -> slide filename does not exist!\n${row.filename}"
    }
    array = [ meta,
        file(row.filename),
        file(row.filedir),
    ]
    return array
}