from itertools import groupby
import re
import thread

from calais import Calais
import nltk
import restlite
from topia.termextract import extract
from wsgiref.simple_server import make_server
import xml.dom.minidom


#################################################
# Helper/support functions & classes
#################################################

class clean_text():
	"""Preprocess text, eliminating noise, in a flexible manner.

	Example usage:
		mycleaner = clean_text(text, ["strip_characters", "eliminate_stopwords", \
										"eliminate_nonwords", "normalize_tokens"])
		cleaned = mycleaner.clean()

	:param text: Text including sentences and paragraphs etc.
	:type: str
	:param cleaners: A list of function names to utilize.
	:type cleaners: list

	"""

	def __init__(self, text, cleaners):
		self.tokens = nltk.word_tokenize(text.lower())
		self.cleaners = ["_%s" % cleaner for cleaner in cleaners]

	def _strip_characters(self):
		self.tokens = [t.strip(',').strip('.').strip('\'').strip('"') 
												 for t in self.tokens]

	def _eliminate_stopwords(self):
		#uses nltk stop word corpus
		stopwords = nltk.corpus.stopwords.words('english')
		self.tokens = [t for t in self.tokens if t.lower() not in stopwords]

	def _eliminate_nonwords(self):   
		self.tokens = [t for t in self.tokens if 
		len(t)>2
			and not re.match('^[\d-]+$', t) \
			and not re.search('\.', t) \
			and not re.match('^&', t)]

	def _normalize_tokens(self):
		# contract on dashes
		self.tokens = [t.replace('-','') for t in self.tokens]

	def clean(self):
		"""Master method"""
		for cleaner in self.cleaners:
			cleaning_func = getattr(self, cleaner)
			cleaning_func()
		cleaned_text = ' '.join(self.tokens)
		return cleaned_text

def create_xml(extracted_info):
	"""Builds xml dom document for REST response.

	:param extracted_info: list of tuples, each representing an extracted item.
		For example: [('search lead', 2, 3.0), .....].
	:type extracted_info: list of tuples

	"""

	doc = xml.dom.minidom.Document()
	resume_info_element = doc.createElement("resume_info")
	doc.appendChild(resume_info_element)
	extracted_element = doc.createElement("extracted")
	resume_info_element.appendChild(extracted_element)

	if extracted_info.get('keywords'):
		keywords_element = doc.createElement("keywords")
		extracted_element.appendChild(keywords_element)
		
		# Group keywords by length.
		groups = []
		for key, group in groupby(sorted(extracted_info.values()[0], 
								key=lambda x:x[2]), lambda x: x[2]):
			if key < 4:
				groups.append(list(group))
		
		# Generate each group with items sorted by hit-count.
		for key, group in enumerate(groups):
			grouping_element = doc.createElement("grouping")
			grouping_element.setAttribute("token_count", str(key + 1))
			keywords_element.appendChild(grouping_element)
			group = sorted(group, key=lambda x:x[1], reverse=True)
			for term, hit_count, token_count in group:
				keyword_element = doc.createElement("keyword")
				keyword_element.setAttribute("hit_count", str(hit_count))
				text_node = doc.createTextNode(term)
				keyword_element.appendChild(text_node)
				grouping_element.appendChild(keyword_element)

	if extracted_info.get('entities'):
		entities_element = doc.createElement("entities")
		extracted_element.appendChild(entities_element)

		# Group entities by type of entities.
		groups = []
		for key, group in groupby(sorted(extracted_info.values()[0], 
								key=lambda x:x[1]), lambda x: x[1]):
			groups.append(list(group))

		# Generate each group with items sorted by by relevancy.
		for group in groups:
			grouping_element = doc.createElement("grouping")
			grouping_element.setAttribute("entity_type", group[0][1])
			entities_element.appendChild(grouping_element)
			group = sorted(group, key=lambda x:x[2], reverse=True)
			for name, entity_type, relevance in group:
				entity_element = doc.createElement("entity")
				entity_element.setAttribute("relvance", str(relevance))
				text_node = doc.createTextNode(name)
				entity_element.appendChild(text_node)
				grouping_element.appendChild(entity_element)
	return doc

#################################################
# REST service methods.
#################################################

def keywords(env, start_response):
	"""Extracts key words and phrases from resume."""
	start_response('200 OK', [('Content-Type', 'text/xml')])
	try:
		with open('Darin_Plutchok_Resume_Taxonomist.txt') as f:
			text = f.read()
	except:
		raise restlite.Status, '400 Error Reading File'
	mycleaner = clean_text(text, ["strip_characters", "eliminate_stopwords", 
								  "eliminate_nonwords", "normalize_tokens"])
	cleaned = mycleaner.clean()

	extractor = extract.TermExtractor()
	keywords_tuples = extractor(cleaned)
	doc = create_xml({'keywords': keywords_tuples})

	return [doc.toxml()]


def entities(env, start_response):
	"""Extracts entities from resume utilizing the OpenCalais webservice."""

	start_response('200 OK', [('Content-Type', 'text/xml')])
	API_KEY = "kqyhhfppufvmvxspkstwjxw5"
	calais = Calais(API_KEY, submitter="resume_analysis")
	try:
		with open('Darin_Plutchok_Resume_Taxonomist.txt') as f:
			text = f.read()
	except: 
		raise restlite.Status, '400 Error Reading File'
	try:
		results = calais.analyze(text)
	except Exception as e:
		return "<error>%s</error>" % e

	entities_tuples = [(entity['name'], entity['_type'], entity['relevance'])
											  for entity in results.entities]
	doc = create_xml({'entities': entities_tuples})
	
	return [str(doc.toxml())]


def resume_text(env, start_response):
	"""Returns resume text"""

	start_response('200 OK', [('Content-Type', 'text/ascii')])
	try:
		with open('Darin_Plutchok_Resume_Taxonomist.txt') as f:
			text = f.read()
	except: 
		raise restlite.Status, '400 Error Reading File'

	return text

# The routes.

routes = [
	(r'GET /resume_text/', 'GET /resume_text/', resume_text),
	(r'GET /keywords/', 'GET /keywords', keywords),
	(r'GET /entities/', 'GET /entities', entities),
]

# Launch the server on port 8000.

if __name__ == '__main__':

    httpd = make_server('', 8000, restlite.router(routes))

    try: httpd.serve_forever()
    except KeyboardInterrupt: pass
