"""
Copyright (c) 2004, CherryPy Team (team@cherrypy.org)
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, 
are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice, 
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice, 
      this list of conditions and the following disclaimer in the documentation 
      and/or other materials provided with the distribution.
    * Neither the name of the CherryPy Team nor the names of its contributors 
      may be used to endorse or promote products derived from this software 
      without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE 
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

"""
Global module that all modules developing with CherryPy should import.
"""

__version__ = '2.1.0'

import datetime
import sys
import types

from _cperror import *
import config
import _cpserver
server = _cpserver.Server()

codecoverage = False

try:
    from threading import local
except ImportError:
    from cherrypy._cpthreadinglocal import local

# Create a threadlocal object to hold the request and response objects.
# In this way, we can easily dump those objects when we stop/start a
# new HTTP conversation.
serving = local()

class _AttributeDump:
    pass

class _ThreadLocalProxy:
    
    def __init__(self, attrname):
        self.__dict__["__attrname__"] = attrname
    
    def purge__(self):
        """Make a new, emtpy proxied object in cherrypy.serving."""
        setattr(serving, self.__attrname__, _AttributeDump())
    
    def __getattr__(self, name):
        childobject = getattr(serving, self.__attrname__)
        return getattr(childobject, name)
    
    def __setattr__(self, name, value):
        childobject = getattr(serving, self.__attrname__)
        setattr(childobject, name, value)
    
    def __delattr__(self, name):
        childobject = getattr(serving, self.__attrname__)
        delattr(childobject, name)

# Create request and response object (the same objects will be used
#   throughout the entire life of the webserver, but will redirect
#   to the "serving" object)
request = _ThreadLocalProxy('request')
response = _ThreadLocalProxy('response')

# Create threadData object as a thread-specific all-purpose storage
threadData = local()

# Create variables needed for session (see lib/sessionfilter.py for more info)
from lib.filter import sessionfilter
session = sessionfilter.SessionWrapper()
_sessionDataHolder = {} # Needed for RAM sessions only
_sessionLockDict = {} # Needed for RAM sessions only
_sessionLastCleanUpTime = datetime.datetime.now()

def expose(func=None, alias=None):
    """Expose the function, optionally providing an alias or set of aliases."""
    
    def expose_(func):
        func.exposed = True
        if alias is not None:
            if isinstance(alias, basestring):
                parentDict[alias] = func
            else:
                for a in alias:
                    parentDict[a] = func
        return func
    
    parentDict = sys._getframe(1).f_locals
    if isinstance(func, (types.FunctionType, types.MethodType)):
        # expose is being called directly, before the method has been bound
        return expose_(func)
    else:
        # expose is being called as a decorator
        if alias is None:
            alias = func
        return expose_

def log(msg, context='', severity=0):
    """Syntactic sugar for writing to the (error) log."""
    # Load _cputil lazily to avoid circular references, and
    # to allow profiler and coverage tools to work on it.
    import _cputil
    logfunc = _cputil.getSpecialAttribute('_cpLogMessage')
    logfunc(msg, context, severity)

