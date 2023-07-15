"""
6.101 Spring '23 Lab 2: Image Processing 2
"""

#!/usr/bin/env python3

# NO ADDITIONAL IMPORTS!
# (except in the last part of the lab; see the lab writeup for details)
import math
from PIL import Image


# VARIOUS FILTERS


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


def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """

    def color_filter(image):
        return combine_images([filt(image) for image in split_image(image)])

    return color_filter


def split_image(image):
    pixels = image["pixels"]
    return [
        {
            "height": image["height"],
            "width": image["width"],
            "pixels": [pixels[j][i] for j in range(len(pixels))],
        }
        for i in range(3)
    ]


def combine_images(images):
    height = images[0]["height"]
    width = images[0]["width"]
    pixels0 = images[0]["pixels"]
    pixels1 = images[1]["pixels"]
    pixels2 = images[2]["pixels"]
    num_pixels = len(pixels0)
    return {
        "height": height,
        "width": width,
        "pixels": [(pixels0[i], pixels1[i], pixels2[i]) for i in range(num_pixels)],
    }


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


def make_blur_filter(kernel_size):
    """
    takes the parameter kernel_size and returns a blur filter
    (which takes a single image as argument). In this way, we
    can make a blur filter that is consistent with the form 
    expected by color_filter_from_greyscale_filter
    """
    def blurred(image):
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

    return blurred


def make_sharpen_filter(kernel_size):
    """
    takes the parameter kernel_size and returns a sharpen filter
    (which takes a single image as argument). In this way, we
    can make a sharpen filter that is consistent with the form 
    expected by color_filter_from_greyscale_filter
    """
    def sharpened(image):
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

    return sharpened


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """

    def apply_filters(image):
        new_image = image
        for filt in filters:
            new_image = filt(new_image)
        return new_image

    return apply_filters


# SEAM CARVING

# Main Seam Carving Implementation


def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image. Returns a new image.
    """
    new_image = image

    for i in range(ncols):
        grey = greyscale_image_from_color_image(new_image)
        energy = compute_energy(grey)
        cem = cumulative_energy_map(energy)
        seam = minimum_energy_seam(cem)
        new_image = image_without_seam(new_image, seam)
        print(i)

    return new_image


# Optional Helper Functions for Seam Carving


def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    pixels = image["pixels"]
    return {
        "height": image["height"],
        "width": image["width"],
        "pixels": [
            round(0.299 * pixels[i][0] + 0.587 * pixels[i][1] + 0.114 * pixels[i][2])
            for i in range(len(pixels))
        ],
    }


def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """
    return edges(grey)


def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_energy
    function), computes a "cumulative energy map" as described in the lab 2
    writeup.

    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].
    """
    width = energy["width"]
    pixels = energy["pixels"]

    def get_energy(index, energy_so_far):
        if index <= width - 1:
            energy_so_far.append(pixels[index])
        elif index % width == 0:
            energy_so_far.append(
                pixels[index]
                + min(energy_so_far[index - width], energy_so_far[index - width + 1])
            )
        elif index % width == width - 1:
            energy_so_far.append(
                pixels[index]
                + min(energy_so_far[index - width], energy_so_far[index - width - 1])
            )
        else:
            energy_so_far.append(
                pixels[index]
                + min(
                    energy_so_far[index - width],
                    energy_so_far[index - width - 1],
                    energy_so_far[index - width + 1],
                )
            )

    energy_so_far = []
    for i in range(len(pixels)):
        get_energy(i, energy_so_far)

    return {
        "height": energy["height"],
        "width": width,
        "pixels": energy_so_far,
    }


def minimum_energy_seam(cem):
    """
    Given a cumulative energy map, returns a list of the indices into the
    'pixels' list that correspond to pixels contained in the minimum-energy
    seam (computed as described in the lab 2 writeup).
    """
    height = cem["height"]
    width = cem["width"]
    pixels = cem["pixels"]

    last_row = pixels[len(pixels) - width : len(pixels)]
    start_index = last_row.index(min(last_row)) + len(pixels) - width

    def get_min_seam_above(index, pixels, min_seam_so_far):
        if index % width == 0:
            indices = [index - width, index - width + 1]
        elif index % width == width - 1:
            indices = [index - width - 1, index - width]
        else:
            indices = [index - width - 1, index - width, index - width + 1]
        energies = [pixels[index] for index in indices]
        min_seam_so_far.insert(0, indices[energies.index(min(energies))])

    min_seam_so_far = [start_index]

    for i in range(height - 1):
        get_min_seam_above(min_seam_so_far[0], pixels, min_seam_so_far)

    return min_seam_so_far


def image_without_seam(image, seam):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    pixels = image["pixels"]
    new_pixels = []
    for i, pixel in enumerate(pixels):
        if i not in seam:
            new_pixels.append(pixel)

    return {
        "height": image["height"],
        "width": image["width"] - 1,
        "pixels": new_pixels,
    }


def custom_feature(im1, im2, row, col):
    """
    Pastes im1 onto im2 starting at the index of
    im2["pixels"] specified by the start input.
    """
    im1_height = im1["height"]
    im1_width = im1["width"]
    im2_width = im2["width"]
    im2_height = im2["height"]
    start = row * im2["width"] + col
    indices_to_paste = []
    print(f"finding indices to paste: {im1_height} rows")
    for r in range(im1_height):
        print(r)
        for index in range(start, start + im1_width):
            indices_to_paste.append(index)
        start += im2_width
    print("done finding indices to paste")

    new_pixels = []
    im1_index = 0
    print(f"assembling final image: {im2_height} rows")
    for i, pixel in enumerate(im2["pixels"]):
        if i % im2_width == 0:
            print(i / im2_width)
        if i in indices_to_paste:
            new_pixels.append(im1["pixels"][im1_index])
            im1_index += 1
        else:
            new_pixels.append(pixel)

    return {"height": im2_height, "width": im2_width, "pixels": new_pixels}


# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img = img.convert("RGB")  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_color_image(image, filename, mode="PNG"):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode="RGB", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
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
    by the 'mode' parameter.
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
    # color_inverted = color_filter_from_greyscale_filter(inverted)
    # inverted_color_cat = color_inverted(load_color_image('test_images/cat.png'))
    # save_color_image(inverted_color_cat, "inverted_color_cat.png")
    # blur_filter = make_blur_filter(9)
    # blurry9 = blur_filter(load_color_image('test_images/python.png'))
    # save_color_image(blurry9, "python_blur.png")
    # sharp7 = make_sharpen_filter(7)(load_color_image("test_images/sparrowchick.png"))
    # save_color_image(sharp7, "sparrowchick_sharp.png")
    # filter1 = color_filter_from_greyscale_filter(edges)
    # filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    # filt = filter_cascade([filter1, filter1, filter2, filter1])
    # frog_filt = filt(load_color_image('test_images/frog.png'))
    # save_color_image(frog_filt, "frog_filt.png")
    # two_cats = load_color_image("test_images/twocats.png")
    # seam_cats = seam_carving(two_cats, 100)
    # save_color_image(seam_cats, "seam_cats.png")
    # bluegill = load_color_image("test_images/bluegill.png")
    # small_frog = load_color_image("test_images/smallfrog.png")
    # test_paste = custom_feature(small_frog, bluegill, 0)
    # save_color_image(test_paste, "test_paste.png")
    alex_headshot = load_color_image("test_images/alex_headshot.png")
    lebron = load_color_image("test_images/lebron.png")
    alex_paste = custom_feature(alex_headshot, lebron, 210, 590)
    save_color_image(alex_paste, "alex_paste.png")
