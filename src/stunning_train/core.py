import io
class reader:
    def file_stream_gen(self,obj):
        for line in obj:
            for word in line.split():
                yield word
    def __init__(self, stream, wpm=300, chunk_size= 5):
        self.wpm= wpm
        self.chunk_size = chunk_size
        if isinstance(stream, str):
            self.stream=iter(stream.split())
            self.size= len(stream.split())
        elif isinstance(stream, io.IOBase):
            curr = stream.tell()
            stream.seek(0, 2)
            self.size = stream.tell()
            stream.seek(curr)
            self.stream = self.file_stream_gen(stream)
        else:
            raise TypeError("Stream must be a string or a file-like object")
        self.history = []
        self.lookahead = []
        self.current = None
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
        return 60.0 / self.wpm


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
        self.current = self.history.pop()
        return self.current

    def nearby_words(self):
        return self.history.copy(), self.current, self.lookahead.copy()