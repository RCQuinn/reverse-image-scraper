# Reverse Image Scraper
Google has this neat feature for uploading images. <br>
This program automates the majority of this process, returning larger images from a folder the user adds to. There is still a manual component as Google's reverse image searching process itself isn't perfect. The returned images are all saved to an output folder for manual sorting.
<br>
## Setup
To setup and install dependencies run the command line: `pip3.8 install -r requirements.txt`

## Using the program
The program three main modes that can be accessed through the command line. As the program is set up as a module, these commands should be run from the program's root directory (where this README is located).
<br>
#### Main Usage
`python -m reverse-image-scraper` <br>
The default usage of this program is to find and return larger images using multi-processing. When running this command for the first time an "input" and "output" folder will be created and the program will complain the input folder is empty. Put the images you want to search with in the "input" folder and run the command again. <br>
<i>Note</i> that subdirectories in the "input" folder are not searched. <br>
<br>
Your images will be moved from the "input" folder to the "output" folder as each search is completed. <br>
If larger images are found, a directory of the same name is created in the "output" folder containing the original image as well as any copies. If no larger images are found, the original image is moved to "(-) Default Results", contained within the "output" folder. <br>
<br>
The program can also be run with `python -m reverse-image-scraper single` to run without multi-processing.

#### Secondary Usage
`python -m reverse_image_scraper extract` <br>
This command searches through all the subdirectories in the "output" folder for directories with a single file. It moves all these files to the "(-) Default Results" folder. <br>
This is mainly a quality of life feature so when you have chosen which one of the returned images are suitable for keeping, you don't have to keep track of which folders you have searched through.

#### Testing Usage
`python -m reverse_image_scraper debug`
Runs test files.
