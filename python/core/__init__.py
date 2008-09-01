# $Id$
"""Core functions of MDAnalysis: The basic class is an AtomGroup; the
whole simulation is called the Universe. Selections are computed on an
AtomGroup and return another AtomGroup. Timeseries are a convenient way to analyse trajectories.

To get started, load the Universe:

  u = Universe(psffilename,dcdfilename)

There are a number flags defined that influence how MDAnalysis
behaves. They are accessible through the pseudo-dictionary

  MDAnalysis.core.flags

The entries appear as 'name'-'value' pairs. Flags check values and
illegal ones raise a ValueError. Documentation on all flags can be obtained with

 print MDAnalysis.core.flags.__doc__
  
"""
__all__ = ['AtomGroup', 'Selection', 'Timeseries', 
           'distances', 'rms_fitting']

# set up flags for core routines
class Flags(dict):
    """Global registry of flags. Acts like a dict for item access.

    There are a number flags defined that influence how MDAnalysis
    behaves. They are accessible through the pseudo-dictionary

      MDAnalysis.core.flags

    The entries appear as 'name'-'value' pairs. Flags check values and
    illegal ones raise a ValueError. Documentation on all flags can be
    obtained with

      print MDAnalysis.core.flags.__doc__

    """
    def __init__(self,*args):
        """Initialize list with a *list* of Flag instances."""
        super(Flags,self).__init__([(flag.name,flag) for flag in args])
    def __doc__():        
        def fget(self): return self.doc()
        return locals()
    __doc__ = property(**__doc__())  # generate dynamic docs on all flags
    def get_flag(self,name):
        return super(Flags,self).__getitem__(name)
    def doc(self):
        """Shows doc strings for all flags."""
        return "\n\n".join([flag.__doc__ for flag in self._itervalues()])
    def append(self,flag):
        super(Flags,self).__setitem__(flag.name,flag)
    def update(self,*flags):
        super(Flags,self).update([(flag.name,flag) for flag in flags])
    def setdefault(self,k,d=None):
        raise NotImplementedError
    def __getitem__(self,name):
        return self.get_flag(name).get()
    def __setitem__(self,name,value):
        self.get_flag(name).set(value)
    def _itervalues(self):
        return super(Flags,self).itervalues()
    def _items(self):
        return super(Flags,self).items()
    def itervalues(self):
        for flag in self._itervalues():
            yield flag.value
    def iteritems(self):
        for flag in self._itervalues():
            yield flag.name,flag.value
    def values(self):
        return [flag.value for flag in self._itervalues()]
    def items(self):
        return [(flag.name,flag.value) for flag in self._itervalues()]
    def __repr__(self):
        return str(self.items())

class IdentityMapping(dict):
    def __getitem__(self,key):
        return key

class Flag(object):
    def __init__(self,name,default,mapping=None,doc=None):        
        self.name = name
        self.value = default
        self.default = default
        # {v1:v1,v2:v1,v3:v3, ...} mapping of allowed values to canonical ones
        self.mapping = mapping or IdentityMapping()
        if doc is not None:
            self.__doc__ = doc % self.__dict__
    def get(self):
        return self.value
    def set(self,value):
        if value is None:
            pass
        else:
            try:
                self.value = self.mapping[value]
            except KeyError:
                raise ValueError("flag must be None or one of "+str(self.mapping.keys()))
        return self.get()
    def __repr__(self):
        return """Flag('%(name)s',%(value)r)""" % self.__dict__
    def prop(self):
        """Use this for property(**flag.prop())"""
        return {'fget':self.get, 'fset':self.set, 'doc':self.__doc__}

_flags = [
    Flag('use_periodic_selections',
         True,
         {True:True,False:False},
         """%(name)s - determines if distance selections (AROUND, POINT) respect periodicity.
            >>> flags['%(name)s'] = value

            Values of flag:
            None     - show current value of the flag
            True     - periodicity is taken into account if supported
            False    - periodicity is ignored

            The MDAnalysis preset of this flag is %(default)r.

            Note that KD-tree based distance selections always ignore this
            flag. (For details see the doc for MDAnalysis.core.use_KDTree_routines.)
            """
         ),
    Flag('use_KDTree_routines',
         'fast',
         {True:'fast','fast':'fast',   # only KDTree if advantageous
          'always':'always',           # always even if slower (for testing)
          False:'never','never':'never'},  # never, only use (slower) alternatives
         """%(name)s - determines which KDTree routines are used for distance selections
    
            >>> flags['%(name)s'] = value

            Values for flag:

            None           - just return the current value
            True, 'fast'   - only use KDTree routines that are typically faster than others
            'always'       - always use KDTree routines where available (eg for benchmarking)
            False, 'never' - always use alternatives

            The preset value for MDAnalysis is %(default)r.

            KDTree routines are significantly faster for some distance
            selections. However, they cannot deal with periodic boxes and thus
            ignore periodicity; if periodicity is crucial, disable KDTree
            routines with

            >>> MDAnalysis.core.use_KDTree_routines(False)
            """
     ),
    ]

# Global flag registry for core
# Can be accessed like a dictionary and appears to the casual user as such.
flags = Flags(*_flags)
del _flags
