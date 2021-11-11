"""This module provides the NetlistHelper class used by the
NetlistMaker and LadderMaker classes.

Copyright 2020--2021 Michael Hayes, UCECE

"""

from .componentnamer import ComponentNamer


class NetlistHelper(object):

    evalf = False
    
    @property 
    def _node(self):

        if not hasattr(self, '_node_counter'):
            self._node_counter = 0
        ret = self._node_counter
        self._node_counter += 1
        return ret

    def _make_nodes(self, *nodes):

        return [self._node if node is None else node for node in nodes]
    
    def _make_name(self, kind):
        """Make identifier"""

        if not hasattr(self, '_namer'):
            self._namer = ComponentNamer()

        return self._namer.name(kind, '')

    def _make_id(self, kind):
        """Make identifier"""

        # Perhaps the names should try to follow the value names, say
        # when generated by the random network generator?  This will
        # avoid confusion.
        if not hasattr(self, '_namer'):
            self._namer = ComponentNamer()

        return self._namer.netid(kind, '')    

    def _netarg(self, arg):

        if self.evalf:
            arg = arg.evalf(n=self.evalf)

        arg = str(arg)

        # TODO: make more robust to catch expressions.
        if ('(' in arg) or (')' in arg) or (' ' in arg) or (',' in arg) or ('*' in arg) or ('/' in arg):
            return '{%s}' % arg
        return arg

    def _netargs(self, net):

        return ' '.join([self._netarg(arg) for arg in net.args])

