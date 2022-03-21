import glob
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, STORED

# Reads converted text files from /subtitles and builds a Whoosh search index.

schema = Schema(content=TEXT(stored=True), title=STORED, videoId=STORED, dubbed=STORED)
index = create_in("index", schema)
writer = index.writer()

file_paths = glob.glob('./subtitles/*.txt')

for file_path in file_paths:
    with open(file_path) as f:
        title = f.readline().strip()
        videoId = f.readline().strip()
        dubbed = f.readline().strip() == 'dubbed'
        f.readline() # Skip first new line.

        content = f.read()
        writer.add_document(title=title, content=content, videoId=videoId, dubbed=dubbed)

writer.commit(optimize=True)
