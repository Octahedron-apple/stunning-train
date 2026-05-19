import curses
import time
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
        elif isinstance(stream, io.IOBase):
            self.stream = self.file_stream_gen(stream)
        else:
            raise TypeError("Stream must be a string or a file-like object")
        self.history = []
        self.lookahead = []
        self.current = None
        