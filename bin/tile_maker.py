#!/opt/conda/bin/python

import argparse
import os
from pathlib import Path
from typing import NamedTuple
import numpy as np
from WSI_handling import wsi
import openslide
from tqdm import tqdm
import cv2


#### arg class

class Args(NamedTuple):
    """ Command-line arguments """
    slide: str
    mask: str
    outdir: str
    tile_size: int
    mag: float

### parsing args

def get_args() -> Args:
    """Parsing command line arguments"""
    
    parser = argparse.ArgumentParser(
        description='Tile extractor: extracts tiles at requested magnification using binary mask and openslide compatible digital slide',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)


    parser.add_argument('slide',
                        metavar='digital slide',
                        help= 'An openslide compatible digital slide',
                        type=str)

    parser.add_argument('-b',
                        '--mask',
                        metavar='tissue mask',
                        help= 'A binary tissue mask in png format',
                        type=str)

    parser.add_argument('-o',
                        '--outdir',
                        metavar='output directory',
                        help= 'Name of output directory',
                        type=str,
                        default='tiles_extracted')

    parser.add_argument('-t',
                        '--tile_size',
                        metavar='tile size',
                        help='Tile size to extract',
                        type=int,
                        default=2048
                        )

    parser.add_argument('-m',
                        '--mag',
                        metavar='magnification',
                        help='Magnification level at which to extract tiles',
                        type=float,
                        default=20.0)

    args = parser.parse_args()

    return Args(args.slide, args.mask, args.outdir, args.tile_size, args.mag)


#### function to get base magnification of slide
def getMag(osh, slide) -> float:
    """Function that gets base magnification through the openslide metadata"""
    mag = osh.properties.get("openslide.objective-power", "NA")
    if (mag == "NA"):  # openslide doesn't set objective-power for all SVS files: https://github.com/openslide/openslide/issues/247
        mag = osh.properties.get("aperio.AppMag", "NA")
    if (mag == "NA"):
        raise ValueError(f"{slide} - Unknown base magnification for file, please use a WSI with ")
    else:
        mag = float(mag)

    return mag

def main() -> None:
    """where the magic happens"""
    args = get_args()

    osh  = openslide.OpenSlide(args.slide) #open slide
    tile_size = args.tile_size

    #get file basename
    samplebase = os.path.basename(args.slide)
    sample = os.path.splitext(samplebase)[0]

    #create outdir

    Path(f"{args.outdir}/").mkdir(parents=True, exist_ok=True)

    ### get level for requested magnification level
    native_mag = getMag(osh, args.slide)
    targeted_mag = args.mag
    down_factor = native_mag / targeted_mag
    relative_down_factors_idx=[np.isclose(x/down_factor,1,atol=.01) for x in osh.level_downsamples]
    level=np.where(relative_down_factors_idx)[0]

    if level.size:
        level=level[0]

    else:
        level = osh.get_best_level_for_downsample(down_factor)
    
    ## get thumbnail of WSI
    osh_mask  = wsi(args.slide)
    mask_level_tuple = osh_mask.get_layer_for_mpp(8) #get level for 8mpp
    mask_level = mask_level_tuple[0]
    img = osh_mask.read_region((0, 0), mask_level, osh_mask["img_dims"][mask_level]) #read entire image at that level
    
    mask_img=cv2.imread(args.mask, cv2.IMREAD_GRAYSCALE) #read mask
    width = int(img.shape[1])
    height = int(img.shape[0])
    dim = (width, height) #get dimensions of thumbnail
    mask_resize = cv2.resize(mask_img,dim) #resize to thumbnail size
    mask = np.float32(mask_resize)
    mask /= 255 #convert to float 

    ds_mask = osh.level_downsamples[mask_level]
    ds_level = osh.level_downsamples[level]
    t_s_mask = int(tile_size*ds_level//ds_mask)

    for y in tqdm(range(0,osh.level_dimensions[0][1],round(tile_size * osh.level_downsamples[level])), desc="outer"):
        for x in tqdm(range(0,osh.level_dimensions[0][0],round(tile_size * osh.level_downsamples[level])), desc=f"innter {y}", leave=False):

            #if skip
                
                
                
            maskx=int(x//ds_mask)
            masky=int(y//ds_mask)
                
                
            if(maskx >= mask.shape[1] or masky >= mask.shape[0]) or mask[masky:masky+t_s_mask,maskx:maskx+t_s_mask].mean() < 0.8:
                continue

            patch = np.asarray(osh.read_region((x, y), level, (tile_size,tile_size)))[:,:,0:3]
            patch=cv2.cvtColor(patch,cv2.COLOR_RGB2BGR)
            cv2.imwrite(f"{args.outdir}/{sample}_{level}_{y}_{x}.png", patch)
    

    print(f"Done making patches!")

if __name__ == "__main__":
    
    main()