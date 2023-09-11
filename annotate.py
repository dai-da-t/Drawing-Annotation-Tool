import argparse
import glob
import os
from typing import Optional, Tuple

import cv2
import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Annotation Tool")
    parser.add_argument(
        "--img_dir",
        default="images",
        help="Directory containing the images to be annotated.",
    )
    parser.add_argument(
        "--save_dir", default="outputs", help="Directory to save the annotated masks."
    )
    return parser.parse_args()


class AnnotationTool:
    def __init__(self, img_dir: str, save_dir: Optional[str] = None):
        """
        Initialize the Annotation Tool.

        Args:
            img_dir (str): Directory containing the images to be annotated.
            save_dir (Optional[str], optional): Directory to save the annotated masks. Defaults to None.
        """
        self.img_dir = img_dir
        self.img_files = sorted(
            glob.glob(os.path.join(img_dir, "*.[jJ][pP][gG]"))
            + glob.glob(os.path.join(img_dir, "*.[jJ][pP][eE][gG]"))
            + glob.glob(os.path.join(img_dir, "*.[pP][nN][gG]"))
        )

        self.save_dir = save_dir if save_dir else img_dir
        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)

        self.index = 0
        self.mask = None
        self.drawing = False
        self.brush_size = 5
        self.eraser_mode = False

        self.initialize_mask()

    def initialize_mask(self) -> None:
        """Initialize the annotation mask."""
        image_fname = os.path.basename(self.img_files[self.index])
        mask_name = os.path.splitext(image_fname)[0] + ".npy"
        self.mask_path = os.path.join(self.save_dir, mask_name)

        if os.path.exists(self.mask_path):
            binary_mask = np.load(self.mask_path)
            # Convert 1-channel binary mask to 3-channel mask for display
            self.mask = np.stack([binary_mask] * 3, axis=-1) * 255
        else:
            # If no .npy file exists, initialize the mask with zeros
            first_img = cv2.imread(self.img_files[self.index])
            self.mask = np.zeros(first_img.shape, np.uint8)

    def draw_mask(self, event: int, x: int, y: int, flags: int, param: Tuple) -> None:
        """
        Draw the annotation mask based on mouse events.

        Args:
            event (int): OpenCV event type.
            x (int): x-coordinate of the mouse event.
            y (int): y-coordinate of the mouse event.
            flags (int): OpenCV event flags.
            param (Tuple): Additional parameters.
        """
        self.brush_size = cv2.getTrackbarPos("Brush Size", "Annotation Tool")
        color = (0, 0, 0) if self.eraser_mode else (255, 255, 255)

        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            cv2.circle(self.mask, (x, y), self.brush_size, color, -1)
            self.update_window()

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                cv2.circle(self.mask, (x, y), self.brush_size, color, -1)
                self.update_window()

    def update_window(self) -> None:
        """Update the annotation window with the current image and overlay."""
        img = cv2.imread(self.img_files[self.index])
        overlay = img.copy()
        cv2.addWeighted(overlay, 0.7, self.mask, 0.3, 0, img)

        # Create a larger background image with extra space at the bottom for the filename
        extra_space = 30
        background = np.zeros(
            (img.shape[0] + extra_space, img.shape[1], 3), dtype=np.uint8
        )
        background[: img.shape[0], :] = img

        font = cv2.FONT_HERSHEY_SIMPLEX
        text_position = (10, img.shape[0] + 20)
        color = (255, 255, 255)
        cv2.putText(
            background,
            self.img_files[self.index],
            text_position,
            font,
            0.8,
            color,
            1,
            cv2.LINE_AA,
        )

        cv2.imshow("Annotation Tool", background)

    def save_mask(self) -> None:
        """Save the current mask as a .npy file."""
        gray_mask = cv2.cvtColor(self.mask, cv2.COLOR_BGR2GRAY)
        binary_mask = np.where(gray_mask > 0, 1, 0).astype(np.uint8)
        np.save(self.mask_path, binary_mask)

    def set_brush_size(self, size: int) -> None:
        """
        Set the brush size for drawing.

        Args:
            size (int): Desired brush size.
        """
        self.brush_size = size

    def main(self) -> None:
        """Main loop for the annotation tool."""
        while True:
            cv2.namedWindow("Annotation Tool")
            cv2.createTrackbar(
                "Brush Size",
                "Annotation Tool",
                self.brush_size,
                50,
                self.set_brush_size,
            )
            cv2.setMouseCallback("Annotation Tool", self.draw_mask)
            self.update_window()
            key = cv2.waitKey(0)

            if key in [27, ord("q")]:  # Exit the tool
                break
            elif key in [ord("a"), ord("d")]:  # Move to the previous or next image
                self.save_mask()
                self.index = (
                    (self.index - 1) % len(self.img_files)
                    if key == ord("a")
                    else (self.index + 1) % len(self.img_files)
                )
                self.initialize_mask()

            elif key == ord("e"):  # Toggle eraser mode
                self.eraser_mode = not self.eraser_mode
            elif key == ord("r"):  # Reset the mask
                self.mask.fill(0)
                self.update_window()

            cv2.destroyAllWindows()


if __name__ == "__main__":
    args = parse_args()

    if not os.path.isdir(args.img_dir):
        print(f"Error: Specified directory '{args.img_dir}' does not exist.")
        exit()

    message = """
    ==============================
        ANNOTATION TOOL
    ==============================

    Description:
    This tool allows you to annotate images with drawing. Use your mouse to draw and the provided key commands to navigate.

    Key Operations:
    - a: Move to the previous image
    - d: Move to the next image
    - e: Toggle eraser mode
    - r: Reset the mask
    - q or ESC: Exit the tool
    """
    print(message)

    tool = AnnotationTool(args.img_dir, save_dir=args.save_dir)
    tool.main()
