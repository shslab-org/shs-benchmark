Build a tiny static site generator and run it:

1. Write `build.py`: converts every .md file in docs/ to an .html file in
   site/ (flat: same basename, .html)
2. Each page must have: <title> from the first # heading, the markdown
   converted to HTML (headings, paragraphs, bold), and a simple navigation
   bar on every page linking to ALL pages
3. index.html: a landing page in site/ linking to all generated pages
4. RUN the generator to actually produce site/ with 4 html files
5. Keep the original docs/ untouched. Verify your output by reading the
   generated files back.