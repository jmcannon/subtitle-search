import webbrowser
from bottle import route, run, template, response, request
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

search_engine = open_dir("index")
parser = QueryParser("content", schema=search_engine.schema)

# Highlight content looks like this:
#
# 00:04:07.791
# Balıklar sizi sevdiklerini hiç çekinmeden söylerler.
#
# 00:04:12.666
# Ama gerçek olup olmadığını bilemezsiniz.

def parse_time_line(timeLine):
    return timeLine[1:-4]   # Only need 1 digit for hours. Don't need subseconds.

def html_format_highlight(highlight):
    lines = highlight.split('\n')
    start_time = ""
    formatted = []

    for line in lines:
        if line == '':
            continue
        elif line[0] == '0':
            start_time = parse_time_line(line)
        else:
            if start_time == "":
                continue
            line = """
                    <div class='text' data-time="{start_time}">
                        <span class="time">{start_time}</span>
                        <div>{line}</div>
                    </div>
            """.format(start_time=start_time, line=line)
            formatted.append(line)

    return '\n'.join(formatted)

def get_start_time_of_highlight(highlight):
    lines = highlight.split('\n')
    for line in lines:
        if line and line[0] == '0':
            return parse_time_line(line)

@route('/')
def index():
    return template('index.html')

@route('/search')
def search():
    response.set_header('Access-Control-Allow-Origin', '*')  # Needed since request coming from localhost.

    query_string = request.query.q
    q = parser.parse(query_string)
    hits = []

    with search_engine.searcher() as searcher:
        results = searcher.search(q, limit=None)
        results.fragmenter.charlimit = None     # With no charlimit, search will provide highlights to the end of the document.
        results.fragmenter.maxchars = 300       # Max length of a fragment.
        results.fragmenter.surround = 100       # Number of characters to with which to surround the match for context.

        for hit in results:
            highlights = hit.highlights("content", top=20).split('...')

            for highlight in highlights:
                start_time = get_start_time_of_highlight(highlight)
                hits.append({
                    'title': hit['title'],
                    'videoId': hit['videoId'],
                    'isDubbed': hit['dubbed'],
                    'startTime': start_time,
                    'html': html_format_highlight(highlight)
                })

    return {'hits': hits}


if __name__ == "__main__":
    webbrowser.open_new('http://localhost:8080')
    run(host='localhost', port=8080)









