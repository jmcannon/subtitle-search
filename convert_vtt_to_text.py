import glob
import os
import re

# .vtt files look like this:
#
# 1
# 00:00:06.000 --> 00:00:09.416 position:50.00%,middle align:middle size:80.00% line:84.67%
# <c.bg_transparent>BİR NETFLIX DİZİSİ</c.bg_transparent>

# 2
# 00:00:09.500 --> 00:00:11.625 position:50.00%,middle align:middle size:80.00% line:84.67%
# <c.bg_transparent><i>Yalnız yaşamanın avantajları var.</i></c.bg_transparent>

# 3
# 00:00:24.833 --> 00:00:27.833 position:50.00%,middle align:middle size:80.00% line:79.33%
# <c.bg_transparent><i>Rahatlamaya çalışırken</i></c.bg_transparent>
# <c.bg_transparent><i>kimse sizi rahatsız etmez.</i></c.bg_transparent>
#
# Titles looks like this:
# Kırık.Kalpler.İçin.Astroloji.Rehberi.S02E06.Balık-81494845.vtt
file_paths = glob.glob('./downloads/*/*.vtt')

for file_path in file_paths:
    is_dubbed = 'dubbed' in file_path   # Dubbed content should be placed in /downloads/dubbed/, native content in /downloads/native/
    file_name = os.path.basename(file_path)
    title, videoId = file_name.split('-')

    # Remove .vtt extension.
    videoId = videoId[:-4]

    # Make readable and cut episode name from the end.
    is_series = bool(re.search(r"S\d\dE\d\d", title))   # Search for something like: S02E12
    if is_series:
        # Remove the episode name from the end by cutting off the end until you reach the episode number.
        # Example: Hilda.S01E02.No..2_.Gece.Yarısı.Devi-80117562.vtt
        title_parts = title.split('.')
        while not bool(re.match(r"S\d\dE\d\d", title_parts[-1])):
            title_parts.pop()
        title = ''.join(title_parts)

    output_file_name = title
    title = title.replace('.', ' ')

    with open('./subtitles/' + output_file_name + '.txt', 'w') as output_file:
        with open(file_path, 'r') as f:
            do_write = False
            line_type = ''
            text_list = []  # Single subtitles are sometime split across multiple lines.

            output_file.write(title + '\n')
            output_file.write(videoId + '\n')
            output_file.write('dubbed' if is_dubbed else 'native')
            output_file.write('\n\n')

            for line in f:
                line = line.strip()

                # Skip to the subtitles and ignore the metadata at the top.
                if not do_write:
                    if line == "1":
                        do_write = True
                        line_type = 'META'
                    continue

                if line_type == 'META':
                    start_time = line.split(' ')[0]
                    line_type = 'TEXT'
                    output_file.write(start_time + '\n')

                elif line_type == 'TEXT':
                    if line == '':
                        line_type = 'SKIP'
                        output_file.write(' '.join(text_list) + '\n')
                        text_list = []
                    else:
                        text = re.sub('<[^<]+?>', '', line)
                        text_list.append(text)

                elif line_type == 'SKIP':
                    output_file.write('\n')
                    line_type = 'META'







