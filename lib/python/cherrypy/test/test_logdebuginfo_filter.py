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

import cherrypy

class Root:
    def index(self):
        yield "Hello, world"
    index.exposed = True

    def bug326(self, file):
        return "OK"
    bug326.exposed = True

cherrypy.root = Root()

cherrypy.config.update({
        'session.storageType': 'ram',
        'session.timeout': 60,
        'session.cleanUpDelay': 60,
        'session.cookieName': 'CherryPySession',
        'session.storageFileDir': '',
        
        'server.logToScreen': False,
        'server.environment': 'production',
        'logDebugInfoFilter.on': True,
})



import helper

class LogDebugInfoFilterTest(helper.CPWebCase):
    
    def testLogDebugInfoFilter(self):
        self.getPage('/')
        self.assertInBody('Build time')
        self.assertInBody('Page size')
        # not compatible with the sessionFilter
        #self.assertInBody('Session data size')

    def testBug326(self):
        httpcls = cherrypy.server.httpserverclass
        if httpcls and httpcls.__name__ == "WSGIServer":
            h = [("Content-type", "multipart/form-data; boundary=x"),
                 ("Content-Length", "110")]
            b = """--x
Content-Disposition: form-data; name="file"; filename="hello.txt"
Content-Type: text/plain

hello
--x--
"""
            cherrypy.config.update({
                '/bug326': {'server.maxRequestBodySize': 3,
                            'server.environment': 'development',
                }
            })
            ignore = helper.webtest.ignored_exceptions
            ignore.append(AttributeError)
            try:
                self.getPage('/bug326', h, "POST", b)
                self.assertStatus("413 Request Entity Too Large")
            finally:
                ignore.pop()

if __name__ == "__main__":
    helper.testmain()
