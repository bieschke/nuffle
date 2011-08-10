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
##########################################################################
## Remco Boerma
##
## History:
## 1.0.4   : 2005-08-28 Fixed issues on input types which are not strings
## 1.0.3   : 2005-01-28 Bugfix on content-length in 1.0.2 code fixed by
##           Gian Paolo Ciceri
## 1.0.2   : 2005-01-26 changed infile dox based on ticket #97
## 1.0.1   : 2005-01-26 Speedup due to generator usage in CP2.
##           The result is now converted to a list with length 1. So the complete
##           xmlrpc result is written at once, and not per character. Thanks to
##           Gian Paolo Ciceri for reporting the slowdown.
## 1.0.0   : 2004-12-29 Released with CP2
## 0.0.9   : 2004-12-23 made it CP2 #59 compatible (returns an iterable)
##           Please note: as the xmlrpc doesn't know what you would want to return
##           (and for the logic of marshalling) it will return Generator objects, as
##           it is.. So it'll brake on that one!!
##           NOTE: __don't try to return a Generator object to the caller__
##           You could of course handle the generator usage internally, before sending
##           the result. This breaks from the general cherrypy way of handling generators...
## 0.0.8   : 2004-12-23 cherrypy.request.paramList should now be a filter. 
## 0.0.7   : 2004-12-07 inserted in the experimental branch (all remco boerma till here)
## 0.0.6   : 2004-12-02 Converted basefilter to baseinputfileter,baseoutputfilter
## 0.0.5   : 2004-11-22 "RPC2/" now changed to "/RPC2/" with the new mapping function
##           Gian paolo ciceri notified me with the lack of passing parameters.
##           Thanks Gian, it's now implemented against the latest trunk.
##           Gian also came up with the idea of lazy content-type checking: if it's sent
##           as a header, it should be 'text/xml', if not sent at all, it should be
##           accepted. (While this it not the xml/rpc standard, it's handy for those
##           xml-rpc client implementations wich don't send this header)
## 0.0.4   : 2004-11-20 in setting the path, the dot is replaces by a slash
##           therefore the regular CP2 routines knows how to handle things, as 
##           dots are not allowed in object names, it's varely easily adopted. 
##           Path + method handling. The default path is 'RPC2', this one is 
##           stripped. In case of path 'someurl' it is used for 'someurl' + method
##           and 'someurl/someotherurl' is mapped to someurl.someotherurl + method.
##           this way python serverproxies initialised with an url other than 
##           just the host are handled well. I don't hope any other service would map
##           it to 'RPC2/someurl/someotherurl', cause then it would break i think. .
## 0.0.3   : 2004-11-19 changed some examples (includes error checking 
##           wich returns marshalled Fault objects if the request is an RPC call.
##           took testing code form afterRequestHeader and put it in 
##           testValidityOfRequest to make things a little simpler. 
##           simply log the requested function with parameters to stdout
## 0.0.2   : 2004-11-19 the required cgi.py patch is no longer needed
##           (thanks remi for noticing). Webbased calls to regular objects
##           are now possible again ;) so it's no longer a dedicated xmlrpc
##           server. The test script is also in a ready to run file named 
##           testRPC.py along with the test server: filterExample.py
## 0.0.1   : 2004-11-19 informing the public, dropping loads of useless
##           tests and debugging
## 0.0.0   : 2004-11-19 initial alpha
## 
##---------------------------------------------------------------------
## 
## EXAMPLE CODE FOR THE SERVER:
##    from cherrypy.lib.filter.xmlrpcfilter import XmlRpcFilter
##    from cherrypy import cherrypy
##
##    class Root:
##        _cpFilterList = [XmlRpcFilter()]
##        
##        def longString(self,s,times):
##            return s*times
##        longString.exposed = True
##
##    cherrypy.root = Root()
##    if __name__=='__main__':
##        cherrypy.server.start(configMap = {'socketPort': 9001,
##                                      'threadPool':0,
##                                      'socketQueueSize':10 })
## EXAMPLE CODE FOR THE CLIENT:
## >>> import xmlrpclib
## >>> server = xmlrpclib.ServerProxy('http://localhost:9001')
## >>> assert server.longString('abc',3) == 'abcabcabc'
## >>>
######################################################################

from basefilter import BaseFilter
import xmlrpclib


class XmlRpcFilter(BaseFilter):
    """Converts XMLRPC to CherryPy2 object system and vice-versa.
    
    PLEASE NOTE:
    
    beforeRequestBody:
        Unmarshalls the posted data to a methodname and parameters.
        - These are stored in cherrypy.request.rpcMethod and .rpcParams
        - The method is also stored in cherrypy.request.path, so CP2 will find
          the right method to call for you, based on the root's position.
    beforeFinalize:
        Marshalls cherrypy.response.body to xmlrpc.
        - Until resolved: cherrypy.response.body must be a python source string;
          this string is 'eval'ed to return the results. This will be
          resolved in the future.
        - Content-Type and Content-Length are set according to the new
          (marshalled) data.
    """
    
    def testValidityOfRequest(self):
        # test if the content-length was sent
        result = False
        if cherrypy.request.headerMap.has_key('Content-Length'):
            length = cherrypy.request.headerMap.get('Content-Length', 0)
            if length is None or length == "": length = 0
            result = int(length) > 0
        ct = 'text/xml'
        if cherrypy.request.headerMap.has_key('Content-Type'):
            ct = cherrypy.request.headerMap.get('Content-Type', 'text/xml').lower()
            if ct is None or ct == "": ct = 'text/xml'
        result = result and ct in ['text/xml']
        return result
    
    def onStartResource(self):
        # We have to dynamically import cherrypy because Python can't handle
        #   circular module imports :-(
        global cherrypy
        import cherrypy
    
    def beforeRequestBody(self):
        """ Called after the request header has been read/parsed"""
        cherrypy.request.xmlRpcFilterOn = cherrypy.config.get('xmlRpcFilter.on', False)
        if not cherrypy.request.xmlRpcFilterOn:
            return True
        
        cherrypy.request.isRPC = self.testValidityOfRequest()
        if not cherrypy.request.isRPC: 
            # used for debugging or more info
            # print 'not a valid xmlrpc call'
            return # break this if it's not for this filter!!
        # used for debugging, or more info:
        # print "xmlrpcmethod...",
        cherrypy.request.processRequestBody = False
        dataLength = int(cherrypy.request.headerMap.get('Content-Length', 0))
        data = cherrypy.request.rfile.read(dataLength)
        try:
            params, method = xmlrpclib.loads(data)
        except Exception:
            params, method = ('ERROR PARAMS', ), 'ERRORMETHOD'
        cherrypy.request.rpcMethod, cherrypy.request.rpcParams = method, params
        # patch the path. there are only a few options:
        # - 'RPC2' + method >> method
        # - 'someurl' + method >> someurl.method
        # - 'someurl/someother' + method >> someurl.someother.method
        if not cherrypy.request.path.endswith('/'):
            cherrypy.request.path += '/'
        if cherrypy.request.path.startswith('/RPC2/'):
            cherrypy.request.path=cherrypy.request.path[5:] ## strip the first /rpc2
        cherrypy.request.path += str(method).replace('.', '/')
        cherrypy.request.paramList = list(params)
        # used for debugging and more info
        # print "XMLRPC Filter: calling '%s' with args: '%s' " % (cherrypy.request.path,params)

    def beforeMain(self):
        """This is a variation of main() from _cphttptools.

        The reason it is redone here is because we don't want
        cherrypy.response.body = iterable(body) - we want to use
        whatever real value the user returned from their callable
        to reach the xmlrpcfilter unchanged."""
        
        if not cherrypy.request.xmlRpcFilterOn:
            return
        
        from cherrypy._cphttptools import mapPathToObject
        path = cherrypy.request.objectPath or cherrypy.request.path
        
        while True:
            try:
                page_handler, object_path, virtual_path = mapPathToObject(path)
                
                # Remove "root" from object_path and join it to get objectPath
                cherrypy.request.objectPath = '/' + '/'.join(object_path[1:])
                args = virtual_path + cherrypy.request.paramList
                body = page_handler(*args, **cherrypy.request.paramMap)
                cherrypy.response.body = body
                return
            except cherrypy.InternalRedirect, x:
                # Try again with the new path
                path = x.path        
    
    def beforeFinalize(self):
        """ Called before finalizing output """
        if (not cherrypy.request.xmlRpcFilterOn
            or not cherrypy.request.isRPC):
            return

        encoding = cherrypy.config.get('xmlRpcFilter.encoding', 'utf-8')
        
        cherrypy.response.body = [xmlrpclib.dumps(
            (cherrypy.response.body,),
            methodresponse=1,
            encoding=encoding,
            allow_none=1)]
        cherrypy.response.headerMap['Content-Type'] = 'text/xml'
        cherrypy.response.headerMap['Content-Length'] = `len(cherrypy.response.body)`
    
    def beforeErrorResponse(self):
        try:
            if not cherrypy.request.xmlRpcFilterOn:
                return
            body = ''.join([chunk for chunk in cherrypy.response.body])
            cherrypy.response.body = [xmlrpclib.dumps(xmlrpclib.Fault(1, body))]
        except:
            pass
