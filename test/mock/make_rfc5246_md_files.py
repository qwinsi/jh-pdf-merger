# This program read rfc5246.txt and convert the text into multiple markdown files.
# Each markdown file is a section of the RFC.
# The markdown files are used to generate the PDF files in the same directory.
# You don't need to run this program unless you want to generate the PDF files yourself.

import re


def save_to_file(filename: str, lines: list[str]):
    with open(filename, 'w') as f:
        # https://stackoverflow.com/questions/17232677/disable-page-numbering-converting-markdown-to-pdf-with-pandoc
        f.write("\\pagenumbering{gobble}\n\n")

        # the title should be huge and in the center
        # https://stackoverflow.com/questions/42217126/how-do-i-convert-a-markdown-file-with-centered-text-in-atom-using-pandoc-conver
        f.write("\\begin{center}")
        f.write(f"\\Huge {lines[0].strip()}\n")
        f.write("\\end{center}\n\n")

        lines[0] = ""
        f.write(''.join(lines))

if __name__ == '__main__':
    lines = ["0. Abstract", "\n"]
    title = "0. Abstract"

    with open('rfc5246.txt', 'r') as f:
        num_lines_to_drop = 0
        new_section = False
        for line in f.readlines():
            if re.match(r'.+\[Page\s\d+\]', line):
                num_lines_to_drop = 4
            if num_lines_to_drop > 0:
                num_lines_to_drop -= 1
                continue

            if re.match(r'((\d+)\.)+(\s*)(\w+)', line):
                # extract leading numbers and dots
                leading_numbers_tag = re.findall(r'[\d\.]+', line)[0]
                num_dots = leading_numbers_tag.count('.')
                assert num_dots > 0
                if num_dots == 1:
                    new_section = True
                else:
                    line = f"{'#' * (num_dots - 1)} {line}"

            elif re.match(r'Appendix [A-Z]', line):
                new_section = True
            elif line == "\n":
                line = "\n\n" # markdown needs two newlines to start a new paragraph

            if new_section:
                save_to_file(f'{title}.md', lines)
                title = line.strip()
                lines = []
                new_section = False

            lines.append(line)

        # Do not forget the final section
        if len(lines) > 0:
            save_to_file(f'{title}.md', lines)
