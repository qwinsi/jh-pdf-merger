# Where do these PDF files come from?

They are generated from RFC-5246, which is available at https://www.rfc-editor.org/rfc/rfc5246

You can run the following commands to generate the PDF files:

```bash
cd test/mock
python make_rfc5246_md_files.py
for i in *md; do pandoc  -o "${i%.md}.pdf" "$i";done
```

You don't need to run these commands, because the PDF files are already placed in this repo.
