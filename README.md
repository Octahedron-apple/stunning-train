# stunning-train

Terminal-based Fast Screen Reader using Rapid Serial Visual Presentation (RSVP).

## Installation

Install the package using pip:

```bash
pip install .
```

This registers the command-line entrypoint `stt`.

## Usage

Run `stt` to open the interactive file selection menu:

```bash
stt
```

Alternatively, read a file or string directly with customized words-per-minute (WPM):

```bash
# Read a file directly
stt -f path/to/file.txt

# Read a string directly
stt -s "Hello world, this is a speed reader test."

# Customize the initial WPM (default is 300)
stt -f path/to/file.txt -w 400
```

## Controls

During reading:
- **Left Arrow**: Seek backward by 2% of the text.
- **Right Arrow**: Seek forward by 2% of the text.

## Python API

You can also use the core reading state engine directly in Python:

```python
from stunning_train.core import reader

# Create a reader instance
r = reader("Hello world this is a test", wpm=300)

# Traverse words
while r.has_next():
    word = r.next_word()
    print(word)
```