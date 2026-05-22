import pypdf
class pdf_reader:
    def __init__(self, path):
        self.path = path
        try:
            self.reader = pypdf.PdfReader(path)
        except Exception as e:
            raise ValueError(f"Could not read PDF file {path}: {e}")

    def get_pages(self):
        return self.reader.pages

    def get_page_count(self):
        return len(self.reader.pages)

    def extract_text(self):
        text = ""
        for page in self.reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
