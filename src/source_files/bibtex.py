import bibtexparser


def parse_bibtex_from_file(path):
    """read BibTeX file and parse information from this file"""

    with open(path, "r") as bibtex_file:
        bibtex_str = bibtex_file.read()
        bib_database = bibtexparser.loads(bibtex_str)
        references = []
        for d in bib_database.entries:
            if d["ENTRYTYPE"] == "article":
                text = "{} .".format(d.pop("author")) if "author" in d else ""
                text += "{} .".format(d.pop("title")) if "title" in d else ""
                text += "{} .".format(d.pop("journal")) if "journal" in d else ""
                text += "{} ;".format(d.pop("year")) if "year" in d else ""
                text += "{}".format(d.pop("volume")) if "volume" in d else ""
                text += "({})".format(d.pop("issue")) if "issue" in d else ""
                text += ":{}".format(d.pop("pages")) if "pages" in d else ""
                text += "doi {}.".format(d.pop("doi")) if "doi" in d else ""
                references.append(text + (" " + str(d) if d else ""))
            else:
                print("NOT ARTICLE")
        return references
