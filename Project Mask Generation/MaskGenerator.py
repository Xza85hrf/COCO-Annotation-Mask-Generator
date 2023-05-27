#!/usr/bin/python3
import argparse
import glob
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import cv2
import numpy as np
from pycocotools.coco import COCO

# define a mapping from category to color
CATEGORY_COLORS = {
    1: [255, 0, 0],  # NonMaskingBackground - Blue
    2: [0, 255, 0],  # MaskingBackground - Green
    3: [0, 0, 255],  # Animal - Red
    4: [255, 255, 255],  # NonMaskingForegroundAttention - White
    # add more categories if needed
}


def generate_masks(coco_file, image_dir, output_dir):
    try:
        coco = COCO(coco_file)

        # get all images
        img_ids = coco.getImgIds()
        images = coco.loadImgs(img_ids)

        # get all unique category IDs in the annotations
        cat_ids = coco.getCatIds()
        print(f"Unique category IDs in annotations: {cat_ids}")

        for image_info in images:
            # check if image exists
            image_path = Path(image_dir) / image_info['file_name']
            if not image_path.exists():
                print(f"Image '{image_path}' does not exist - skipping")
                continue

            # load image
            image = cv2.imread(str(image_path))

            if image is None:
                print(f"Failed to load '{image_path}' - skipping")
                continue

            # create mask
            mask = np.zeros((image_info["height"], image_info["width"], 3), dtype=np.uint8)

            # get annotation ids for the current image
            ann_ids = coco.getAnnIds(imgIds=image_info['id'])
            annotations = coco.loadAnns(ann_ids)

            # sort annotations by area (smaller annotations last)
            annotations.sort(key=lambda ann: coco.imgs[ann['image_id']]['height'] * coco.imgs[ann['image_id']]['width'])

            for annotation in annotations:
                # check if the annotation category is in the category-color mapping
                if annotation['category_id'] not in CATEGORY_COLORS:
                    print(f"Category ID {annotation['category_id']} not known - skipping annotation!")
                    continue

                # create a mask for the current annotation
                ann_mask = coco.annToMask(annotation)

                if not np.any(ann_mask):  # skip if the mask is empty
                    continue

                # color the mask
                colored_ann_mask = np.zeros((image_info["height"], image_info["width"], 3), dtype=np.uint8)
                colored_ann_mask[ann_mask > 0] = CATEGORY_COLORS[annotation['category_id']]

                # only apply the colored mask if the corresponding area in the combined mask has not been colored yet
                mask_to_apply = np.zeros((image_info["height"], image_info["width"], 3), dtype=np.uint8)
                mask_to_apply[(ann_mask > 0) & (mask == [0, 0, 0]).all(axis=2)] = colored_ann_mask[
                    (ann_mask > 0) & (mask == [0, 0, 0]).all(axis=2)]

                # combine the masks
                mask = cv2.bitwise_or(mask, mask_to_apply)

            # save the mask
            mask_output_path = Path(output_dir) / f"{Path(image_info['file_name']).stem}_mask.png"
            cv2.imwrite(str(mask_output_path), mask)

    except FileNotFoundError as e:
        print(f"Failed to process due to missing file: {str(e)}")
    except Exception as e:
        print(f"Failed to process {coco_file} due to error: {str(e)}")


def process_all_coco_files(coco_dir, image_dir, output_dir, num_workers):
    # find all json files in the coco directory
    coco_files = glob.glob(str(Path(coco_dir) / '*.json'))

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        for coco_file in coco_files:
            executor.submit(generate_masks, coco_file, image_dir, output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate masks from COCO annotations.')
    parser.add_argument('coco_dir', help='Directory containing COCO annotation files.')
    parser.add_argument('image_dir', help='Directory containing image files.')
    parser.add_argument('output_dir', help='Directory to output the generated mask images.')
    parser.add_argument('--num-workers', type=int, default=4, help='Number of parallel workers for processing images.')
    args = parser.parse_args()

    # check if the directories exist
    if not Path(args.coco_dir).exists():
        print(f"COCO directory {args.coco_dir} does not exist!")
        exit(1)
    if not Path(args.image_dir).exists():
        print(f"Image directory {args.image_dir} does not exist!")
        exit(1)
    if not Path(args.output_dir).exists():
        print(f"Output directory {args.output_dir} does not exist!")
        exit(1)

    process_all_coco_files(args.coco_dir, args.image_dir, args.output_dir, args.num_workers)

#How to run the code -
#python3 your_script.py "/path/to/coco_dir" "/path/to/image_dir" "/path/to/output_dir" --num-workers 4

#num-workers 4 - how many processor cores to utilize