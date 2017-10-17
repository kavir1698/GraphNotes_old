import bibtexparser
import re
from crossref.restful import Works
import operator
import random, string
from itertools import islice
import ast
from common import *

reglar_expressions = {
    'r_end': re.compile(r"\s*#end#"),
    'r_dict': re.compile(r"(\{('.*': ('.*'|.*),?)*\})#end#"),
    'r_doi': re.compile(r"doi ([^\.]+).#end#"),
    'r_pages': re.compile(r":(\d+\s*[-]+\s*\d*)\s*#end#"),
    'r_issue': re.compile(r"\((.*)\)#end#"),
    'r_year': re.compile(r"\.\s*(\d{4})\s*;?#end#"),
    'r_volume': re.compile(r";\s*(.+)#end#"),
    'r_author': re.compile(r"(((\w+|\w+\s+\w+|\w\.\s+\w+|\w+\s+\w\.|\w\.\s+\w\.\s+\w\.\s+\w+|\w+\s+\w\.\s\w\.)(,\s+|\s*&\s*|\s+and\s+))+(\w\w+|\w+ \w+|\w\. \w+)\.)"),
    'r_title_and_journal': re.compile(r"(\w+)\s*\.\s*(\w+)\s*"),
    'r_prepear': re.compile(r"(@[^{]+\{[^,]+,)(.*)", flags=re.MULTILINE|re.DOTALL),
    'r_delete_spaces': re.compile(r",\s+(\w)"),
    'r_handle_end': re.compile(r"}}($|\n)")
}


ALL_BIBTEX_ATTR = [
    'howpublished', 'edition', 'organization', 'editor', 'volume', 'title', 'school',
    'author', 'month', 'journal', 'note', 'isbn', 'booktitle', 'series', 'doi', 'institution',
    'pages', 'chapter', 'address', 'number', 'year', 'publisher', 'issue', 'type', 'newrender', 'oldrender',
]

TYPE_BY_FIELDS = {
    'article': ['author', 'title', 'journal', 'year', 'volume', 'issue', 'pages', 'note'], 
    'book' : ['author', 'title', 'publisher', 'address', 'edition', 'month',  'year', 'note'],
    'booklet' : ['author', 'title', 'howpublished', 'address', 'month', 'year', 'note'],
    'conference' : ['author', 'title', 'editor', 'booktitle', 'volume', 'series', 'pages', 'address', 'month', 'year', 'organization', 'publisher', 'note'],        
    'inbook' : ['author', 'title', 'volume', 'series', 'chapter', 'pages', 'publisher', 'address', 'edition', 'month', 'year', 'note'],    
    'incollection' : ['author', 'title', 'organization', 'address', 'edition', 'edition', 'month', 'year', 'note'],
    'mastersthesis' : ['author', 'title', 'school', 'address', 'month', 'year', 'note'],
    'misc' : ['author', 'title', 'howpublished', 'month', 'year', 'note'],
    'phdthesis' : ['author', 'title', 'school', 'month', 'year', 'note'],   
    'proceedings' : ['editor', 'title', 'volume', 'series', 'address', 'month',  'year', 'organization', 'publisher', 'note'],  
    'techreport' : ['author', 'title', 'number', 'institution', 'address', 'month', 'year', 'note'],
}

ALL_TYPES = TYPE_BY_FIELDS.keys()

def randomword(length=12):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    size = random.randint(8, 12)
    return ''.join(random.choice(chars) for x in range(size))

# function
def prepareBibHTML(text):
    # placeholder
    return text
    
def getBibRenderFromHTML(html):
    return renderBibFromBibStr(getPlainText(html))

def prepareBibStr(bibtex_str):
    bibtex_str = bibtex_str.replace("\n", "")
    bibtex_str = reglar_expressions['r_delete_spaces'].sub(",\\1", bibtex_str, 0)
    bibtex_str = reglar_expressions['r_handle_end'].sub("}\n}", bibtex_str, 0)
    bibtex_str = "},\n\t".join(bibtex_str.split("},"))#replace("}}($|\n)", "}\n}")#.replace("}\n},", "}},")
    bibtex_str = reglar_expressions['r_prepear'].sub("\\1\n\t\\2", bibtex_str, 0)    
    return bibtex_str

def renderBibFromBibStr(bibtex_str):
    bibtex_str = prepareBibStr(bibtex_str)
    bib_database = bibtexparser.loads(bibtex_str)
    if not bib_database.entries:
        return "BROKEN BIBTEX" 
    
    ref = bib_database.entries[0]
    bibtex_attributes = ALL_BIBTEX_ATTR
    d = dict()
    d['TYPE'] = ref.get('ENTRYTYPE')
    d.update({attr: ref.get(attr) for attr in bibtex_attributes})
    return renderBibFromDict(d)
    
def readBibsFromFile(path, debug=False):
    
    """read BibTeX file and parse information from this file"""
    with open(path, "r") as bibtex_file:
        bibtex_str = bibtex_file.read()
        
    bibtex_str = prepareBibStr(bibtex_str)
    
    bib_database = bibtexparser.loads(bibtex_str)
    references = []
    bibtex_attributes = ALL_BIBTEX_ATTR
    for ref in bib_database.entries:
        d = dict()
        d['TYPE'] = ref.get('ENTRYTYPE')
        d.update({attr: ref.get(attr) for attr in bibtex_attributes})
        d['newrender'] = renderBibFromDict(d)
        converted_ref = convertDictToBibStr(d)
        references.append(converted_ref)  
    return references

# todo: need cleaning up ref:
def getRefByDOI(doi, debug=False):
    works = Works()
    ref = works.doi(doi)
    ref = {key: value for key, value in ref.items() if key in ALL_BIBTEX_ATTR }
    ref['newrender'] = renderBibFromDict(ref)
    if ref:
        return convertDictToBibStr(ref)
    


def convertDictToBibStr(d):
    bibtex_str = ""
    if "ENTRYTYPE" not in d:
        d["ENTRYTYPE"] = 'article'
    
    if "ID" not in d:
        d["ID"] = randomword(10)
        
    d["newrender"] = renderBibFromDict(d)
    
    etype = d.pop("ENTRYTYPE")
    ident = d.pop("ID")
    
    
    bibtex_str += "@{etype}{{{ident},".format(etype=etype, ident=ident)
    bibtex_str += ",\n".join("{} = {{{}}}".format(key, value) for key, value in d.items() if value)
    bibtex_str += "}"
    return bibtex_str

def renderBibFromDict(ref):
    if "newrender" in ref:
        return ref["newrender"]
    
    t = ref.get('TYPE') 
    t = t if t else ref.get('type')
    
    if list == type(ref.get('author')):
        ref['author'] = ", ".join([" ".join([i.get('family'), i.get('given')]) for i in ref.get('author')])
    
    if list == type(ref.get('title')):
        ref['title'] = ", ".join([i for i in ref.get('title')])
    
    if ref.get('page'): 
        ref['pages'] = ref['page']
        
    if ref.get('published-print'):
        pass
    
    for item in ALL_BIBTEX_ATTR:
        if type(ref.get(item)) == list:
            ref[item] = ', '.join(ref[item])
    
    if t not in ALL_TYPES:
        d = dict()
        for key, value in TYPE_BY_FIELDS.items():
            d[key] = sum([ 1 if ref.get(i) else 0 for i in value])
    
        t = max(d, key=lambda key: d[key])
        t = t if d[t] < 5 else "Other"
            
    if t == 'article':
    
        result  = '{}. '.format(ref['author'])  if ref.get('author') else ''
        result += '{}. '.format(ref['title'])   if ref.get('title') else ''
        result += '{}. '.format(ref['journal']) if ref.get('journal') else ''
        result += '{}'.format(ref['year'])      if ref.get('year') else ''
        result += '; {}'.format(ref['volume'])   if ref.get('volume') else '; '
        result += '({})'.format(ref['issue'])   if ref.get('issue') else ''
        result += ':{}.'.format(ref['pages'])    if ref.get('pages') else ''
        result += ' {}'.format(ref['note'])    if ref.get('note') else ''

    elif t == 'book':
        result  = '{}. '.format(ref['author'])  if ref.get('author') else ''
        result += '{}. '.format(ref['title'])   if ref.get('title') else ''
        result += '{}, '.format(ref['publisher'])   if ref.get('publisher') else ''
        result += '{}, '.format(ref['address'])   if ref.get('address') else '' 
        result += '{} edition, '.format(ref['edition'])   if ref.get('edition') else '' 
        result += '{} '.format(ref['month'])   if ref.get('month') else '' 
        result += '{}. '.format(ref['year'])   if ref.get('year') else ''
        result += ' {}'.format(ref['note'])    if ref.get('note') else ''
   
    elif t == 'booklet':
        result  = '{}. '.format(ref['author'])  if ref.get('author') else ''
        result += '{}. '.format(ref['title'])   if ref.get('title') else ''
        result += '{}, '.format(ref['howpublished'])   if ref.get('howpublished') else ''
        result += '{}, '.format(ref['address'])   if ref.get('address') else ''
        result += '{} '.format(ref['month'])   if ref.get('month') else ''
        result += '{}. '.format(ref['year'])   if ref.get('year') else ''
        result += ' {}'.format(ref['note'])    if ref.get('note') else ''
   
    elif t == 'conference':
        result  = '{}. '.format(ref['author'])  if ref.get('author') else ''
        result += '{}. '.format(ref['title'])   if ref.get('title') else ''
        result += 'In {}, editor, '.format(ref['editor'])   if ref.get('editor') else ''
        result += '{}, '.format(ref['booktitle'])   if ref.get('booktitle') else ''
        result += 'volume {} '.format(ref['volume'])   if ref.get('volume') else ''
        result += 'of {}, '.format(ref['series'])   if ref.get('series') else ''
        result += 'page {}, '.format(ref['pages'])   if ref.get('pages') else ''
        result += '{}, '.format(ref['address'])   if ref.get('address') else ''
        result += '{} '.format(ref['month'])   if ref.get('month') else ''
        result += '{}. '.format(ref['year'])   if ref.get('year') else ''
        result += '{}. '.format(ref['organization'])   if ref.get('organization') else ''
        result += '{}. '.format(ref['publisher'])   if ref.get('publisher') else ''
        result += ' {}'.format(ref['note'])    if ref.get('note') else ''
   
    elif t == 'inbook':
        result  = '{}. '.format(ref['author'])  if ref.get('author') else ''
        result += '{}. '.format(ref['title'])   if ref.get('title') else ''
        result += 'volume {} '.format(ref['volume'])   if ref.get('volume') else ''
        result += 'of {}, '.format(ref['series'])   if ref.get('series') else ''
        result += 'chapter {}, '.format(ref['chapter'])   if ref.get('chapter') else ''
        result += 'pages {}, '.format(ref['pages'])   if ref.get('pages') else ''
        result += '{}. '.format(ref['publisher'])   if ref.get('publisher') else ''
        result += '{}, '.format(ref['address'])   if ref.get('address') else ''
        result += '{} edition, '.format(ref['edition'])   if ref.get('edition') else ''
        result += '{} '.format(ref['month'])   if ref.get('month') else ''
        result += '{}. '.format(ref['year'])   if ref.get('year') else ''
        result += ' {}'.format(ref['note'])    if ref.get('note') else '' 
   
   
    elif t == 'incollection':
        result  = '{}. '.format(ref['author'])  if ref.get('author') else ''
        result += '{}. '.format(ref['title'])   if ref.get('title') else ''
        result += '{}.'.format(ref['organization'])   if ref.get('organization') else ''
        result += '{}, '.format(ref['address'])   if ref.get('address') else ''
        result += '{} edition, '.format(ref['edition'])   if ref.get('edition') else ''
        result += '{} '.format(ref['month'])   if ref.get('month') else ''
        result += '{}. '.format(ref['year'])   if ref.get('year') else ''
        result += ' {}'.format(ref['note'])    if ref.get('note') else '' 

    elif t == 'mastersthesis':
        result  = '{}. '.format(ref['author'])  if ref.get('author') else ''
        result += '{}. Thesis, '.format(ref['title'])   if ref.get('title') else ''
        result += '{}. '.format(ref['school'])   if ref.get('school') else ''
        result += '{}, '.format(ref['address'])   if ref.get('address') else ''
        result += '{} '.format(ref['month'])   if ref.get('month') else ''
        result += '{}. '.format(ref['year'])   if ref.get('year') else ''
        result += ' {}'.format(ref['note'])    if ref.get('note') else ''   

    elif t == 'misc':
        result  = '{}. '.format(ref['author'])  if ref.get('author') else ''
        result += '{}. , '.format(ref['title'])   if ref.get('title') else ''
        result += '{}, '.format(ref['howpublished'])   if ref.get('howpublished') else ''
        result += '{} '.format(ref['month'])   if ref.get('month') else ''
        result += '{}. '.format(ref['year'])   if ref.get('year') else ''
        result += ' {}'.format(ref['note'])    if ref.get('note') else ''

    elif t == 'phdthesis':
        result  = '{}. '.format(ref['author'])  if ref.get('author') else ''
        result += '{}. Thesis, '.format(ref['title'])   if ref.get('title') else ''
        result += '{}, '.format(ref['school'])   if ref.get('school') else ''
        result += '{} '.format(ref['month'])   if ref.get('month') else ''
        result += '{}. '.format(ref['year'])   if ref.get('year') else ''
        result += ' {}'.format(ref['note'])    if ref.get('note') else ''   

    elif t == 'proceedings':
        result  = '{}, editor. '.format(ref['editor'])  if ref.get('editor') else ''
        result += '{}, '.format(ref['title'])   if ref.get('title') else ''
        result += 'volume {} '.format(ref['volume'])   if ref.get('volume') else ''
        result += 'of {}, '.format(ref['series'])   if ref.get('series') else ''
        result += '{}, '.format(ref['address'])   if ref.get('address') else ''
        result += '{} '.format(ref['month'])   if ref.get('month') else ''
        result += '{}. '.format(ref['year'])   if ref.get('year') else ''
        result += '{}. '.format(ref['organization'])   if ref.get('organization') else ''
        result += '{}. '.format(ref['publisher'])   if ref.get('publisher') else ''
        result += ' {}'.format(ref['note'])    if ref.get('note') else '' 
   
    elif t == 'techreport':
        result  = '{}. '.format(ref['author'])  if ref.get('author') else ''
        result += '{}. '.format(ref['title'])   if ref.get('title') else ''
        result += 'Techical report {}. '.format(ref['number'])   if ref.get('number') else ''
        result += '{}, '.format(ref['institution'])   if ref.get('institution') else ''
        result += '{}, '.format(ref['address'])   if ref.get('address') else ''
        result += '{} '.format(ref['month'])   if ref.get('month') else ''
        result += '{}. '.format(ref['year'])   if ref.get('year') else ''
        result += ' {}'.format(ref['note'])    if ref.get('note') else ''
   
    else:
        result  = '{}. '.format(ref['author'])  if ref.get('author') else ''
        result += '{}. '.format(ref['title'])   if ref.get('title') else ''
        result += '{} '.format(ref['month'])   if ref.get('month') else ''
        result += '{}. '.format(ref['year'])   if ref.get('year') else ''
        result += ' {}'.format(ref['note'])    if ref.get('note') else ''        
   
    return result


# Coverting bib render to bibtex notation
def deleteEndingSpaces(line):
    
    # Compile regular for finding ending
    r_end = re.compile(r"\s*#end#")
    
    if r_end.search(line):
        
        # Last match of ending mark
        for m_end in r_end.finditer(line): pass
        
        # delete any spaces between #end# and string
        line = line[:m_end.start()] + "#end#"
        
        return line
    else: 
        raise LookupError
    
def getAttrByReg(line, reg, from_start=False):
    
    line = deleteEndingSpaces(line)
    
    # Compile regular for finding attr with ending mark 
    r = reg
    
    # Check attr in the end of string
    if r.search(line):
        
        if from_start:
            m = r.search(line)
        else:
        # Last match of the attr with ending mark
            for m in islice(r.finditer(line), 0, 10): pass
        
        # Delete attr with #end# and the append #end# to end of sting 
        if from_start:
            line = line[:m.start()] + line[m.end():]
        else:
            line = line[:m.start()] + "#end#"
        
        return line, m.groups()
    
    else:
        return line, None

def getBibStrFromRender(line):
    bibtex_dict = dict()
    
    # Check line is string or not
    if not isinstance(line, str): raise TypeError
    
    bibtex_dict["oldrender"] = line
    
    # Add #end# mark to the end of line
    line = re.sub("\n", " ", line)
    line = line + "#end#"
    
    # get dict
    reg = reglar_expressions["r_dict"]
    line, groups = getAttrByReg(line, reg)
    if groups:
        dict_as_str = groups[0]
        dict_as_dict = ast.literal_eval(dict_as_str)
        bibtex_dict.update(dict_as_dict)
    
    #get doi
    reg = reglar_expressions["r_doi"]
    line, groups = getAttrByReg(line, reg)
    if groups:
        doi = groups[0]
        bibtex_dict["doi"] = doi
    
    #get pages
    reg = reglar_expressions["r_pages"]
    line, groups = getAttrByReg(line, reg)
    if groups:
        pages = groups[0]
        bibtex_dict["pages"] = pages
        
    #get issue   
    reg = reglar_expressions["r_issue"]
    line, groups = getAttrByReg(line, reg)
    if groups:
        issue = groups[0]
        bibtex_dict["issue"] = issue
    
    #get year
    reg = reglar_expressions["r_year"]
    line, groups = getAttrByReg(line, reg)
    if groups:
        year = groups[0]
        bibtex_dict["year"] = year        
        
    #get volume
    reg = reglar_expressions["r_volume"]
    line, groups = getAttrByReg(line, reg)
    if groups:
        volume = groups[0]
        bibtex_dict["volume"] = volume        

    #get year
    reg = reglar_expressions["r_year"]
    line, groups = getAttrByReg(line, reg)
    if groups:
        year = groups[0]
        bibtex_dict["year"] = year      
    
    if len(line.split(" .")) == 3:
        author, title, journal = line.replace("#end#", "").split(" .")
        bibtex_dict["author"], bibtex_dict["title"], bibtex_dict["journal"] = author, title, journal
        
    elif len(line.split(" .")) == 2:
        author, title = line.replace("#end#", "").split(" .")
        bibtex_dict["author"], bibtex_dict["title"] = author, title
   
    elif len(line.split(" .")) == 4:
        author, title, journal, year = line.replace("#end#", "").split(" .")
        bibtex_dict["author"], bibtex_dict["title"], bibtex_dict["journal"], bibtex_dict["year"] = author, title, journal, year 
    else:
        
        
            #line, groups = getAttrByReg(line, r"\.\s*.*\s*(\d{4})\s.*;?#end#")
              
        #get author
        reg = reglar_expressions["r_author"]
        line = line.replace(" .", ". ")
        line, groups = getAttrByReg(line, reg, from_start=True)
        if groups:
            author = groups[0]
            bibtex_dict["author"] = author 
            
        reg = reglar_expressions["r_title_and_journal"]
        line, groups = getAttrByReg(line, reg)
        if groups:
            title, journal = groups[0], groups[1]
            bibtex_dict["title"], bibtex_dict["journal"] = title, journal       
    
    #line = line.replace("#end#", "")
    
    if "ENTRYTYPE" not in bibtex_dict:
        bibtex_dict['ENTRYTYPE'] = 'article'
    
    if "ID" not in bibtex_dict:
        bibtex_dict['ID'] = randomword(10)
    
    bibtext_str = convertDictToBibStr(bibtex_dict)
        
    return bibtext_str    



if __name__ == "__main__":
    pass
    	