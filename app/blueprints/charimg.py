from PIL import Image
from functools import lru_cache
import os


path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "static", "img", "character"
)


def open_image(name):
    return Image.open(
        os.path.join(
            path,
            name,
        )
    )


@lru_cache
def charimg(*args):
    args = list(args)
    save_path = (
        f"{''.join([arg if type(arg) != int else f'body{arg}' for arg in args])}.png"
    )
    if os.path.exists(os.path.join(path, save_path)):
        return save_path

    # make image if it doesn't exist yet
    images = []
    for arg in args:
        if arg is not None and arg != "None":
            if arg.isdigit():
                body_image = open_image(f"body{arg}.png")
            else:
                images.append(open_image(f"{arg}.png"))
    for image in images:
        body_image.paste(image, (0, 0), image)
    body_image.save(os.path.join(path, save_path))
    return save_path
