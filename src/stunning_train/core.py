import io
from .pdf import pdf_reader
class reader:
    def file_stream_gen(self,obj):
        for line in obj:
            for word in line.split():
                yield word
    
    def pdf_stream_gen(self, obj):
        for i, page in enumerate(obj.get_pages()):
            self.current_page = i + 1
            text = page.extract_text()
            if text:
                for word in text.split():
                    yield word
    def __init__(self, stream, wpm=300, chunk_size= 5):
        self.wpm= wpm
        self.chunk_size = chunk_size
        self.is_pdf = False
        self.current_page = 0
        if isinstance(stream, str):
            self.stream=iter(stream.split())
            self.size= len(stream)
        elif isinstance(stream, io.IOBase):
            curr = stream.tell()
            stream.seek(0, 2)
            self.size = stream.tell()
            stream.seek(curr)
            self.stream = self.file_stream_gen(stream)
        elif isinstance(stream, pdf_reader):
            self.is_pdf = True
            self.stream = self.pdf_stream_gen(stream)
            self.size = stream.get_page_count()
        else:
            raise TypeError("Stream must be a string, file-like object, or pdf_reader")
        self.history = []
        self.lookahead = []
        self.current = None
        self.words_read = 0
        self.chars_read = 0
        self.fill_lookahead()
    def fill_lookahead(self):
        while len(self.lookahead) < self.chunk_size:
            try:
                word = next(self.stream)
                self.lookahead.append(word)
            except StopIteration:
                break

    def get_speed(self):
        return self.wpm

    def set_speed(self, value):
        if value <= 0:
            raise ValueError("Speed must be greater than 0")
        self.wpm = value

    def get_delay(self):
        base_delay = 60.0 / self.wpm
        if self.current:
            return base_delay * (len(self.current) / 5.0)
        return base_delay


    def has_next(self):
        self.fill_lookahead()
        return len(self.lookahead) > 0

    def next_word(self):
        if not self.has_next():
            raise StopIteration()
        if self.current is not None:
            self.history.append(self.current)
            if len(self.history) > self.chunk_size:
                self.history.pop(0)
        self.current = self.lookahead.pop(0)
        self.words_read = self.words_read + 1
        self.chars_read = self.chars_read + len(self.current) + 1
        self.fill_lookahead()
        return self.current
    def skip_forward(self, n=1):
        for _ in range(n):
            if not self.has_next():
                break
            self.next_word()
        return self.current
    def go_backward(self):
        if len(self.history) == 0:
            return self.current
        if self.current is not None:
            self.lookahead.insert(0, self.current)
            self.chars_read = self.chars_read - (len(self.current) + 1)
        self.current = self.history.pop()
        self.words_read = self.words_read - 1
        if self.words_read < 0:
            self.words_read = 0
        if self.chars_read < 0:
            self.chars_read = 0
        return self.current
    def nearby_words(self):
        return self.history.copy(), self.current, self.lookahead.copy()
    def get_orp(self, word):
        if not word:
            return 0
        length = len(word)
        if length <= 3:
            return 0
        elif length <= 5:
            return 1
        elif length <= 9:
            return 2
        else:
            return 3