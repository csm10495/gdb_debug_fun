'''
Playing around with GDB and gettings structs from debug info
MIT License - Charles Machalow
'''
from pygdbmi.gdbcontroller import GdbController

class GdbError(RuntimeError):
    pass

class DebugInfo(object):
    def __init__(self, debugFile):
        self.debugFile = debugFile
        self.gdb = GdbController(gdb_args=['-q', self.debugFile])

        # setup an offsetof macro
        self.sendToGdb('macro define offsetof(t, f) &((t *) 0)->f)')

    @classmethod
    def _filterText(cls, txt):
        originalText = txt[:]
        try:
            txt = txt.split('(gdb)')[-1].strip()

            # struct/union definitions
            if txt.startswith('type ='):
                txt = txt.split('type =', 1)[1]

            # sizeof operations
            if txt.startswith("$") and '=' in txt:
                txt = txt.split('=', 1)[1]

            # offsetof operations
            if '(' in txt and ')' in txt and '*' in txt and 'x' in txt:
                txt = txt.split(')')[-1].strip() # gives hex for some reason.

            return txt.strip()
        except:
            pass

        raise GdbError('Unable to filter text: %s' % originalText)

    def sendToGdb(self, cmd):
        response = self.gdb.write(cmd)
        txt = '\n'.join([x['payload'] for x in response])
        return txt

    def getDefinition(self, name):
        txt = self.sendToGdb('ptype %s' % name)
        return self._filterText(txt)

    def getSizeOf(self, name):
        if '.' in name:
            # assume reference to a struct item?
            thing, name = name.split('.', 1)
            name = '((%s*)0)->%s' % (thing, name)

        if '.' in name:
            raise GdbError("It is not supported to have multiple levels of nesting")

        txt = self.sendToGdb('print sizeof(%s)' % name)
        t = self._filterText(txt)
        try:
            return int(t)
        except:
            raise GdbError("Unable to coerce to int: %s" % t)

    def getOffsetOf(self, typ, field):
        txt = self.sendToGdb('print offsetof(%s, %s)' % (typ, field))
        t = self._filterText(txt)
        if 'Cannot access' in t:
            # bitfield?
            raise NotImplementedError("bitfield likely hit. This isn't supported")

        try:
            return int(t, 16)
        except:
            raise GdbError("Unable to coerce to int: %s" % t)

    def getFieldLineFromDefinition(self, typ, field):
        d = self.getDefinition(typ)
        for line in d.splitlines():
            # warning. this is not great logic right now.
            if ' ' + field in line:
                return line

if __name__ == '__main__':
    d = DebugInfo('play')