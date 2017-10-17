import html2text

h = html2text.HTML2Text()
h.mark_code = False

def getPlainText(html):
    text = h.handle(html)
    text = text.replace("\n", "").strip()
    text = " ".join(text.split())
    return text