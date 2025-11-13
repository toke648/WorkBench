import gzip

with gzip.open("enwiki-latest-all-titles-in-ns0.gz", "rt", encoding="utf-8") as f:
    text = f.read()

with open("wiki_data.txt", "w", encoding="utf-8") as f:
    f.write(text)
