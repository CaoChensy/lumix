import io
import base64
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim


__all__ = [
    "trans_bs64_to_image",
    "trans_image_to_bs64",
    "drop_similar_images",
    "drop_single_color_images",
]


def trans_bs64_to_image(bs64: str):
    """"""
    img_bytes = base64.b64decode(bs64)
    image = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    return image


def trans_image_to_bs64(image: Image.Image) -> str:
    """"""
    img_bytes = io.BytesIO()
    if image.mode == "RGB":
        image.save(img_bytes, format='JPEG')
    elif image.mode == "RGBA":
        image.save(img_bytes, format='PNG')
    else:
        raise ValueError("Unsupported image mode: {}".format(image.mode))
    img_bs64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
    return img_bs64


def drop_similar_images(
        images: list[Image.Image],
        threshold: float = 0.95,
        resize: tuple[int, int] = (256, 256)
) -> list[Image.Image]:
    """
    使用 SSIM 剔除相似图片

    Args:
        images: 输入的 PIL 图片列表
        threshold: SSIM 阈值（0~1，值越大越严格）
        resize: 预处理尺寸（缩小可加速计算）

    Returns:
        过滤后的唯一图片列表
    """
    processed = []
    for img in images:
        img = img.convert("L")
        img = img.resize(resize)
        processed.append(np.array(img))

    unique_images = []
    unique_data = []
    for i, processed_image in enumerate(processed):
        is_unique = True
        for j in range(len(unique_data)):
            similarity = ssim(processed_image, unique_data[j], channel_axis=None)
            if similarity >= threshold:
                is_unique = False
                break
        if is_unique:
            unique_images.append(images[i])
            unique_data.append(processed_image)
    return unique_images


def is_single_color(
        image: Image.Image,
        tolerance: int = 5,
) -> bool:
    """

    Args:
        image:
        tolerance:

    Returns:

    """
    img = image.convert("RGB")
    r_extrema = img.getextrema()[0]
    g_extrema = img.getextrema()[1]
    b_extrema = img.getextrema()[2]
    mark = (
        (r_extrema[1] - r_extrema[0] <= tolerance) and
        (g_extrema[1] - g_extrema[0] <= tolerance) and
        (b_extrema[1] - b_extrema[0] <= tolerance)
    )
    return mark


def drop_single_color_images(
        images: list[Image.Image],
) -> list[Image.Image]:
    """
    过滤单色图片

    Args:
        images: 输入的PIL图片列表

    Returns:
        过滤后的图片列表
    """
    return [image for image in images if not is_single_color(image)]

