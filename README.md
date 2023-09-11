# Drawing Annotation Tool

An interactive image annotation tool using OpenCV that allows users to draw and annotate images.

## Features

-   Navigate between images with keyboard shortcuts.
-   Draw annotations using the mouse.
-   Toggle eraser mode to remove annotations.
-   Save annotations in `.npy` format.
-   Display the current image name on the annotation window.

## Installation

Ensure you have `Python` and `pip` installed. Then, install the required packages:

```bash
pip install opencv-python numpy
```

### Using Poetry

If you are using `poetry` for dependency management, you can set up the environment with:

```bash
poetry install
```

This will create a virtual environment and install the necessary dependencies.

## Usage

Run the annotation tool with:

```bash
python annotation_tool.py --img_dir [IMAGE_DIRECTORY] --save_dir [SAVE_DIRECTORY]
```

Optional arguments:

-   `--img_dir`: Directory containing the images to be annotated. Default is `images`.
-   `--save_dir`: Directory to save the annotated masks. Default is `outputs`.

### Key Operations

-   `a`: Move to the previous image.
-   `d`: Move to the next image.
-   `e`: Toggle eraser mode.
-   `r`: Reset the mask.
-   `q` or `ESC`: Exit the tool.
