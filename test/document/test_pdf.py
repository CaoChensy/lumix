import unittest
from lumix.documents import StructuredPDF


class TestReadPDF(unittest.TestCase):

    def setUp(self):
        self.pdf_path = "https://pdf.dfcfw.com/pdf/H3_AP202503201645075160_1.pdf?1742482089000.pdf"

    def test_read_pdf(self):
        pdf = StructuredPDF(self.pdf_path)

        print(len(pdf.documents))
        print(pdf.documents[0].metadata.images)
        print(pdf.documents[0].metadata.page_number)

    def test_save_image(self):
        """"""
        pdf = StructuredPDF(self.pdf_path)
        pdf.save_images(path="./")

    def test_tran_image(self):
        """"""
        pdf = StructuredPDF(self.pdf_path)
        images = pdf.page_to_image(dpi=300, pages=[0])
        print(images)

    def test_request(self):
        """"""
        pdf = StructuredPDF(self.pdf_path)
        print(pdf.documents)
        pdf.save_structured(path="./")
