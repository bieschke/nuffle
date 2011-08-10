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

import os
import urllib
from basefilter import BaseFilter


class StaticFilter(BaseFilter):
    """Filter that handles static content."""
    
    def beforeMain(self):
        from cherrypy import config, request
        from cherrypy.lib import cptools
        
        if not config.get('staticFilter.on', False):
            return
        
        regex = config.get('staticFilter.match', '')
        if regex:
            import re
            if not re.search(regex, request.path):
                return
        
        filename = config.get('staticFilter.file')
        if not filename:
            staticDir = config.get('staticFilter.dir')
            section = config.get('staticFilter.dir', returnSection=True)
            if section == 'global':
                section = "/"
            section = section.rstrip(r"\/")
            extraPath = request.path[len(section) + 1:]
            extraPath = extraPath.lstrip(r"\/")
            extraPath = urllib.unquote(extraPath)
            filename = os.path.join(staticDir, extraPath)
        
        # If filename is relative, make absolute using "root".
        if not os.path.isabs(filename):
            root = config.get('staticFilter.root', '').rstrip(r"\/")
            if root:
                filename = os.path.join(root, filename)
        
        cptools.serveFile(filename)

