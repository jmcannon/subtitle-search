This is an app for quickly searching through Turkish subtitles on Netflix.
Dependencies are:
  1. Whoosh: light-weight library for rolling your own full-text search.
  2. Bottle: micro web framework

Subtitles must be manually downloaded from Netflix using this TamperMonkey script: https://greasyfork.org/en/scripts/26654-netflix-subtitle-downloader.
I have slightly modified the script to include videoIds in the file name. The script with my modifications is in this directory. Unfortunately, this
implementation is fragile and will break on updates to the original TamperMonkey script (which would likely be in response to Netflix changing their code).

Subtitles are expected to be in .vtt format. If the .vtt subtitles are to native content, they should be placed in /downloads/native. Otherwise, in /downloads/dubbed.

convert_vtt_to_text.py
Converts all the .vtt files in /downloads to simple text files that will be written to Whoosh storage. Copies are saved in /subtitles.

build_index.py
Builds Whoosh index and storage from scratch every time. If this starts taking a long time, optimize by only writing new documents. There's an example in the Whoosh docs.

run_app.py
Runs the Bottle web server and provides a single GET endpoint /search that expects a GET param q that contains a query string plugged directly into Whoosh.

KNOWN ISSUES:
- Currently hacking highlights by using a custom Scorer when the query is more than one word. This however is breaking quotes and wildcards on multi-words queries.
- Queries that have many matches (like common single words) are taking way too long.

To use:
  python -m venv env
  source env/bin/activate
  pip install -r requirements.txt

  if new .vtt files have been added:
    python convert_vtt_to_text.py
    python build_index.py

  python run_app.py

  Open localhost:8080.


TINY VIDEO CREATION PROCESS:
Use ScreenFlow to screen capture from Netflix. Make sure graphics acceleration is turned off in Chrome advanced
settings.
"t" to split.
Change canvas size to 350 x 350
"1" to zoom
"2" to resize to fit.
Custom save:
24 fps, 500 kb/s, multi-pass, automatic
audio: 44.1 khz, 96 k/s, mono
Export as mp4, place in video-compression directory. Run script and take results from 'compressed' dir.



