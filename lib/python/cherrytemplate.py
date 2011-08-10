"""
Copyright (c) 2004, CherryPy Team (team@cherrypy.org)
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
    * Neither the name of the CherryPy Team nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

__version__ = '1.1.1-beta'

import sys, StringIO, inspect, os, time
import copy

default_input_encoding = None
default_output_encoding = None
default_output_encoding_errors = 'replace'
path = ['.']
default_return_generator = False

_cache = {}

_quote3 = '"""'

class RenderError(Exception): pass
class ParseError(Exception): pass
class InternalError(Exception): pass
class FileNotFoundError(Exception): pass

def _findClosingQuote(str, quote, startIndex, beforeNewline=1):
    while 1:
        i=str.find(quote, startIndex)
        if i==-1: raise ParseError, "No closing '%s' for string '%s ...'" % (quote, str[startIndex:startIndex+20])
        elif str[i-1] == '\\':
            startIndex = i+1
            continue
        if beforeNewline:
            j=str.find('\n', startIndex)
            if j!=-1 and j<i:
                raise ParseError, "No closing '%s' for string '%s ...' before the end of the line" % (quote, str[startIndex:j])
        return i

def _findEndOfTag(str, startIndex, beforeNewline=1):
    i = _findClosingQuote(str, '"', str.find('"', startIndex)+1, beforeNewline)
    if str[i+1]=='>': end = i+1
    elif str[i+1:i+3]=='/>': end = i+2
    elif str[i+1:i+4]==' />': end = i+3
    else:
        raise ParseError, "No closing '%s' for string '%s ...'"%('">', str[startIndex:startIndex+20])
    if beforeNewline:
        j=str.find('\n', startIndex)
        if j!=-1 and j<i:
            raise ParseError, "No closing '%s' for string '%s ...' before the end of the line"%('">', str[startIndex:j])
    return (i, end)

def _findEndOfPyCode(str, startIndex):
    i = startIndex
    while 1:
        i = _findClosingQuote(str, '>', i+1, 0)
        if i == -1:
            raise ParseError, "No closing '%s' for string '%s ...'"%('">', str[startIndex:startIndex+20])
        elif str[i-1:i+1] == '">':
            return (i-1, i)
        elif str[i-2:i+1] == '"/>':
            return (i-2, i)
        elif str[i-3:i+1] == '" />':
            return (i-3, i)

def _findClosingTag(template, openingTag, closingTag, openTagCount, startIndex, text):
    if openTagCount < 0:
        raise ParseError, \
            "Too many closing tags '%s' for '%s ... %s ...'" % (
                closingTag, openingTag, text
            )
    i = template.find(openingTag, startIndex)
    j = template.find(closingTag, startIndex)
    if j == -1: raise ParseError, "No matching '%s' tag for '%s ... %s ...'"%(closingTag, openingTag, text)
    if i == -1 or j < i: # closingTag is first
        if openTagCount == 0:
            return j # found it !
        return _findClosingTag(template, openingTag, closingTag, openTagCount-1, j+1, text)
    else: # openingTag is first
        return _findClosingTag(template, openingTag, closingTag, openTagCount+1, i+1, text)

def _findClosingDiv(template, startIndex, text):
    return _findClosingTag(template, '<div', '</div>', 0, startIndex, text)

def _findClosingPyFor(template, startIndex, text):
    return _findClosingTag(template, '<py-for', '</py-for>', 0, startIndex, text)

def _findClosingPyIf(template, startIndex, text):
    return _findClosingTag(template, '<py-if', '</py-if>', 0, startIndex, text)

def _findClosingPyElse(template, startIndex, text):
    return _findClosingTag(template, '<py-else', '</py-else>', 0, startIndex, text)

def _writeInTripleQuotes(f, str, tab):
    if str:
        str=str.replace('\\', '\\\\').replace('"""', '\\"""')
        if str[0]=='"': str='\\'+str
        if str[-1]=='"': str=str[:-1]+'\\"'
        if isinstance(str, unicode):
            unicodePrefix = 'u'
        else:
            unicodePrefix = ''
        f.write( tab + "yield " + unicodePrefix + _quote3 + str + _quote3 + "\n")

def _getTemplateFile(filename, path):
    if os.path.isabs(filename):
        return open(filename, 'rb').read()
    for dir in path:
        newfilename = os.path.join(dir, filename)
        if os.path.exists(newfilename):
            return open(newfilename, 'rb').read()
    raise FileNotFoundError(filename, path)
    
    

def _expandPyInclude(template, path, loop=0):
    if loop>100:
        raise ParseError, "Infinite loop in 'py-include'"
    i=template.find("py-include")
    if i==-1: return template
    if template[i+10:i+12]!='="':
        raise ParseError, "Tag 'py-include' should be followed by '=\"'"
    j,end=_findEndOfTag(template, i)

    # Read template file
    templateFilename = template[i+12:j]
    templateData = _getTemplateFile(templateFilename, path)

    # Replace py-include tag with template file
    if i>0 and template[i-1]=='<':
        # CGTL tag (<py-include)
        i=i-1
        j=end
    else:
        if i>=5 and template[i-5:i]=='<div ':
            # CHTL tag (<div py-include)
            j=_findClosingDiv(template, i, templateFilename)
            i=i-5
            j=j+5
        else:
            raise ParseError, "'py-include' tag can be used either as '<py-include=\"...\">' or '<div py-include=\"...\">...</div>'"

    template = template[:i] + templateData + template[j+1:]
    template=_expandPyInclude(template, path, loop+1)
    return template

def _firstNonSpace(s):
    i = 0
    while i < len(s) and s[i] == ' ':
        i += 1
    return i

def _writeTemplate(f, template, tab):
    # New cherrytemplate syntax
    tagList = ['<%--', '<%=', '<%']
    minI = len(template)
    minTag = ""
    for tag in tagList:
        i = template.find(tag)
        if i == -1: continue
        if i < minI:
            minI = i
            minTag = tag

    if minTag == '<%':
        j = _findClosingTag(template, '<%', '%>', 0, minI + 1, '')
        execStr = template[minI+2:j]
        # Try to indent execStr correctly
        lines=[]
        minIndent=1000
        lastIndent=0
        for line in execStr.split('\n'):
            if line.split():
                sLine = line.strip()
                indentCount = _firstNonSpace(line)
                lastIndent = indentCount
                if sLine[-1] == ':':
                    lastIndent += 4
                if indentCount < minIndent:
                    minIndent = indentCount
                lines.append(line)
        if minIndent==1000: minIndent=0
        lastIndent -= minIndent

        _writeTemplate(f, template[:minI], tab)
        lastLineIndent = ''
        isEnd = False
        if len(lines) == 1:
            sLine = lines[0].strip()
            if sLine.startswith('# end') or sLine.startswith('#end'):
                isEnd = True
                tab = tab[4:]
        if not isEnd:
            for line in lines:
                f.write(tab + line[minIndent:] + '\n')
        _writeTemplate(f, template[j+2:], tab + ' ' * lastIndent)
        return

    elif minTag == '<%=':
        j = _findClosingTag(template, '<%=', '%>', 0, minI + 1, '')
        evalStr = template[minI+3:j]
        _writeInTripleQuotes(f, template[:minI], tab)
        f.write(tab+'yield %s\n' % evalStr)
        _writeTemplate(f, template[j+2:], tab)
        return

    elif minTag == '<%--':
        j = _findClosingTag(template, '<%--', '--%>', 0, minI + 1, '')
        _writeInTripleQuotes(f, template[:minI], tab)
        _writeTemplate(f, template[j+2:], tab)
        return

    # Old cherrytemplate syntax
    tagList=['py-eval', 'py-exec', 'py-code', 'py-attr', 'py-if', 'py-for']
    minI=len(template)
    minTag=""
    for tag in tagList:
        i=template.find(tag+'="')
        if i==-1: continue
        if i<minI:
            minI=i
            minTag=tag
    if not minTag:
        # Check that no tags are left without '='
        # This catches common mistake: 'py-if "1==1"' instead of 'py-if="1==1"'
        if not minTag: minI=-1
        for tag in tagList:
            if template[:minI].find(tag) !=-1:
                raise ParseError, "Tag '%s' should be followed by '=\"'"%(tag)
        # Check that no "py-else" are left:
        if not minTag and template.find("py-else")!=-1:
            raise ParseError, "Tag 'py-else' found without corresponding 'py-if'"
        if not minTag:
            _writeInTripleQuotes(f, template, tab)
    if minTag=='py-eval':
        j,maxI=_findEndOfTag(template, minI)
        evalStr=template[minI+9:j]

        if minI>0 and template[minI-1]=='<':

            # CGTL tag (<py-eval)
            _writeInTripleQuotes(f, template[:minI-1], tab)
            f.write(tab+'yield %s\n' % evalStr)
            _writeTemplate(f, template[maxI+1:], tab)

        else:

            # CHTL tag (<div py-eval)
            j2=template.find('<', j)
            # Check if we have a special <div, just for the py-eval
            if minI>=5 and template[minI-5:minI]=='<div ':
                # Special case for <div py-eval="i+2">Dummy</div>: remove <div and </div in that case
                j3=_findClosingDiv(template, minI, evalStr)
                _writeInTripleQuotes(f, template[:minI-5], tab)
                f.write(tab+'yield %s\n'%evalStr)
                _writeTemplate(f, template[j3+6:], tab)
            else:
                _writeInTripleQuotes(f, template[:minI-1]+'>', tab)
                f.write(tab+'yield %s\n'%evalStr)
                _writeTemplate(f, template[j2:], tab)

    elif minTag=='py-attr':
        j=_findClosingQuote(template, '"', minI+9)

        j2a=template.find('="', j)
        if j2a==-1: j2a=len(template)
        j2b=template.find("='", j)
        if j2b==-1: j2b=len(template)
        if j2a<j2b:
            j2=j2a
            j3=template.find('"', j2+2)
        else:
            j2=j2b
            j3=template.find("'", j2+2)
        evalStr=template[minI+9:j]
        _writeInTripleQuotes(f, template[:minI-1]+template[j+1:j2+2], tab)
        f.write(tab+'yield %s\n'%evalStr)
        _writeTemplate(f, template[j3:], tab)

    elif minTag=='py-exec':
        j,maxI=_findEndOfTag(template, minI)

        execStr=template[minI+9:j]

        if minI>0 and template[minI-1]=='<':

            # CGTL tag(<py-exec)
            _writeInTripleQuotes(f, template[:minI-1], tab)
            f.write(tab+execStr+'\n')
            _writeTemplate(f, template[maxI+1:], tab)

        else:

            # CHTL tag(<div py-exec)

            # Check that we have a </div> after the command
            if template[j+2:j+2+6]!='</div>':
                raise ParseError, "'<div py-exec=%s' is not closed with '</div>'"%execStr

            j0=template.rfind('<div', 0, minI)
            j2=template.find('</div>', j0)
            _writeInTripleQuotes(f, template[:j0], tab)
            f.write(tab+execStr+'\n')
            _writeTemplate(f, template[j2+6:], tab)

    elif minTag=='py-code':
        # Has to be used like:
        # <div py-code="
        #    i=1
        #    yield "%s 2"%i
        # ">
        if template[minI+9]!='\n':
            raise ParseError, "'py-code=\"' must be followed by a newline"
        j,maxI=_findEndOfPyCode(template, minI)

        execStr=template[minI+10:j]
        # Try to indent execStr correctly
        lines=[]
        minIndent=1000
        for line in execStr.split('\n'):
            if line.split():
                indentCount = 0
                while indentCount < len(line) and line[indentCount:indentCount+4] == '    ': indentCount += 4
                if indentCount < minIndent: minIndent=indentCount
                lines.append(line)
        if minIndent==1000: minIndent=0

        if minI>0 and template[minI-1]=='<':

            # CGTL tag(<py-code)
            _writeInTripleQuotes(f, template[:minI-1], tab)
            for line in lines:
                # Remove "minIndent" tabs and add "tab" tabs from each line
                f.write(tab+line[minIndent:]+'\n')
            _writeTemplate(f, template[maxI+1:], tab)

        else:

            # CHTL tag(<div py-code)

            # Check that we have a </div> after the command
            if template[j+2:j+2+6]!='</div>':
                raise ParseError, "'<div py-code=%s' is not closed with '</div>'"%execStr

            j0=template.rfind('<div', 0, minI)
            j2=template.find('</div>', j0)
            _writeInTripleQuotes(f, template[:j0], tab)
            for line in lines:
                # Remove "minIndent" tabs and add "tab" tabs from each line
                f.write(tab+line[minIndent:]+'\n')
            _writeTemplate(f, template[j2+6:], tab)

    elif minTag=='py-for':
        j=_findClosingQuote(template, '">', minI)

        forStr=template[minI+8:j]

        if minI>0 and template[minI-1]=='<':

            # CGTL (<py-for ... </py-for>)
            j2=_findClosingPyFor(template, j, forStr)
            text=template[j+2:j2]
            _writeInTripleQuotes(f, template[:minI-1], tab)
            try:
                forStr.split(' in ')[1]
            except IndexError:
                raise ParseError, "py-for string '%s' is not correct"%forStr
            f.write(tab+'for '+forStr+':\n')
            _writeTemplate(f, text, tab+'    ')
            _writeTemplate(f, template[j2+9:], tab)

        else:

            # CHTL (<div py-for ... </div>)
            j0=template.rfind('<div', 0, minI)
            # Find matching </div> (warning: could be nested)
            j2=_findClosingDiv(template, j0+1, forStr)
            text=template[j+2:j2]
            _writeInTripleQuotes(f, template[:j0], tab)
            try:
                forStr.split(' in ')[1]
            except IndexError:
                raise ParseError, "py-for string '%s' is not correct"%forStr
            f.write(tab+'for '+forStr+':\n')
            _writeTemplate(f, text, tab+'    ')
            _writeTemplate(f, template[j2+6:], tab)

    elif minTag=='py-if':
        j=_findClosingQuote(template, '">', minI)

        ifStr=template[minI+7:j]

        if minI>0 and template[minI-1]=='<':

            # CGTL (<py-if ... </py-if>   <py-else>...</py-else>)
            j2=_findClosingPyIf(template, j, ifStr)
            ifText=template[j+2:j2]
            # Check if there is a <py-else>
            k=j2+8 # k will be the index of the next significant character after </py-if>
            while k<len(template):
                if '    \r\n '.find(template[k])==-1: break
                k+=1
            if k!=len(template) and template[k:k+9]=='<py-else>':
                j3=_findClosingPyElse(template, k+9, ifStr+" else ")
                elseText=template[k+9:j3]
                j4=j3+10
            else:
                elseText=""
                j4=j2+8
            #print "ifStr:",ifStr
            _writeInTripleQuotes(f, template[:minI-1], tab)
            f.write(tab+'if %s:\n'%ifStr)
            _writeTemplate(f, ifText, tab+'    ')
            if elseText:
                f.write(tab+'else:\n')
                _writeTemplate(f, elseText, tab+'    ')
            _writeTemplate(f, template[j4:], tab)

        else:

            # CHTL (<div py-if ... </div>   <div py-else>...</div>)
            j0=template.rfind('<div', 0, minI)
            # Find matching </div> (warning: could be nested)
            j2=_findClosingDiv(template, j0+1, ifStr)
            ifText=template[j+2:j2]
            # Check if there is a py-else>
            k=j2+6 # k will be the index of the next significant character after </div>
            while k<len(template):
                if '    \r\n '.find(template[k])==-1: break
                k+=1
            if k!=len(template) and template[k:k+13]=='<div py-else>':
                j3=_findClosingDiv(template, k+13, ifStr+" else ")
                elseText=template[k+13:j3]
            else:
                elseText=""
                j3=j2
            #print "ifStr:",ifStr
            _writeInTripleQuotes(f, template[:j0], tab)
            f.write(tab+'if %s:\n'%ifStr)
            _writeTemplate(f, ifText, tab+'    ')
            if elseText:
                f.write(tab+'else:\n')
                _writeTemplate(f, elseText, tab+'    ')
            _writeTemplate(f, template[j3+6:], tab)

    elif minTag:
        raise InternalError(minTag)

def render(template = '', file = None, input_encoding = None, output_encoding = None, output_encoding_errors = None, return_generator = None, glob = None, loc = None, log_func = None):
    # print "* Rendering:", file
    t0 = time.time()

    cache_key = template or file
    _render_template_code = _cache.get(cache_key)

    if not _render_template_code:
        originalTemplate = template
        if file != None:
            template = _getTemplateFile(file, path)
        # Expand py-include
        template = _expandPyInclude(template, path)
        template = template.replace('\r\n', '\n')
        f = StringIO.StringIO()
        f.write("def _render_template():\n")
        _writeTemplate(f, template, '    ')
        _render_template_code = f.getvalue()
        _cache[cache_key] = _render_template_code

    if loc is None:
        loc = inspect.currentframe(1).f_locals
    if glob is None:
        glob = inspect.currentframe(1).f_globals
    g = glob.copy() # make a copy because we don't want to avoid changing original global scope.
    g.update(loc) # add local vars to global scope g to allow access from within template.
    
    try:
        exec(_render_template_code, g)
    except:
        # In case of an exception, we include the body of the template in
        #   the traceback
        import sys, traceback
        tb = "".join(traceback.format_exception(*sys.exc_info()))
        errorList = ["An error occured while trying to render a template."]
        if file is not None:
            errorList.append("The template file was %s" % repr(file))
        errorList.append("The traceback was:")
        errorList.append(_indentAndNumberCode(tb, number = False))
        errorList.append("The template code was:")
        errorList.append(_indentAndNumberCode(template))
        if file is None:
            errorList.append("The original template was:")
            errorList.append(_indentAndNumberCode(originalTemplate, number = False))
        raise RenderError, '\n'.join(errorList)

    if output_encoding == None:
        output_encoding = default_output_encoding
    if output_encoding_errors == None:
        output_encoding_errors = default_output_encoding_errors
    input_encoding = input_encoding
    if input_encoding == None:
        input_encoding = default_input_encoding
    if return_generator == None:
        return_generator = default_return_generator

    try:
        result = eval('_render_template()',g)

        if return_generator:
            return _resultAsGenerator(result, input_encoding, output_encoding, output_encoding_errors)
        else:
            result = ''.join(list(result))
            if not isinstance(result, unicode):
                if input_encoding:
                    result = unicode(result, input_encoding)
            if output_encoding:
                return result.encode(output_encoding, output_encoding_errors)
            if log_func:
                log_func("Rendered file %s in %.02fs" % (
                    file, time.time() - t0))
            return result
    except:
        # In case of an exception, we include the body of the template in
        #   the traceback
        import sys, traceback
        tb = "".join(traceback.format_exception(*sys.exc_info()))
        errorList = ["An error occured while trying to render a template."]
        if file is not None:
            errorList.append("The template file was %s" % repr(file))
        errorList.append("The traceback was:")
        errorList.append(_indentAndNumberCode(tb, number = False))
        errorList.append("The template code was:")
        errorList.append(_indentAndNumberCode(template))
        if file is None:
            errorList.append("The original template was:")
            errorList.append(_indentAndNumberCode(originalTemplate, number = False))
        raise RenderError, '\n'.join(errorList)

renderTemplate = render # legacy API

def _resultAsGenerator(result, input_encoding, output_encoding, output_encoding_errors):
        for line in result:
            if not isinstance(line, unicode):
                if input_encoding:
                    line = unicode(line, input_encoding)
            if output_encoding:
                yield line.encode(output_encoding, output_encoding_errors)
            yield line
            if log_func:
                log_func("Rendered file %s in %.02fs" % (
                    file, time.time() - t0))

def _indentAndNumberCode(code, number = True, tab = '    '):
    resList = []
    for i, line in enumerate(code.splitlines()):
        if number:
            line = '%05d' % (i+1) + ' ' + line
        resList.append(tab +  line)
    return '\n'.join(resList)
