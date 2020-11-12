import traceback
import warnings
from pprint import pprint
import ast, tokenize
from pathlib import Path
from collections import Counter, defaultdict

MODULES = """\
__future__
__main__
__phello__.foo
_aix_support
_bootlocale
_bootsubprocess
_collections_abc
_compat_pickle
_compression
_markupbase
_osx_support
_py_abc
_pydecimal
_pyio
_sitebuiltins
_strptime
_sysconfigdata_x86_64_conda_cos6_linux_gnu
_sysconfigdata_x86_64_conda_linux_gnu
_thread
_threading_local
_weakrefset
abc
aifc
antigravity
argparse
array
ast
asynchat
asyncio
asyncio.base_events
asyncio.base_futures
asyncio.base_subprocess
asyncio.base_tasks
asyncio.constants
asyncio.coroutines
asyncio.events
asyncio.exceptions
asyncio.format_helpers
asyncio.futures
asyncio.locks
asyncio.log
asyncio.proactor_events
asyncio.protocols
asyncio.queues
asyncio.runners
asyncio.selector_events
asyncio.sslproto
asyncio.staggered
asyncio.streams
asyncio.subprocess
asyncio.tasks
asyncio.threads
asyncio.transports
asyncio.trsock
asyncio.unix_events
asyncio.windows_events
asyncio.windows_utils
asyncore
atexit
audioop
base64
bdb
binascii
binhex
bisect
builtins
bz2
cProfile
calendar
cgi
cgitb
chunk
cmath
cmd
code
codecs
codeop
collections
collections.abc
colorsys
compileall
concurrent
concurrent.futures
concurrent.futures._base
concurrent.futures.process
concurrent.futures.thread
configparser
contextlib
contextvars
copy
copyreg
crypt
csv
ctypes
ctypes._aix
ctypes._endian
ctypes.macholib
ctypes.macholib.dyld
ctypes.macholib.dylib
ctypes.macholib.framework
ctypes.util
ctypes.wintypes
curses
curses.ascii
curses.has_key
curses.panel
curses.textpad
dataclasses
datetime
dbm
dbm.dumb
dbm.gnu
dbm.ndbm
decimal
difflib
dis
distutils
distutils._msvccompiler
distutils.archive_util
distutils.bcppcompiler
distutils.ccompiler
distutils.cmd
distutils.command
distutils.command.bdist
distutils.command.bdist_dumb
distutils.command.bdist_msi
distutils.command.bdist_packager
distutils.command.bdist_rpm
distutils.command.bdist_wininst
distutils.command.build
distutils.command.build_clib
distutils.command.build_ext
distutils.command.build_py
distutils.command.build_scripts
distutils.command.check
distutils.command.clean
distutils.command.config
distutils.command.install
distutils.command.install_data
distutils.command.install_egg_info
distutils.command.install_headers
distutils.command.install_lib
distutils.command.install_scripts
distutils.command.register
distutils.command.sdist
distutils.command.upload
distutils.config
distutils.core
distutils.cygwinccompiler
distutils.debug
distutils.dep_util
distutils.dir_util
distutils.dist
distutils.errors
distutils.extension
distutils.fancy_getopt
distutils.file_util
distutils.filelist
distutils.log
distutils.msvc9compiler
distutils.msvccompiler
distutils.spawn
distutils.sysconfig
distutils.tests
distutils.tests.support
distutils.tests.test_archive_util
distutils.tests.test_bdist
distutils.tests.test_bdist_dumb
distutils.tests.test_bdist_msi
distutils.tests.test_bdist_rpm
distutils.tests.test_bdist_wininst
distutils.tests.test_build
distutils.tests.test_build_clib
distutils.tests.test_build_ext
distutils.tests.test_build_py
distutils.tests.test_build_scripts
distutils.tests.test_check
distutils.tests.test_clean
distutils.tests.test_cmd
distutils.tests.test_config
distutils.tests.test_config_cmd
distutils.tests.test_core
distutils.tests.test_cygwinccompiler
distutils.tests.test_dep_util
distutils.tests.test_dir_util
distutils.tests.test_dist
distutils.tests.test_extension
distutils.tests.test_file_util
distutils.tests.test_filelist
distutils.tests.test_install
distutils.tests.test_install_data
distutils.tests.test_install_headers
distutils.tests.test_install_lib
distutils.tests.test_install_scripts
distutils.tests.test_log
distutils.tests.test_msvc9compiler
distutils.tests.test_msvccompiler
distutils.tests.test_register
distutils.tests.test_sdist
distutils.tests.test_spawn
distutils.tests.test_sysconfig
distutils.tests.test_text_file
distutils.tests.test_unixccompiler
distutils.tests.test_upload
distutils.tests.test_util
distutils.tests.test_version
distutils.tests.test_versionpredicate
distutils.text_file
distutils.unixccompiler
distutils.util
distutils.version
distutils.versionpredicate
doctest
email
email._encoded_words
email._header_value_parser
email._parseaddr
email._policybase
email.base64mime
email.charset
email.contentmanager
email.encoders
email.errors
email.feedparser
email.generator
email.header
email.headerregistry
email.iterators
email.message
email.mime
email.mime.application
email.mime.audio
email.mime.base
email.mime.image
email.mime.message
email.mime.multipart
email.mime.nonmultipart
email.mime.text
email.parser
email.policy
email.quoprimime
email.utils
encodings
encodings.aliases
encodings.ascii
encodings.base64_codec
encodings.big5
encodings.big5hkscs
encodings.bz2_codec
encodings.charmap
encodings.cp037
encodings.cp1006
encodings.cp1026
encodings.cp1125
encodings.cp1140
encodings.cp1250
encodings.cp1251
encodings.cp1252
encodings.cp1253
encodings.cp1254
encodings.cp1255
encodings.cp1256
encodings.cp1257
encodings.cp1258
encodings.cp273
encodings.cp424
encodings.cp437
encodings.cp500
encodings.cp720
encodings.cp737
encodings.cp775
encodings.cp850
encodings.cp852
encodings.cp855
encodings.cp856
encodings.cp857
encodings.cp858
encodings.cp860
encodings.cp861
encodings.cp862
encodings.cp863
encodings.cp864
encodings.cp865
encodings.cp866
encodings.cp869
encodings.cp874
encodings.cp875
encodings.cp932
encodings.cp949
encodings.cp950
encodings.euc_jis_2004
encodings.euc_jisx0213
encodings.euc_jp
encodings.euc_kr
encodings.gb18030
encodings.gb2312
encodings.gbk
encodings.hex_codec
encodings.hp_roman8
encodings.hz
encodings.idna
encodings.iso2022_jp
encodings.iso2022_jp_1
encodings.iso2022_jp_2
encodings.iso2022_jp_2004
encodings.iso2022_jp_3
encodings.iso2022_jp_ext
encodings.iso2022_kr
encodings.iso8859_1
encodings.iso8859_10
encodings.iso8859_11
encodings.iso8859_13
encodings.iso8859_14
encodings.iso8859_15
encodings.iso8859_16
encodings.iso8859_2
encodings.iso8859_3
encodings.iso8859_4
encodings.iso8859_5
encodings.iso8859_6
encodings.iso8859_7
encodings.iso8859_8
encodings.iso8859_9
encodings.johab
encodings.koi8_r
encodings.koi8_t
encodings.koi8_u
encodings.kz1048
encodings.latin_1
encodings.mac_arabic
encodings.mac_croatian
encodings.mac_cyrillic
encodings.mac_farsi
encodings.mac_greek
encodings.mac_iceland
encodings.mac_latin2
encodings.mac_roman
encodings.mac_romanian
encodings.mac_turkish
encodings.mbcs
encodings.oem
encodings.palmos
encodings.ptcp154
encodings.punycode
encodings.quopri_codec
encodings.raw_unicode_escape
encodings.rot_13
encodings.shift_jis
encodings.shift_jis_2004
encodings.shift_jisx0213
encodings.tis_620
encodings.undefined
encodings.unicode_escape
encodings.utf_16
encodings.utf_16_be
encodings.utf_16_le
encodings.utf_32
encodings.utf_32_be
encodings.utf_32_le
encodings.utf_7
encodings.utf_8
encodings.utf_8_sig
encodings.uu_codec
encodings.zlib_codec
ensurepip
ensurepip._bundled
ensurepip._uninstall
enum
errno
faulthandler
fcntl
filecmp
fileinput
fnmatch
formatter
fractions
ftplib
functools
gc
genericpath
getopt
getpass
gettext
glob
graphlib
grp
gzip
hashlib
heapq
hmac
html
html.entities
html.parser
http
http.client
http.cookiejar
http.cookies
http.server
idlelib
idlelib.autocomplete
idlelib.autocomplete_w
idlelib.autoexpand
idlelib.browser
idlelib.calltip
idlelib.calltip_w
idlelib.codecontext
idlelib.colorizer
idlelib.config
idlelib.config_key
idlelib.configdialog
idlelib.debugger
idlelib.debugger_r
idlelib.debugobj
idlelib.debugobj_r
idlelib.delegator
idlelib.dynoption
idlelib.editor
idlelib.filelist
idlelib.format
idlelib.grep
idlelib.help
idlelib.help_about
idlelib.history
idlelib.hyperparser
idlelib.idle
idlelib.idle_test
idlelib.idle_test.htest
idlelib.idle_test.mock_idle
idlelib.idle_test.mock_tk
idlelib.idle_test.template
idlelib.idle_test.test_autocomplete
idlelib.idle_test.test_autocomplete_w
idlelib.idle_test.test_autoexpand
idlelib.idle_test.test_browser
idlelib.idle_test.test_calltip
idlelib.idle_test.test_calltip_w
idlelib.idle_test.test_codecontext
idlelib.idle_test.test_colorizer
idlelib.idle_test.test_config
idlelib.idle_test.test_config_key
idlelib.idle_test.test_configdialog
idlelib.idle_test.test_debugger
idlelib.idle_test.test_debugger_r
idlelib.idle_test.test_debugobj
idlelib.idle_test.test_debugobj_r
idlelib.idle_test.test_delegator
idlelib.idle_test.test_editmenu
idlelib.idle_test.test_editor
idlelib.idle_test.test_filelist
idlelib.idle_test.test_format
idlelib.idle_test.test_grep
idlelib.idle_test.test_help
idlelib.idle_test.test_help_about
idlelib.idle_test.test_history
idlelib.idle_test.test_hyperparser
idlelib.idle_test.test_iomenu
idlelib.idle_test.test_macosx
idlelib.idle_test.test_mainmenu
idlelib.idle_test.test_multicall
idlelib.idle_test.test_outwin
idlelib.idle_test.test_parenmatch
idlelib.idle_test.test_pathbrowser
idlelib.idle_test.test_percolator
idlelib.idle_test.test_pyparse
idlelib.idle_test.test_pyshell
idlelib.idle_test.test_query
idlelib.idle_test.test_redirector
idlelib.idle_test.test_replace
idlelib.idle_test.test_rpc
idlelib.idle_test.test_run
idlelib.idle_test.test_runscript
idlelib.idle_test.test_scrolledlist
idlelib.idle_test.test_search
idlelib.idle_test.test_searchbase
idlelib.idle_test.test_searchengine
idlelib.idle_test.test_sidebar
idlelib.idle_test.test_squeezer
idlelib.idle_test.test_stackviewer
idlelib.idle_test.test_statusbar
idlelib.idle_test.test_text
idlelib.idle_test.test_textview
idlelib.idle_test.test_tooltip
idlelib.idle_test.test_tree
idlelib.idle_test.test_undo
idlelib.idle_test.test_warning
idlelib.idle_test.test_window
idlelib.idle_test.test_zoomheight
idlelib.iomenu
idlelib.macosx
idlelib.mainmenu
idlelib.multicall
idlelib.outwin
idlelib.parenmatch
idlelib.pathbrowser
idlelib.percolator
idlelib.pyparse
idlelib.pyshell
idlelib.query
idlelib.redirector
idlelib.replace
idlelib.rpc
idlelib.run
idlelib.runscript
idlelib.scrolledlist
idlelib.search
idlelib.searchbase
idlelib.searchengine
idlelib.sidebar
idlelib.squeezer
idlelib.stackviewer
idlelib.statusbar
idlelib.textview
idlelib.tooltip
idlelib.tree
idlelib.undo
idlelib.window
idlelib.zoomheight
idlelib.zzdummy
imaplib
imghdr
imp
importlib
importlib._bootstrap
importlib._bootstrap_external
importlib._common
importlib.abc
importlib.machinery
importlib.metadata
importlib.resources
importlib.util
inspect
io
ipaddress
itertools
json
json.decoder
json.encoder
json.scanner
json.tool
keyword
lib.libpython3
lib2to3
lib2to3.btm_matcher
lib2to3.btm_utils
lib2to3.fixer_base
lib2to3.fixer_util
lib2to3.fixes
lib2to3.fixes.fix_apply
lib2to3.fixes.fix_asserts
lib2to3.fixes.fix_basestring
lib2to3.fixes.fix_buffer
lib2to3.fixes.fix_dict
lib2to3.fixes.fix_except
lib2to3.fixes.fix_exec
lib2to3.fixes.fix_execfile
lib2to3.fixes.fix_exitfunc
lib2to3.fixes.fix_filter
lib2to3.fixes.fix_funcattrs
lib2to3.fixes.fix_future
lib2to3.fixes.fix_getcwdu
lib2to3.fixes.fix_has_key
lib2to3.fixes.fix_idioms
lib2to3.fixes.fix_import
lib2to3.fixes.fix_imports
lib2to3.fixes.fix_imports2
lib2to3.fixes.fix_input
lib2to3.fixes.fix_intern
lib2to3.fixes.fix_isinstance
lib2to3.fixes.fix_itertools
lib2to3.fixes.fix_itertools_imports
lib2to3.fixes.fix_long
lib2to3.fixes.fix_map
lib2to3.fixes.fix_metaclass
lib2to3.fixes.fix_methodattrs
lib2to3.fixes.fix_ne
lib2to3.fixes.fix_next
lib2to3.fixes.fix_nonzero
lib2to3.fixes.fix_numliterals
lib2to3.fixes.fix_operator
lib2to3.fixes.fix_paren
lib2to3.fixes.fix_print
lib2to3.fixes.fix_raise
lib2to3.fixes.fix_raw_input
lib2to3.fixes.fix_reduce
lib2to3.fixes.fix_reload
lib2to3.fixes.fix_renames
lib2to3.fixes.fix_repr
lib2to3.fixes.fix_set_literal
lib2to3.fixes.fix_standarderror
lib2to3.fixes.fix_sys_exc
lib2to3.fixes.fix_throw
lib2to3.fixes.fix_tuple_params
lib2to3.fixes.fix_types
lib2to3.fixes.fix_unicode
lib2to3.fixes.fix_urllib
lib2to3.fixes.fix_ws_comma
lib2to3.fixes.fix_xrange
lib2to3.fixes.fix_xreadlines
lib2to3.fixes.fix_zip
lib2to3.main
lib2to3.patcomp
lib2to3.pgen2
lib2to3.pgen2.conv
lib2to3.pgen2.driver
lib2to3.pgen2.grammar
lib2to3.pgen2.literals
lib2to3.pgen2.parse
lib2to3.pgen2.pgen
lib2to3.pgen2.token
lib2to3.pgen2.tokenize
lib2to3.pygram
lib2to3.pytree
lib2to3.refactor
lib2to3.tests
lib2to3.tests.data.bom
lib2to3.tests.data.crlf
lib2to3.tests.data.different_encoding
lib2to3.tests.data.false_encoding
lib2to3.tests.data.fixers.bad_order
lib2to3.tests.data.fixers.myfixes
lib2to3.tests.data.fixers.myfixes.fix_explicit
lib2to3.tests.data.fixers.myfixes.fix_first
lib2to3.tests.data.fixers.myfixes.fix_last
lib2to3.tests.data.fixers.myfixes.fix_parrot
lib2to3.tests.data.fixers.myfixes.fix_preorder
lib2to3.tests.data.fixers.no_fixer_cls
lib2to3.tests.data.fixers.parrot_example
lib2to3.tests.data.infinite_recursion
lib2to3.tests.data.py2_test_grammar
lib2to3.tests.data.py3_test_grammar
lib2to3.tests.pytree_idempotency
lib2to3.tests.support
lib2to3.tests.test_all_fixers
lib2to3.tests.test_fixers
lib2to3.tests.test_main
lib2to3.tests.test_parser
lib2to3.tests.test_pytree
lib2to3.tests.test_refactor
lib2to3.tests.test_util
linecache
locale
logging
logging.config
logging.handlers
lzma
mailbox
mailcap
marshal
math
mimetypes
mmap
modulefinder
msilib
msvcrt
multiprocessing
multiprocessing.connection
multiprocessing.context
multiprocessing.dummy
multiprocessing.dummy.connection
multiprocessing.forkserver
multiprocessing.heap
multiprocessing.managers
multiprocessing.pool
multiprocessing.popen_fork
multiprocessing.popen_forkserver
multiprocessing.popen_spawn_posix
multiprocessing.popen_spawn_win32
multiprocessing.process
multiprocessing.queues
multiprocessing.reduction
multiprocessing.resource_sharer
multiprocessing.resource_tracker
multiprocessing.shared_memory
multiprocessing.sharedctypes
multiprocessing.spawn
multiprocessing.synchronize
multiprocessing.util
netrc
nis
nntplib
ntpath
nturl2path
numbers
opcode
operator
optparse
os
os.path
ossaudiodev
parser
pathlib
pdb
pickle
pickletools
pipes
pkgutil
platform
plistlib
poplib
posix
posixpath
pprint
profile
pstats
pty
pwd
py_compile
pyclbr
pydoc
pydoc_data
pydoc_data.topics
queue
quopri
random
re
readline
reprlib
resource
rlcompleter
runpy
sched
secrets
select
selectors
shelve
shlex
shutil
signal
site
smtpd
smtplib
sndhdr
socket
socketserver
spwd
sqlite3
sqlite3.dbapi2
sqlite3.dump
sre_compile
sre_constants
sre_parse
ssl
stat
statistics
string
stringprep
struct
subprocess
sunau
symbol
symtable
sys
sysconfig
syslog
tabnanny
tarfile
telnetlib
tempfile
termios
test
test.support
test.support.bytecode_helper
test.support.hashlib_helper
test.support.logging_helper
test.support.script_helper
test.support.socket_helper
test.support.testresult
test.test_script_helper
test.test_support
textwrap
this
threading
time
timeit
tkinter
tkinter.colorchooser
tkinter.commondialog
tkinter.constants
tkinter.dialog
tkinter.dnd
tkinter.filedialog
tkinter.font
tkinter.messagebox
tkinter.scrolledtext
tkinter.simpledialog
tkinter.tix
tkinter.ttk
token
tokenize
trace
traceback
tracemalloc
tty
turtle
turtledemo
turtledemo.bytedesign
turtledemo.chaos
turtledemo.clock
turtledemo.colormixer
turtledemo.forest
turtledemo.fractalcurves
turtledemo.lindenmayer
turtledemo.minimal_hanoi
turtledemo.nim
turtledemo.paint
turtledemo.peace
turtledemo.penrose
turtledemo.planet_and_moon
turtledemo.rosette
turtledemo.round_dance
turtledemo.sorting_animate
turtledemo.tree
turtledemo.two_canvases
turtledemo.yinyang
types
typing
unicodedata
unittest
unittest._log
unittest.async_case
unittest.case
unittest.loader
unittest.main
unittest.mock
unittest.result
unittest.runner
unittest.signals
unittest.suite
unittest.util
urllib
urllib.error
urllib.parse
urllib.request
urllib.response
urllib.robotparser
uu
uuid
venv
warnings
wave
weakref
webbrowser
winreg
winsound
wsgiref
wsgiref.handlers
wsgiref.headers
wsgiref.simple_server
wsgiref.util
wsgiref.validate
xdrlib
xml
xml.dom
xml.dom.NodeFilter
xml.dom.domreg
xml.dom.expatbuilder
xml.dom.minicompat
xml.dom.minidom
xml.dom.pulldom
xml.dom.xmlbuilder
xml.etree
xml.etree.ElementInclude
xml.etree.ElementPath
xml.etree.ElementTree
xml.etree.cElementTree
xml.parsers
xml.parsers.expat
xml.parsers.expat.errors
xml.parsers.expat.model
xml.sax
xml.sax._exceptions
xml.sax.expatreader
xml.sax.handler
xml.sax.saxutils
xml.sax.xmlreader
xmlrpc
xmlrpc.client
xmlrpc.server
zipapp
zipfile
zipimport
zlib
zoneinfo
zoneinfo._common
zoneinfo._tzpath
zoneinfo._zoneinfo"""

MODULES = frozenset(MODULES.splitlines())

def change_context(func):
    def inner(self, node):
        self._enter_ctx(node)
        ret = self.generic_visit(node)
        self._exit_ctx()
        return ret
    return inner
    
def process_package(directory):
    number = Counter()
    for file in directory.glob("**/*.py"):
        try:
            with tokenize.open(file) as stream:
                tree = ast.parse(stream.read())
        except:
            continue
        for call in filter(lambda node: isinstance(node, ast.Call), ast.walk(tree)):
            if type(call.func) is ast.Attribute and type(call.func.value) is ast.Name and call.func.value.id in MODULES:
                number[call.func.value.id + call.func.attr] += 1

    return number

def process_packages(directory):
    number = Counter()
    for index, package in enumerate(directory.iterdir(), 1):
        if package.is_dir():
            number.update(process_package(package))
        if index % 50 == 0:
            print(', '.join(f'{k} ({v})' for k, v in number.most_common(10)))
    return number

results = process_packages(Path("disk/rawdata/clean/"))
with open("func_res", "w") as f:
    f.write(repr(results))
