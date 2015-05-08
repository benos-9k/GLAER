#!/bin/env python
#
# API for querying the OpenGL API specification / documentation
#
# The API specification './api/gl.xml' will be downloaded if it is not present.
# The documentation is not critical to the operation of this module, and as such
# will not be downloaded if it does not exist. This module does however come with
# both the API specification and documentation already present.
#
# To update the API specification and documentation, import this module and call
# 'glapi.update_api()' and 'glapi.update_docs()' respectively, then reload the module.
#
# Input files are expected to use unix line breaks (LF only).
#
# @author Ben Allen
#

import bs4
import sys, os, re, inspect, urllib2

# get script directory so we can find resources
thisdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

def _get_page(url):
	'''download a webpage'''
	headers = {'User-Agent': 'Mozilla/5.0'}
	req = urllib2.Request(url,headers=headers)
	return urllib2.urlopen(req).read()
# }

def _get_manpage(manpath):
	'''download a GL manpage, e.g. 'man2/glAccum.xml' '''
	return _get_page('https://cvs.khronos.org/svn/repos/ogl/trunk/ecosystem/public/sdk/docs/' + manpath)
# }

def _ensure_dir_exists(path):
	'''make a directory and all parents, but don't error if it exists'''
	try:
		os.makedirs(path)
	except OSError, e:
		if e.errno != errno.EEXIST: raise
	# }
# }

def update_api():
	'''update the API specification files (gl.xml)'''
	_ensure_dir_exists(thisdir + '/api')
	page = _get_page('https://cvs.khronos.org/svn/repos/ogl/trunk/doc/registry/public/api/gl.xml')
	print type(page)
	with open(thisdir + '/api/gl.xml', 'w') as f: f.write(page)
# }

def update_docs():
	'''update the API documentation files'''
	print >>sys.stderr, 'glapi.py: fetching documentation'
	# save all xml docs
	for version in (2, 3, 4):
		man = 'man{0}'.format(version)
		manpage = _get_manpage(man)
		_ensure_dir_exists(thisdir + '/docs/' + man)
		soup = bs4.BeautifulSoup(manpage, features='xml')
		file_tags = [file_tag for file_tag in soup.find('svn').find('index').find_all('file')]
		for i, file_tag in enumerate(file_tags):
			href = str(file_tag['href']).strip()
			# skip non-xml
			if not href.endswith('.xml'): continue
			print >>sys.stderr, 'glapi.py: fetching [{man} {i:5} /{c:5}] {href}'.format(man=man, i=i+1, c=len(file_tags), href=href)
			# skip files we already have
			filename = thisdir + '/docs/{man}/{href}'.format(man=man, href=href)
			if os.path.exists(filename):
				print >>sys.stderr, 'glapi.py: skipping'
				continue
			# }
			# download and save
			page = _get_manpage('{man}/{href}'.format(man=man, href=href))
			with open(filename + '.part', 'w') as file:
				file.write(page)
			# }
			# rename to mark completion
			# prevent corruption if downloader is aborted
			os.rename(filename + '.part', filename)
		# }
		# TODO save all manX docs to one file each
		
	# }
# }

# download API specification if not present
if not os.path.exists(thisdir + '/api/gl.xml'):
	print >>sys.stderr, 'glapi.py: api/gl.xml not present, downloading...'
	_update_api()
# }

class API(object):
	'''
	One of the OpenGL APIs (GL, GLES1, GLES2).
	
	Attributes:
		name          Unicode name of this API
		versions      Dict of unicode API version names to API version instances for this API
		extensions    Dict of unicode extension names to extensions for this API
		enums         Dict of unicode enum names to Enum instances for all versions of this API
		commands      Dict of unicode command names to Command instances for all versions of this API
	'''
	def __init__(self, name):
		self.name = name
		# name -> APIVersion
		self.versions = dict()
		# name -> Extension
		self.extensions = dict()
		# name -> Enum (all versions)
		self.enums = dict()
		# name -> Command (all versions)
		self.commands = dict()
	# }
# }

class APIVersion(object):
	'''
	A version of a specific OpenGL API (e.g. GL 3.3).
	
	Attributes:
		api         API instance this APIVersion instance is for
		name        Unicode name of this API version
		number      Unicode string 'number' of this version of this API
		enums       Dict of unicode enum names to Enum instances for enums required by this version of this API
		commands    Dict of unicode command names to Command instances for commands required by this version of this API
	'''
	def __init__(self, api, name, number):
		self.api = api
		self.name = name
		# this is still a string
		self.number = number
		# name -> Enum
		self.enums = dict()
		# name -> Command
		self.commands = dict()
	# }
# }

class Extension(object):
	'''
	An extension to OpenGL.
	
	Attributes:
		name        Unicode name of this extension
		apis        Dict of unicode API names to API instances this extension is compatible with
		enums       Dict of unicode enum names to Enum instances for enums required by this extension
		commands    Dict of unicode command names to Command instances for commands required by this extension
	'''
	def __init__(self, name):
		self.name = name
		# name -> API
		self.apis = dict()
		# name -> Enum
		self.enums = dict()
		# name -> Command
		self.commands = dict()
	# }
# }

class Enum(object):
	'''
	An OpenGL Enum (named integer constant).
	
	Attributes:
		name           Unicode name of this enum
		value          Integer value of this enum
		apiversions    Dict of unicode API version names to APIVersion instances requiring this enum
		extensions     Dict of unicode extension names to Extension instances requiring this enum
	'''
	def __init__(self, name, value):
		self.name = name
		self.value = value
		# name -> APIVersion
		self.apiversions = dict()
		# name -> Extension
		self.extensions = dict()
	# }
# }

class Param(object):
	'''
	A parameter to an OpenGL command.
	
	Attributes:
		command    Command this parameter is associated with
		name       Unicode name of this parameter (
		index      Integer index of this parameter in the associated command
		doc        List of unicode strings for the documentation about this parameter
	'''
	def __init__(self, command, name, index, proto):
		self.command = command
		self.name = name
		self.index = index
		# format string for prototype
		self._proto = proto
		self.doc = []
	# }
	
	def format_proto(self, name=None):
		'''Format the (C-language) function parameter declaration with an optional user-specified parameter name.'''
		name = self.name if name == None else name
		return self._proto.format(name=name)
	# }
# }

class Command(object):
	'''
	An OpenGL command (function).
	
	Attributes:
		name           Unicode name of this command
		params         List of parameters (in order) to this command as Param instances
		apiversions    Dict of API version names to APIVersion instances requiring this command
		extensions     Dict of extension names to Extension instances requiring this command
		doc_desc       List of unicode strings for the 'description' documentation section for this command
		doc_notes      List of unicode strings for the 'notes' documentation section for this command
		doc_errors     List of unicode strings for the 'errors' documentation section for this command
	'''
	def __init__(self, name, params, proto):
		self.name = name
		self.params = params
		# format string for prototype
		self._proto = proto
		# name -> APIVersion
		self.apiversions = dict()
		# name -> Extension
		self.extensions = dict()
		self.doc_desc = []
		self.doc_notes = []
		self.doc_errors = []
	# }
	
	def find_param(self, pname):
		'''Find a parameter by name. Returns a Param instance if successful, None otherwise.'''
		return ([p for p in self.params if p.name == pname] + [None])[0]
	# }
	
	def format_proto(self, name=None):
		'''Format the (C-language) function prototype (minus parameter list) with an optional user-specified function name.'''
		name = self.name if name == None else name
		return self._proto.format(name=name)
	# }
# }

# name -> API
apis = dict()

# name -> APIVersion (all apis)
versions = dict()

# name -> Extension (all apis)
extensions = dict()

# name -> Enum (all apis, all versions)
enums = dict()

# name -> Command (all apis, all versions)
commands = dict()

# parse the api specification
_apisoup = bs4.BeautifulSoup(open(thisdir + '/api/gl.xml'), features='xml')

def _stripdocstr(s):
	return re.sub('\n\s+', '\n', s.strip())
# }

# enums
for enum_tags in _apisoup.registry.find_all('enums'):
	for enum_tag in enum_tags.find_all('enum'):
		name = unicode(enum_tag['name'])
		value = unicode(enum_tag['value'])
		enums[name] = Enum(name, value)
	# }
# }

# commands
for command_tag in _apisoup.registry.commands.find_all('command'):
	name = unicode(command_tag.proto.find('name').string).strip()
	# turn the command prototype into a format string
	command_tag.proto.find('name').string = ' {name} '
	# parameters
	params = []
	com = Command(name, params, unicode(command_tag.proto.get_text()).strip())
	for (i, ptag) in enumerate(command_tag.find_all('param')):
		pname = unicode(ptag.find('name').string).strip()
		# turn the param prototype into a format string
		ptag.find('name').string = ' {name} '
		params.append(Param(com, pname, i, unicode(ptag.get_text()).strip()))
	# }
	commands[name] = com
# }

# api versions
# TODO assumption: commands and enums only appear in feature tags once
for feature_tag in _apisoup.registry.find_all('feature'):
	# get or create api object
	apiname = unicode(feature_tag['api'])
	api = apis.get(apiname, API(apiname))
	apis[apiname] = api
	# get or create apiversion object, add to api
	vername = unicode(feature_tag['name'])
	ver = versions.get(vername, APIVersion(api, vername, unicode(feature_tag['number'])))
	versions[vername] = ver
	api.versions[vername] = ver
	# add enums and commands to apiversion, set apiversion on enums and commands
	for require_tag in feature_tag.find_all('require'):
		for enum_tag in require_tag.find_all('enum'):
			enum = enums[enum_tag['name'].strip()]
			enum.apiversions[vername] = ver
			api.enums[enum.name] = enum
			ver.enums[enum.name] = enum
		# }
		for command_tag in require_tag.find_all('command'):
			command = commands[command_tag['name'].strip()]
			command.apiversions[vername] = ver
			api.commands[command.name] = command
			ver.commands[command.name] = command
		# }
	# }
# }

# extensions
for extension_tag in _apisoup.registry.extensions.find_all('extension'):
	# get or create extension object
	extname = unicode(extension_tag['name'])
	ext = extensions.get(extname, Extension(extname))
	extensions[extname] = ext
	# supported apis
	for apiname in [name.strip() for name in extension_tag['supported'].split('|')]:
		api = apis.get(apiname)
		# many extensions mention 'glcore' in the supported string
		if not api: continue
		ext.apis[api.name] = api
		api.extensions[extname] = ext
	# }
	# add enums and commands to extension
	for require_tag in extension_tag.find_all('require'):
		for enum_tag in require_tag.find_all('enum'):
			enum = enums[enum_tag['name'].strip()]
			enum.extensions[extname] = ext
			ext.enums[enum.name] = enum
		# }
		for command_tag in require_tag.find_all('command'):
			command = commands[command_tag['name'].strip()]
			command.extensions[extname] = ext
			ext.commands[command.name] = command
		# }
	# }
# }

# documentation
for man in ['man2', 'man3', 'man4']:
	if os.path.isdir(thisdir + '/docs/' + man):
		for filename in os.listdir(thisdir + '/docs/' + man):
			if not filename.endswith('.xml'): continue
			with open(thisdir + '/docs/{man}/{name}'.format(man=man, name=filename)) as file:
				soup = bs4.BeautifulSoup(file, features='xml')
				
				try:
					
					# commands this doc page applies to
					# refnamediv is unfortunately not always usable for this
					doccmds = []
					# There are doc files for GLU and GLX commands (which are not part of GL itself),
					# GLSL functions, and some other things; we have to make sure they don't break anything.
					if soup.refentry and soup.refentry.refsynopsisdiv:
						for synoptag in soup.refentry.refsynopsisdiv.find_all('funcsynopsis'):
							if synoptag:
								# func prototypes according to doc page
								for prototag in synoptag.find_all('funcprototype'):
									cmd = commands.get(prototag.funcdef.function.string.strip())
									if cmd:
										doccmds.append(cmd)
										# re-write param names according to doc page;
										# these sometimes differ from the param names in gl.xml.
										# we _CANNOT_ re-write the entire prototype because the doc pages
										# contain mistakes like misspelt typenames.
										for (i, ptag) in enumerate(prototag.find_all('paramdef')):
											# functions of no args show up with one arg with def 'void'
											# 'void' may or may not be inside a parameter tag, which may not exist
											if ptag.get_text().strip() != 'void':
												# glTextureParameterfv has a stray '.' on a param name and a stray newline too
												cmd.params[i].name = unicode(ptag.parameter.string).replace('\n', ' ').strip(' .')
											# }
										# }
									# }
								# }
							# }
						# }
					# }
					
					# no relevant GL commands -> do nothing
					if len(doccmds) == 0: continue
					
					# doc section tags
					# both 'id' (man2, man3) and 'xml:id' (man4) are used
					params_tag = soup.refentry.find(lambda tag: tag.name == 'refsect1' and 'parameters' in [tag.get('xml:id'), tag.get('id')])
					desc_tag = soup.refentry.find(lambda tag: tag.name == 'refsect1' and 'description' in [tag.get('xml:id'), tag.get('id')])
					notes_tag = soup.refentry.find(lambda tag: tag.name == 'refsect1' and 'notes' in [tag.get('xml:id'), tag.get('id')])
					errors_tag = soup.refentry.find(lambda tag: tag.name == 'refsect1' and 'errors' in [tag.get('xml:id'), tag.get('id')])
					
					# command doc
					doc_desc = [_stripdocstr(tag.get_text()) for tag in desc_tag.find_all('para')]
					doc_notes = [_stripdocstr(tag.get_text()) for tag in notes_tag.find_all('para')] if notes_tag else []
					doc_errors = [_stripdocstr(tag.get_text()) for tag in errors_tag.find_all('para')] if errors_tag else []
					
					# parameter doc
					param_doc = dict()
					# some commands have no parameters
					if params_tag:
						for ptag in params_tag.variablelist.find_all('varlistentry'):
							# these param tags can be for several parameters
							pnames = [tag.string.strip() for tag in ptag.term.find_all('parameter')]
							doc = []
							for ltag in ptag.find_all('listitem'):
								doc += [_stripdocstr(tag.get_text()) for tag in ltag.find_all('para')]
							# }
							for pname in pnames: param_doc[pname] = doc
						# }
					# }
					
					# apply to commands and params
					for cmd in doccmds:
						cmd.doc_desc = doc_desc
						cmd.doc_notes = doc_notes
						cmd.doc_errors = doc_errors
						for (pname, pdoc) in param_doc.iteritems():
							param = cmd.find_param(pname)
							if param:
								param.doc = pdoc
							# }
						# }
					# }
				
				except:
					print >>sys.stderr, 'glapi.py: error processing file', filename
					raise
				# }
			# }
		# }
	# }
# }

# alias specific APIs
gl = apis['gl']




























