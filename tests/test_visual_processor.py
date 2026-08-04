import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

import pymupdf

from app.core.visual_processor import VisualDocumentProcessor


class VisualDocumentProcessorTest(unittest.TestCase):

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.root = Path(self.temporary_directory.name)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_reads_image_for_gemma(self):
        path = self.root / "scan.JPG"
        path.write_bytes(b"image-content")

        visual = VisualDocumentProcessor().extract(path)

        self.assertEqual(visual.images, (b"image-content",))
        self.assertEqual(visual.total_pages, 1)

    def test_extracts_pptx_images_in_numeric_order(self):
        path = self.root / "slides.pptx"

        with ZipFile(path, "w") as archive:
            archive.writestr("ppt/media/image10.png", b"ten")
            archive.writestr("ppt/media/image2.jpeg", b"two")

        visual = VisualDocumentProcessor().extract(path)

        self.assertEqual(visual.images, (b"two", b"ten"))
        self.assertEqual(visual.total_pages, 2)

    def test_renders_pdf_pages_as_images(self):
        path = self.root / "scan.pdf"
        document = pymupdf.open()
        document.new_page(width=200, height=200)
        document.save(path)
        document.close()

        visual = VisualDocumentProcessor().extract(path)

        self.assertEqual(visual.total_pages, 1)
        self.assertTrue(visual.images[0].startswith(b"\xff\xd8"))

    def test_reads_visual_pages_on_demand(self):
        path = self.root / "slides.pptx"

        with ZipFile(path, "w") as archive:
            archive.writestr("ppt/media/image1.png", b"first")
            archive.writestr("ppt/media/image2.png", b"second")

        processor = VisualDocumentProcessor(max_pages=1)

        self.assertEqual(processor.page_count(path), 2)
        self.assertEqual(processor.extract_page(path, 1), b"second")


if __name__ == "__main__":
    unittest.main()
