"""
6.1010 Spring '23 Lab 1: Image Processing
"""

#!/usr/bin/env python3

import math

from PIL import Image

# NO ADDITIONAL IMPORTS ALLOWED!


def get_pixel(image, row, col):
    width = image["width"]
    return image["pixels"][row * width + col]


def set_pixel(image, row, col, color):
    width = image["width"]
    image["pixels"][row * width + col] = color


def apply_per_pixel(image, func):
    """
    Takes image and function as input. Applies function on each pixel in image,
    returning result as output
    """
    height = image["height"]
    width = image["width"]
    result = {
        "height": height,
        "width": width,
        "pixels": [0] * height * width,
    }
    for row in range(height):
        for col in range(width):
            color = get_pixel(image, row, col)
            new_color = func(color)
            set_pixel(result, row, col, new_color)
    return result


def inverted(image):
    return apply_per_pixel(image, lambda color: 255 - color)


# HELPER FUNCTIONS


def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings "zero", "extend", or "wrap",
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of "zero", "extend", or "wrap", return
    None.

    Otherwise, the output of this function should have the same form as a 6.101
    image (a dictionary with "height", "width", and "pixels" keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE
    Kernel represented as list of lists, with each row as a list.
    """
    width = image["width"]
    height = image["height"]
    kernel_length = len(kernel)

    def get_pixel_location(image_index, kernel_index):
        """
        Gets location of pixel to multiply given the index of the pixel
        we are operating on and the index of the kernel
        """
        image_row = image_index[0]
        image_col = image_index[1]
        kernel_row = kernel_index[0]
        kernel_col = kernel_index[1]
        kernel_row_offset = kernel_row - (kernel_length - 1) / 2
        kernel_col_offset = kernel_col - (kernel_length - 1) / 2
        return [image_row + kernel_row_offset, image_col + kernel_col_offset]

    def get_pixel_zero(image_index):
        """
        get_pixel, but accounting for boundary behavior being zero
        """
        row = image_index[0]
        col = image_index[1]

        if 0 <= row <= height - 1 and 0 <= col <= width - 1:
            return image["pixels"][int(row * width + col)]
        return 0

    def get_pixel_extend(image_index):
        """
        get_pixel, but accounting for boundary behavior being zero
        """
        row = image_index[0]
        new_row = min(height - 1, max(0, row))
        col = image_index[1]
        new_col = min(width - 1, max(0, col))

        return image["pixels"][int(new_row * width + new_col)]

    def get_pixel_wrap(image_index):
        """
        get_pixel, but accounting for boundary behavior being wrap
        """
        row = image_index[0]
        new_row = row % height
        col = image_index[1]
        new_col = col % width

        return image["pixels"][int(new_row * width + new_col)]

    def get_pixel_boundary(image_index, boundary_behavior):
        """
        get_pixel, but accounting for boundary behavior
        """
        if boundary_behavior == "zero":
            return get_pixel_zero(image_index)
        elif boundary_behavior == "extend":
            return get_pixel_extend(image_index)
        elif boundary_behavior == "wrap":
            return get_pixel_wrap(image_index)

    def apply_to_pixel(image_index):
        """
        Applies the kernel to an indvidual pixel.
        """
        return sum(
            (kernel[row][col])
            * get_pixel_boundary(
                get_pixel_location(image_index, [row, col]), boundary_behavior
            )
            for row in range(kernel_length)
            for col in range(kernel_length)
        )

    def apply_to_image():
        """
        Applies the kernel to the image.
        """
        new_image = new_image = {
            "height": height,
            "width": width,
            "pixels": [
                apply_to_pixel([row, col])
                for row in range(height)
                for col in range(width)
            ],
        }

        return new_image

    if boundary_behavior in ("zero", "extend", "wrap"):
        return apply_to_image()
    else:
        return None


def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the "pixels" list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    width = image["width"]
    height = image["height"]
    new_image = {
        "height": height,
        "width": width,
        "pixels": [round(min(255, max(0, pixel))) for pixel in image["pixels"]],
    }

    return new_image


# FILTERS


def blurred(image, kernel_size):
    """
    Return a new image representing the result of applying a box blur (with the
    given kernel size) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)

    # then compute the correlation of the input image with that kernel

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    def create_kernel_blur(n):
        return [[1 / (n**2)] * n] * n

    blurred_image = correlate(image, create_kernel_blur(kernel_size), "extend")
    final_image = round_and_clip_image(blurred_image)

    return final_image


def sharpened(image, kernel_size):
    """
    Returns sharpened image.
    """

    def create_kernel_sharpen(n):
        kernel = []
        mid = int((n - 1) / 2)
        for i in range(n):
            kernel.append([-1 / (n**2)] * n)
        kernel[mid][mid] += 2
        return kernel

    sharpened_image = correlate(image, create_kernel_sharpen(kernel_size), "extend")
    final_image = round_and_clip_image(sharpened_image)

    return final_image


def edges(image):
    """
    Detect edges on image.
    """
    krow = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
    kcol = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    o_r = correlate(image, krow, "extend")
    o_c = correlate(image, kcol, "extend")
    edge_image = {
        "height": image["height"],
        "width": image["width"],
        "pixels": [
            round(math.sqrt((o_r["pixels"][i]) ** 2 + (o_c["pixels"][i]) ** 2))
            for i in range(len(image["pixels"]))
        ],
    }
    final_image = round_and_clip_image(edge_image)

    return final_image


# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image("test_images/cat.png")
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [
                round(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]) for p in img_data
            ]
        elif img.mode == "LA":
            pixels = [p[0] for p in img_data]
        elif img.mode == "L":
            pixels = list(img_data)
        else:
            raise ValueError(f"Unsupported image mode: {img.mode}")
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_greyscale_image(image, filename, mode="PNG"):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the "mode" parameter.
    """
    out = Image.new(mode="L", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    construct = load_greyscale_image("test_images/construct.png")
    construct_edge = edges(construct)
    save_greyscale_image(construct_edge, "construct_edge.png")
