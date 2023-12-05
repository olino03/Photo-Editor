from PIL import Image, ImageDraw


def create_image(i, j):
    image = Image.new("RGB", (i, j), "white")
    return image


def get_pixel(image, i, j):
    width, height = image.size
    if i > width or j > height:
        return None

    pixel = image.getpixel((i, j))
    return pixel


# Bound pixels within 0-255 values
def get_max(value):
    if value > 255:
        return 255

    return int(value)


def get_sepia_pixel(red, green, blue, alpha):
    value = 0

    tRed = get_max((0.759 * red) + (0.398 * green) + (0.194 * blue))
    tGreen = get_max((0.676 * red) + (0.354 * green) + (0.173 * blue))
    tBlue = get_max((0.524 * red) + (0.277 * green) + (0.136 * blue))

    if value == 1:
        tRed = get_max((0.759 * red) + (0.398 * green) + (0.194 * blue))
        tGreen = get_max((0.524 * red) + (0.277 * green) + (0.136 * blue))
        tBlue = get_max((0.676 * red) + (0.354 * green) + (0.173 * blue))
    if value == 2:
        tRed = get_max((0.676 * red) + (0.354 * green) + (0.173 * blue))
        tGreen = get_max((0.524 * red) + (0.277 * green) + (0.136 * blue))
        tBlue = get_max((0.524 * red) + (0.277 * green) + (0.136 * blue))

    return tRed, tGreen, tBlue, alpha


def color_average(image, i0, j0, i1, j1):
    red, green, blue, alpha = 0, 0, 0, 255

    width, height = image.size

    i_start, i_end = i0, i1
    if i0 < 0:
        i_start = 0
    if i1 > width:
        i_end = width

    j_start, j_end = j0, j1
    if j0 < 0:
        j_start = 0
    if j1 > height:
        j_end = height

    count = 0
    for i in range(i_start, i_end - 2, 2):
        for j in range(j_start, j_end - 2, 2):
            count += 1
            p = get_pixel(image, i, j)
            red, green, blue = p[0] + red, p[1] + green, p[2] + blue

    red /= count
    green /= count
    blue /= count

    return int(red), int(green), int(blue), alpha


def convert_sepia(image):
    image = image.convert("RGB")
    width, height = image.size
    new = create_image(width, height)
    pixels = new.load()

    for i in range(0, width, 1):
        for j in range(0, height, 1):
            p = get_pixel(image, i, j)
            pixels[i, j] = get_sepia_pixel(p[0], p[1], p[2], 255)

    return new


def convert_pointilize(image):
    image = image.convert("RGB")
    width, height = image.size

    radius = 6
    count = 0
    errors = [1, 0, 1, 1, 2, 3, 3, 1, 2, 1]
    new = create_image(width, height)
    draw = ImageDraw.Draw(new)

    for i in range(0, width, radius + 3):
        for j in range(0, height, radius + 3):
            color = color_average(image, i - radius, j - radius, i + radius, j + radius)

            eI = errors[count % len(errors)]
            count += 1
            eJ = errors[count % len(errors)]

            draw.ellipse((i - radius + eI, j - radius + eJ, i + radius + eI, j + radius + eJ), fill=color)

    return new
