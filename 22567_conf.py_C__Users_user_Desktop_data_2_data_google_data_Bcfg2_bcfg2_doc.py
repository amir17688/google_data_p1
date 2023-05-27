# -*- coding: utf-8 -*-
#
# Bcfg2 documentation build configuration file, created by
# sphinx-quickstart on Sun Dec 13 12:10:30 2009.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import os
import re
import sys
import time

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath('../src/lib'))
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('exts'))

# -- General configuration -----------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.doctest',
              'sphinx.ext.intersphinx', 'sphinx.ext.viewcode',
              'xmlschema']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# Path to XML schemas
xmlschema_path = "../schemas"

# The suffix of source filenames.
source_suffix = '.txt'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
#master_doc = 'contents'
master_doc = 'index'

# General information about the project.
# py3k compatibility
if sys.hexversion >= 0x03000000:
    project = 'Bcfg2'
    copyright = '2009-%s, Narayan Desai' % time.strftime('%Y')
else:
    project = u'Bcfg2'
    copyright = u'2009-%s, Narayan Desai' % time.strftime('%Y')

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '1.4'
# The full version, including alpha/beta/rc tags.
release = '1.4.0'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The reST default role (used for this markup: `text`) to use for all documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []


# -- Options for HTML output ---------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'default'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "collapsiblesidebar": "true"
}

# Add any paths that contain custom themes here, relative to this directory.
#html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
#html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = 'favicon.ico'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
html_sidebars = {
    'index': 'indexsidebar.html'
}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
#html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = 'Bcfg2doc'


# -- Options for LaTeX output --------------------------------------------------

latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
#'papersize': 'letterpaper',

# The font size ('10pt', '11pt' or '12pt').
#'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
#'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
# py3k compatibility
if sys.hexversion >= 0x03000000:
    latex_documents = [
      ('index', 'Bcfg2.tex', 'Bcfg2 Documentation',
       'Narayan Desai et al.', 'manual'),
    ]
else:
    latex_documents = [
      ('index', 'Bcfg2.tex', u'Bcfg2 Documentation',
       u'Narayan Desai et al.', 'manual'),
    ]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# Additional stuff for the LaTeX preamble.
#latex_preamble = ''

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True


# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('man/bcfg2', 'bcfg2', 'Bcfg2 client tool', [], 1),
    ('man/bcfg2-admin', 'bcfg2-admin',
     'Perform repository administration tasks', [], 8),
    ('man/bcfg2-build-reports', 'bcfg2-build-reports',
     'Generate state reports for Bcfg2 clients', [], 8),
    ('man/bcfg2.conf', 'bcfg2.conf',
     'Configuration parameters for Bcfg2', [], 5),
    ('man/bcfg2-crypt', 'bcfg2-crypt',
     'Bcfg2 encryption and decryption utility', [], 8),
    ('man/bcfg2-info', 'bcfg2-info',
     'Creates a local version of the Bcfg2 server core for state observation',
     [], 8),
    ('man/bcfg2-lint', 'bcfg2-lint',
     'Check Bcfg2 specification for validity, common mistakes, and style',
     [], 8),
    ('man/bcfg2-lint.conf', 'bcfg2-lint.conf',
     'Configuration parameters for bcfg2-lint', [], 5),
    ('man/bcfg2-report-collector', 'bcfg2-report-collector',
     'Reports collection daemon', [], 8),
    ('man/bcfg2-reports', 'bcfg2-reports',
     'Query reporting system for client status', [], 8),
    ('man/bcfg2-server', 'bcfg2-server',
     'Server for client configuration specifications', [], 8),
]

# If true, show URL addresses after external links.
#man_show_urls = False


# -- Options for Texinfo output ------------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
  ('index', 'Bcfg2', u'Bcfg2 Documentation',
   u'Narayan Desai', 'Bcfg2', 'One line description of project.',
   'Miscellaneous'),
]

# Documents to append as an appendix to all manuals.
#texinfo_appendices = []

# If false, no module index is generated.
#texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#texinfo_show_urls = 'footnote'


# autodoc settings
autodoc_default_flags = ['members', 'show-inheritance']
autoclass_content = "both"

private_re = re.compile(r'^\s*\.\.\s*private-include:\s*(.+)$')

private_include = []


def skip_member_from_docstring(app, what, name, obj, skip, options):
    """ since sphinx 1.0 autodoc doesn't support the :private-members:
    directive, this function allows you to specify
    ``.. private-include: <name>[,<name,...]`` in the docstring of a
    class containing a private method, etc., to ensure that it's
    included. Due to a bug in Sphinx, this doesn't work for attributes
    -- only things that actually have docstrings.  If you want to
    include private attributes, you have to explicitly include them,
    either with :members:, or by putting :autoattribute: in the
    __init__ docstring for a class or module docstring."""
    global private_include
    if name == '__doc__':
        private_include = []
        if not obj:
            return None
        for line in obj.splitlines():
            match = private_re.match(line)
            if match:
                private_include.extend(re.split(r',\s*', match.group(1)))
        return None

    if not skip:
        return None

    if name in private_include:
        return False
    return None


def setup(app):
    app.connect('autodoc-skip-member', skip_member_from_docstring)

# intersphinx settings

# generate intersphinx mappings for all versions of python we support;
# the default will be the version of python this is built with.
# Python only started using sphinx in 2.6, so we won't have docs for
# 2.4 or 2.5.  These are in reverse order, since sphinx seems to look
# in the last mapping first.

def check_object_path(key, url, path):
    if os.path.isfile(path):
        return {key: (url, path)}
    else:
        return {key: (url, None)}

intersphinx_mapping = {}
intersphinx_mapping.update(\
    check_object_path('mock',
                      'http://www.voidspace.org.uk/python/mock',
                      '/usr/share/doc/python-mock-doc/html/objects.inv'))
intersphinx_mapping.update(\
    check_object_path('cherrypy',
                      'http://docs.cherrypy.org/stable',
                      'intersphinx/cherrypy/objects.inv'))

versions = ["3.2", "2.7", "2.6"]
cur_version = '.'.join(str(v) for v in sys.version_info[0:2])

for pyver in versions:
    if pyver == cur_version:
        key = 'py'
    else:
        key = 'py' + pyver.replace(".", "")
    intersphinx_mapping.update(\
        check_object_path(key,
                          'http://docs.python.org/%s' % pyver,
                          '/usr/share/doc/python'
                            + '.'.join([str(x) for x in sys.version_info[0:2]])
                            + '/html/objects.inv'))
