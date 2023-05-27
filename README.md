# COCO-Annotation-Mask-Generator
Python script generates colored masks from COCO-style annotations. It reads the COCO annotation files, creates masks for each annotation, colors the masks based on the annotation's category, and saves the colored masks as images. The script is designed to handle multiple categories and can be easily extended to support more categories if needed.

Features:
Supports multiple categories with different colors for each category.
Processes images in parallel using multiple workers to speed up the mask generation.
Handles errors gracefully and skips over images or annotations that cause problems.
Outputs colored masks as PNG images.

Usage:
To run this script, you need to provide three positional arguments: 
coco_dir, image_dir, and output_dir. Additionally, you can provide an optional argument --num-workers 
to specify the number of parallel workers for processing images.

Here is an example of how to run this script from the command line:
python3 mask_generator.py /path/to/coco_dir /path/to/image_dir /path/to/output_dir --num-workers 4

Replace mask_generator.py with the name of your Python script, and replace /path/to/coco_dir, /path/to/image_dir, and /path/to/output_dir with the actual paths to your COCO annotations directory, image directory, and output directory, respectively. The --num-workers 4 part is optional and specifies that 4 workers should be used for parallel processing. If you don't provide this argument, the script will use 4 workers by default.

Requirements:
Python 3,
OpenCV,
NumPy,
pycocotools,
You can install the required Python packages using pip:
pip install opencv-python numpy pycocotools

Limitations:
This script assumes that the COCO annotations are correct and complete. If there are errors or missing data in the annotations, the script may not generate the masks correctly.


Generating COCO Files and Adding Annotations Using makesense.ai
makesense.ai is an online tool that allows you to easily add annotations to your images and export them in various formats, including COCO JSON format.

Here are the steps to generate COCO files and add annotations to your images using makesense.ai:

1. Upload Your Images
Go to makesense.ai.
Click on the + Select Images button.
Select the images you want to annotate and click Open.

2. Label Your Images
Click on the + Add new label button to create a new label.
Enter the name of the label and click Add.
Repeat this process for all the labels you need.
To label an image, select the label you want to use, then click and drag on the image to create a bounding box or polygon around the object you want to label.
Repeat this process for all the objects you want to label in each image.

3. Export Your Annotations
Once you've labeled all your images, click on the Export button in the top right corner.
Select COCO (JSON) as the export format.
Click on the Download button to download your annotations in COCO JSON format.

4. Use the COCO JSON File
The downloaded COCO JSON file can be used directly with the Python script provided in this repository. Just specify the path to the COCO JSON file when running the script.

Please note that makesense.ai is a third-party tool, and its interface or functionality may change over time. If you encounter any issues or have any questions about using makesense.ai, please refer to their official documentation or contact their support.
