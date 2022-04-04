import webbrowser
from collections import defaultdict
from bottle import route, run, template, response, request, debug
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh.highlight import FragmentScorer

search_engine = open_dir("index")
parser = QueryParser("content", schema=search_engine.schema)
debug(False)

# Highlight content looks like this:
#
# 00:04:07.791
# Balıklar sizi sevdiklerini hiç çekinmeden söylerler.
#
# 00:04:12.666
# Ama gerçek olup olmadığını bilemezsiniz.

def parse_time_line(timeLine):
    # 00:04:12.666
    return timeLine[1:-4]   # Only need 1 digit for hours. Don't need subseconds.

def get_lines(highlight):
    lines = highlight.split('\n')
    start_time = ""
    line_objects = []

    for line in lines:
        if line == '':
            continue
        elif line[0] == '0' and len(line) == 12:
            start_time = parse_time_line(line)
        else:
            if start_time == "":
                continue
            line = {'text': line, 'time': start_time}
            line_objects.append(line)
            start_time = ""

    return line_objects

def get_start_time_of_highlight(highlight):
    lines = highlight.split('\n')
    for line in lines:
        if line and line[0] == '0':
            return parse_time_line(line)

def has_special_chars(q):
    return 'AND' in q or 'OR' in q or '*' in q

class PhraseScorer(FragmentScorer):
    def __init__(self, phrase):
        # Get the list of words from the phrase query
        self.words = phrase.split(' ')

    def __call__(self, f):
        # Create a dictionary mapping words to the positions the word
        # occurs at, e.g. "foo" -> [1, 5, 10]
        d = defaultdict(list)
        for token in f.matches:
            d[token.text].append(token.pos)

        # For each position the first word appears at, check to see if the
        # rest of the words appear in order at the subsequent positions
        first_word = self.words[0]
        for pos in d[first_word]:
            # found = 1
            found = False
            for word in self.words[1:]:
                pos += 1
                if pos not in d[word]:
                    break
                else:
                    #found += 1
                    found = True
            #if found == len(self.words):
            if found:
                return 100
        return 0

@route('/')
def index():
    return template('index.html')

@route('/search')
def search():
    query_string = request.query.q
    page_number = int(request.query.page) or 1

    if not has_special_chars(query_string):
        query_string = '"' + query_string + '"'

    q = parser.parse(query_string)
    hits = []
    result_page = None

    with search_engine.searcher() as searcher:
        #results = searcher.search(q, limit=None, terms=True)       # Search all at once - was getting too slow for lots of hits.
        result_page = searcher.search_page(q, page_number, pagelen=50)
        results = result_page.results

        results.fragmenter.charlimit = None     # With no charlimit, search will provide highlights to the end of the document.
        results.fragmenter.maxchars = 300       # Max length of a fragment.
        results.fragmenter.surround = 100       # Number of characters to with which to surround the match for context.

        # Use a custom scorer to only surface exact matches in highlights. Ignore if wildcard, AND, or OR is used.
        if (len(query_string.split(' ')) > 1) and not has_special_chars(query_string):
           results.scorer = PhraseScorer(query_string.replace('"', ''))

        for hit in result_page:
            highlights = hit.highlights("content", top=20).split('...')

            for highlight in highlights:
                start_time = get_start_time_of_highlight(highlight)
                lines = get_lines(highlight)

                if start_time:
                    hits.append({
                        'title': hit['title'],
                        'videoId': hit['videoId'],
                        'isDubbed': hit['dubbed'],
                        'startTime': start_time,
                        'lines': lines
                    })

    print(f'Found {len(hits)} results. Returning page {result_page.pagenum} of {result_page.pagecount}.' )
    return {'hits': hits, 'pageNumber': result_page.pagenum, 'totalPages': result_page.pagecount}


if __name__ == "__main__":
    webbrowser.open_new('http://localhost:8080')
    run(host='localhost', port=8080)









