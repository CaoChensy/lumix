import os
import requests
import urllib.parse
from PIL import Image
from io import BytesIO
from typing import List, Optional

try:
    import fitz
    from fitz import Page
except ImportError:
    raise ImportError("Please install PyMuPDF to use this function.")
from lumix.types.documents import PageMetadata, DocumentPage

__all__ = [
    "StructuredPDF",
]


class StructuredPDF:
    """"""
    pdf: fitz.Document
    documents: List[DocumentPage]

    def __init__(
            self,
            path_or_data: BytesIO | bytes | str,
            **kwargs,
    ):
        """
        读取PDF文件并输出结构化的数据

        Args:
            path_or_data: PDF文件路径、URL链接或二进制数据
            **kwargs:
        """
        self.load_data(path_or_data)
        self.documents = []
        self.kwargs = kwargs
        self.parse_pdf_pages()

    def load_data(self, path_or_data: BytesIO | bytes | str, ):
        """"""
        if isinstance(path_or_data, BytesIO):
            stream = path_or_data
        elif isinstance(path_or_data, bytes):
            stream = BytesIO(path_or_data)
        elif isinstance(path_or_data, str):
            parsed_path = urllib.parse.urlparse(path_or_data)
            if parsed_path.scheme in ["http", "https"]:
                response = requests.get(path_or_data, timeout=20)
                response.raise_for_status()
                stream = BytesIO(response.content)
            else:
                expanded_path = os.path.expanduser(path_or_data)
                with open(expanded_path, 'rb') as f:
                    content = f.read()
                    stream = BytesIO(content)
        else:
            raise TypeError("Unsupported type for path_or_data: {}".format(type(path_or_data)))
        self.pdf = fitz.open(stream=stream)

    def parse_page_images(self, page: Page) -> List[Image.Image]:
        """"""
        images = []
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            base_image = self.pdf.extract_image(img[0])
            images.append(Image.open(BytesIO(base_image.get("image"))))
        return images

    def parse_pdf_pages(self):
        """"""
        for page_number in range(self.pdf.page_count):
            page = self.pdf.load_page(page_number)
            page_content = page.get_text()
            page_images = self.parse_page_images(page)

            self.documents.append(
                DocumentPage(
                    page_content=page_content,
                    metadata=PageMetadata(
                        page_number=page_number,
                        images=page_images
                    )
                )
            )

    def save_images(self, path: str) -> None:
        """"""
        image_path = os.path.join(path, "image")
        if not os.path.exists(image_path):
            os.makedirs(image_path)
        for page in self.documents:
            if page.metadata.images is not None:
                for i, image in enumerate(page.metadata.images):
                    path = os.path.join(image_path, f"page_{page.metadata.page_number}_image_{i}.png")
                    image.save(path)

    def save_text(self, path: str) -> None:
        """ 保存文本数据

        Args:
            path:

        Returns:

        """
        if not os.path.exists(path):
            os.makedirs(path)

        content = "\n\n".join([document.page_content for document in self.documents])
        file_path = os.path.join(path, f"content.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def save_structured(self, path: str) -> None:
        """"""
        self.save_text(path=path)
        self.save_images(path=path)

    def to_text(self, delimiter: str = "\n\n") -> str:
        """"""
        content = delimiter.join([document.page_content for document in self.documents])
        return content

    def page_to_image(self, dpi: Optional[int] = 150, pages: Optional[List[int]] = None) -> List[Image.Image]:
        """"""
        images = []
        if pages is None:
            pages = range(self.pdf.page_count)

        for page_number in pages:
            page = self.pdf.load_page(page_number)
            pix = page.get_pixmap(dpi=dpi)
            image = Image.frombytes(mode="RGB", size=(pix.width, pix.height), data=pix.samples)
            images.append(image)
        return images
