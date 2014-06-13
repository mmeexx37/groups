# -*- coding: utf-8 -*-
import itertools
import re
from   closure     import closure2A
from   permutation import Permutation

__all__ = ["group",
	   "Cyclic", "Semidirect", "DirectProduct", "Dicyclic", "Quaternion",
	   "Dihedral", "Trivial", "Klein4", "AutCyclic", "HolCyclic",
	   "CycSemiCyc", "Symmetric",
	   "Group", "Element",
	   "isHomomorphism"]

class group(object):
    paramNames = None

    def __init__(self, *args):
	if self.paramNames is None:
	    raise NotImplementedError('paramNames is not defined')
	qty = len(paramNames)
	if len(args) != qty:
	    raise TypeError('Constructor takes exactly %d argument%s'
			     % (qty, 's' if qty != 1 else ''))
	self.params = args
	for n,p in zip(params, args):
	    setattr(self, n, p)

    def identity(self):    raise NotImplementedError
    def oper(self,x,y):    raise NotImplementedError
    def invert(self,x):    raise NotImplementedError
    def order(self,x):     raise NotImplementedError
    def indexElem(self,x): raise NotImplementedError  ### TODO: Remove?
    def LaTeX(self):       raise NotImplementedError
    def showElem(self,x):  raise NotImplementedError
    def LaTeXElem(self,x): raise NotImplementedError

    def showUElem(self,x): return uniexp(self.showElem(x))
    def __unicode__(self): return uniexp(str(self))

    # Subclasses also need to define __len__, __iter__, __contains__, __str__,
    # and (optionally) __unicode__.

    @property
    def family(self): return self.__class__.__name__

    def __hash__(self): return hash((self.family, self.params))

    ###def __mul__(self, other): return DirectProduct(self, other)

    def __nonzero__(self): return len(self) > 1

    def __cmp__(self, other):
	return cmp(type(self), type(other)) or cmp(self.params, other.params)

    def __repr__(self):
	return self.family + '(' + ', '.join(map(repr, self.params)) + ')'

    def elements(self): return list(iter(self))

    def copy(self): return self.__class__(*self.params)

    def product(self, xs): return reduce(self.oper, xs, self.identity())

    def conjugate(self, x, y): return self.oper(self.oper(y,x), self.invert(y))

    def centralizer(self, elems):
	elems = list(elems)
	op = self.oper
	return filter(lambda x: all(op(x,y) == op(y,x) for y in elems), self)

    def center(self): return self.centralizer(self)

    def normalizer(self, elems):
	elems = set(elems)
	return filter(lambda x: all(self.conjugate(y,x) in elems for y in elems), self)

    def isNormal(self, elems):
	# whether `elems` is actually a subgroup is not checked
	elems = set(elems)
	return all(self.conjugate(y,x) in elems for x in self for y in elems)

    def isSubgroup(self, elems):
	elems = set(elems)
	op = self.oper
	return bool(elems) \
	   and all(x in self for x in elems) \
	   and all(op(x,y) in elems for x in elems for y in elems)

    def isAbelian(self):
	op = self.oper
	return all(op(x,y) == op(y,x) for x in self for y in self)

    def conjugacies(self):
	yield set([self.identity()])
	left = set(self)
	left.remove(self.identity())
	while left:
	    least = minimum(left)
	    cc = set(self.conjugate(least,x) for x in left)
	    yield cc
	    left -= cc

    def lowerCentral(self):
	whole = frozenset(self)
	h = whole
	while True:
	    yield h
	    h = frozenset(commutators(whole, h))

    def nilpotence(self):
	if len(self) == 1: return 0
	i = 1
	lc = self.lowerCentral()
	prev = lc.next()
	for h in lc:
	    if h == prev: return None
	    if len(h) == 1: return i
	    i += 1
	    prev = h

    def closure(self, iterable): return closure2A(self.oper, iterable)
	# assumes the iterable is over elements of `self`
	# returns an iterator
	### TODO: Should this return a set?

    def commutator(self, x, y):
	return self.oper(self.invert(self.oper(y,x)), self.oper(x,y))

    def commutators(self, iterable1, iterable2):
	# assumes the iterables are over elements of `self`
	### TODO: Should this return a set?
	aset = set(iterable1)
	bset = set(iterable2)
	return closure(self.commutator(x,y) for x in aset for y in bset)


class Group(group):
    paramNames = ('group',)

    def __init__(self, rawGroup):
	if isinstance(rawGroup, Group):
	    rawGroup = rawGroup.group
	super(Group, self).__init__((rawGroup,))

    def identity(self):    return Element(self.group.identity(), self)
    def oper(self,x,y):    return Element(self.group.oper(x.value,y.value),self)
    def invert(self,x):    return Element(self.group.invert(x.value), self)
    def order(self,x):     return self.group.order(x.value)
    def indexElem(self,x): return self.group.indexElem(x.value)
    def LaTeX(self):       return self.group.LaTeX()
    def showElem(self,x):  return self.group.showElem(x.value)
    def showUElem(self,x): return self.group.showUElem(x.value)
    def LaTeXElem(self,x): return self.group.LaTeXElem(x.value)
    def __len__(self):     return len(self.group)

    def __iter__(self):
        return itertools.imap(lambda x: Element(x, self), self.group)

    def __str__(self): return str(self.group)
    def __unicode__(self): return unicode(self.group)

    @property
    def family(self): return self.group.__class__.__name__

    def __contains__(self, x): return isinstance(x, Element) and x.group == self


class Element(object):
    def __init__(self, val, gr):
	self.value = val
	self.group = gr

    @property
    def order(self): return self.group.order(self)

    @property
    def index(self): return self.group.indexElem(self)

    @property
    def rawGroup(self): return self.group.group

    def __mul__(self, y): return self.group.oper(self,y)
    def __invert__(self): return self.group.invert(self)
    def __div__(self, y): return self * ~y
    __truediv__ = __div__

    def __repr__(self):    return 'Element(%r, %r)' % (self.value, self.group)
    def __str__(self):     return self.group.showElem(self)
    def __unicode__(self): return self.group.showUElem(self)
    def LaTeX(self):       return self.group.LaTeXElem(self)

    def __cmp__(self, other):
	return cmp(type(self), type(other)) or \
	       cmp((self.group, self.value), (other.group, other.value))

    def __hash__(self): return hash((self.rawGroup, self.index))

    def __nonzero__(self): return self.value != self.group.identity().value

    def __pow__(self, n):  ### TODO: Make this available to non-Group elements
	order = self.order
	n %= order
	if n == 0: return self.group.identity()
	if order - n < order // 2:
	    n = order - n
	    x = ~self
	else:
	    x = self
	i=1
	while not (n & i):
	    x *= x
	    i <<= 1
	agg = x
	i <<= 1
	x *= x
	while i <= n:
	    if n & i: agg *= x
	    i <<= 1
	    x *= x
	return agg

    def cycle(self):  ### TODO: Make this available to non-Group elements
	yield self.group.identity()
	x = self
	while x:
	    yield x
	    x *= self


class Cyclic(group):
    paramNames = ('n',)

    def __init__(self, n):
	if n < 1: raise ValueError('n must be positive')
	super(Cyclic, self).__init__((n,))

    def identity(self):    return 0
    def oper(self,x,y):    return (x + y) % self.n
    def invert(self,x):    return -x.i % self.n
    def __len__(self):     return self.n
    def __iter__(self):    return xrange(self.n)
    def __contains__(self,x): return 0 <= x < self.n
    def order(self,x):     return cycOrd(self.n, x)
    def indexElem(self,x): return x
    def __str__(self):     return  'Z' + sub(self.n)
    def __unicode__(self): return u'ℤ' + subU(self.n)
    def LaTeX(self):       return r'\mathbb{Z}' + sub(self.n)
    def showElem(self,x):  return shexp('x', x)
     ### TODO: Add an option for changing the name of the variable
    LaTeXElem = showElem


class Semidirect(group):
    paramNames = ('g', 'h', 'phi')
    # It is the user's responsibility to ensure that phi is an actual valid
    # homomorphism from the Elements of h to the automorphism group on the
    # Elements of g.

    ### v.2.6+: Use `namedtuple` for elements

    def identity(self): return (self.g.identity(), self.h.identity())

    def oper(self,x,y):
	return (self.g.oper(x[0] * self.phi(x[1])(y[0])),
		self.h.oper(x[1] * y[1]))

    def invert(self,x):
	return (self.phi(h.invert(x[1]))(g.invert(x[0])), h.invert(x[1]))

    def __len__(self):  return len(self.g) * len(self.h)

    def __iter__(self): return ((a,b) for a in self.g for b in self.h)

    def __contains__(self, x):
	return isPair(x) and x[0] in self.g and x[1] in self.h

    def indexElem(self,x): return g.indexElem(x[0]) * len(g) + h.indexElem(x[1])

    def order(self, x):
	# Should the results be cached somehow?
	i=1
	val=x
	while val[0] != self.g.identity() and val[1] != self.h.identity():
	    val = self.oper(val, x)
	    i += 1
	if val[0] == self.g.identity(): return i * self.h.order(val[1])
	else: return i * self.g.order(val[0])

    def showElem(self,x):
	if x == self.identity(): return '1'
	else: return '(%s, %s)' % (self.g.showElem(x[0]), self.h.showElem(x[1]))

    def showUElem(self,x):
	if x == self.identity(): return u'1'
	else: return u'(%s, %s)' % (self.g.showUElem(x[0]), self.h.showUElem(x[1]))

    def LaTeXElem(self,x):
	if x == self.identity(): return '1'
	else: return '(%s, %s)' % (self.g.LaTeXElem(x[0]), self.h.LaTeXElem(x[1]))

    ### TODO: Add an option for turning on "ab"-style showing

    def __str__(self): return showbinop(self.g, 'x|', self.h)
     ### Rethink the operator
    def __unicode__(self): return showbinopU(self.g, u'⋊', self.h)
    def LaTeX(self): return showbinop(self.g.LaTeX(), r'\rtimes', self.h.LaTeX())


class DirectProduct(Semidirect):
    paramNames = ('g', 'h')
    def oper(self, x, y):  return (self.g.oper(x[0] * y[0]), self.h.oper(x[1] * y[1]))
    def invert(self, x):   return (self.g.invert(x[0]), self.h.invert(x[1]))
    def order(self,x):     return lcm(self.g.order(x[0]), self.h.order(x[1]))
    def __str__(self):     return showbinop(self.g,   '*', self.h)
    def __unicode__(self): return showbinopU(self.g, u'×', self.h)

    def LaTeX(self):
	return showbinop(self.g.LaTeX(), r'\times', self.h.LaTeX())

    # identity, indexElem, __len__, __iter__, __contains__, showElem,
    # showUElem, and LaTeXElem are inherited from semidirect (though the last
    # three might have to be overridden if "ba"-style showing is ever
    # implemented).

    @property
    def phi(self): return lambda y: lambda x: x


class Dicyclic(group):
    paramNames = ('n',)

    def __init__(self, n):
	if n < 2: raise ValueError('n must be at least 2')
	super(Dicyclic, self).__init__((n,))

    ### v.2.6+: Use `namedtuple` for elements

    def identity(self): return (0, False)

    def oper(self,x,y):
	return ((x[0] + (-y[0] if x[1] else y[0])
		      + self.n * (x[1] and y[1])) % (2*self.n),
		x[1] != y[1])

    def invert(self,x):
	return ((x[0]+self.n if x[1] else -x[0]) % (2*self.n), x[1])

    def __len__(self): return 4*self.n

    def __iter__(self):
	return ((i,j) for i in range(2*self.n) for j in [False, True])

    def __contains__(self, x):
	return isPair(x) and 0 <= x[0] < 2*self.n and 0 <= x[1] < 2

    def order(self,x): return 4 if x[1] else cycOrd(2*self.n, x[0])

    def indexElem(self,x): return (2*self.n if x[1] else 0) + x[0]

    def __str__(self): return 'Dic' + sub(self.n)

    def LaTeX(self): return r'\operatorname{Dic}' + sub(self.n)

    def showElem(self,x):
	(pre, i) = ('', x[0]) if x[0] < self.n else ('-', x[0] - self.n)
	return pre + multish(shexp('i', i), 'j' if x[1] else '1')

    LaTeXElem = showElem

def Quaternion(n=2):
    if n<2: raise ValueError('n must be at least 2')
    qn = Dicyclic(1 << (n-1))
    #qn.__str__ = qn.LaTeX = lambda self: 'Q' + sub(1 << (n+1))
     ### TODO: Figure out how to make this work.
    return qn
    ### When n=2, the group should be somehow modified so that 'ij' is shown as
    ### 'k'.


class Dihedral(group):
    paramNames = ('n',)

    def __init__(self, n):
	if n < 1: raise ValueError('n must be positive')
	super(Dihedral, self).__init__((n,))

    ### v.2.6+: Use `namedtuple` for elements

    def identity(self): return (False, 0)
    def invert(self,x): return x if x[0] else (False, -x[1] % self.n)
    def order(self,x): return 2 if x[0] else cycOrd(self.n, x[1])
    def indexElem(self,x): return (self.n if x[0] else 0) + x[1]
    def __len__(self): return 2*self.n
    def __str__(self): return 'Dih' + sub(self.n)
    def LaTeX(self): return r'\operatorname{Dih}' + sub(self.n)

    def oper(self,x,y):
	return (x[0] != y[0], (y[1] + (-x[1] if y[0] else x[1])) % self.n)

    def __iter__(self):
	return ((s,r) for s in [False, True] for r in range(self.n))

    def __contains__(self, x):
	return isPair(x) and 0 <= x[0] < 2 and 0 <= x[1] < self.n

    def showElem(self,x):
	return multish('s' if x[0] else '1', shexp('r', x[1]))
    ### Should there be an option for showing the 'r' before the 's'?

    LaTeXElem = showElem


class Trivial(group):
    paramNames = ()
    def identity(self):    return ()
    def oper(self,x,y):    return x
    def invert(self,x):    return x
    def order(self,x):     return 1
    def __len__(self):     return 1
    def __iter__(self):    yield ()
    def __contains__(self, x): return x == ()
    def __str__(self):     return '1'
    def LaTeX(self):       return '1'
    def indexElem(self,x): return 0
    def showElem(self,x):  return '1'
    LaTeXElem = showElem


class Klein4(group):
    paramNames = ()
    ### v.2.6+: Use `namedtuple` for elements?
    def identity(self):    return (False, False)
    def oper(self,x,y):    return (x[0] != y[0], x[1] != y[1])
    def invert(self,x):    return x
    def order(self,x):     return 2 if x else 1
    def __len__(self):     return 4
    def __iter__(self):    return ((a,b) for a in [False, True]
					 for b in [False, True])
    def __str__(self):     return 'V_4'
    def LaTeX(self):       return 'V_4'
    def indexElem(self,x): return int(x[0]) * 2 + int(x[1])
    def showElem(self,x):  return multish('a' if x[0] else '1',
					  'b' if x[1] else '1')
    LaTeXElem = showElem

    def __contains__(self, x):
	return isPair(x) and 0 <= x[0] < 2 and 0 <= x[1] < 2


class AutCyclic(group):  # formerly "MultiplicN"
    paramNames = ('n',)

    def __init__(self, n):
	if n < 1: raise ValueError('n must be positive')
	super(AutCyclic, self).__init__((n,))
	self._elems = [i for i in range(1,n+1) if gcd(n,i) == 1]
	self._indices = dict(zip(self._elems, range(n)))

    def identity(self):    return 1
    def oper(self,x,y):    return (x * y) % self.n
    def invert(self,x):    return modInverse(x, self.n)
    def indexElem(self,x): return self._indices[x]
    def __len__(self):     return len(self._elems)
    def __iter__(self):    return iter(self._elems)
    def __contains__(self, x): return 0 <= x < self.n and gcd(x, self.n) == 1

    def order(self,x):
    ### TODO: Try to find a more efficient way to calculate this.
	i=1
	val=x
	while val != 1:
	    val = (val * x) % self.n
	    i += 1
	return i

    ### TODO: Rethink these:
    def __str__(self):     return  'Z'          + sub(self.n)  + '^*'
    def __unicode__(self): return u'ℤ'          + subU(self.n) + u'ˣ'
    def LaTeX(self):       return r'\mathbb{Z}' + sub(self.n)  + r'^\times{}'
    def showElem(self,x):  return  '*'       + str(x)     if x else  '1'
    def showUElem(self,x): return u'⋅'       + unicode(x) if x else u'1'
    def LaTeXElem(self,x): return r'\cdot{}' + str(x)     if x else  '1'


def HolCyclic(n):
    if n<1: raise ValueError('n must be positive')
    g = Cyclic(n)
    h = AutCyclic(n)
    return Semidirect(g, h, lambda y: lambda x: g.elem((x * y) % n))
    ### TODO: Should __str__ etc. be overridden to show $\Hol(\Z_n)$?

def CycSemiCyc(n,m,i):
    if n < 1 or m < 1:
	raise ValueError('n and m must be positive')
    elif pow(i,m,n) != 1:
	raise ValueError('invalid homomorphism')
    else:
	g = Cyclic(n)
	h = Cyclic(m)
	return Semidirect(g, h, lambda y: lambda x: g.elem((x * i**y) % n))


class Symmetric(group):
    paramNames = ('n',)

    def __init__(self, n):
	if n < 0: raise ValueError('n must be nonnegative')
	if n == 0: n = 1
	super(Symmetric, self).__init__((n,))

    def identity(self):    return Permutation()
    def oper(self,x,y):    return x * y
    def invert(self,x):    return x.inverse
    def __len__(self):     return factorial(self.n)
    def order(self,x):     return x.order
    def indexElem(self,x): return x.lehmer
    def __str__(self):     return 'S' + sub(self.n)
    LaTeX = __str__
    def showElem(self,x):  return str(x)
    def LaTeXElem(self,x): return str(x).replace(' ', r'\>')
    def __iter__(self):    return Permutation.s_n(self.n)

    def __contains__(self, x):
	return isinstance(x, Permutation) and x.degree <= self.n


def isHomomorphism(phi, g, h):
    """Tests whether the callable object `phi` is a homomorphism from the group
       `g` to the group `h`"""
    gop = g.oper
    hop = h.oper
    return all(phi(x) in h for x in g) \
       and all(hop(phi(x), phi(y)) == phi(gop(x,y)) for x in g for y in g)


# Internal functions: ---------------------------------------------------------

subs   = {0x30: u'₀', 0x31: u'₁', 0x32: u'₂', 0x33: u'₃', 0x34: u'₄',
	  0x35: u'₅', 0x36: u'₆', 0x37: u'₇', 0x38: u'₈', 0x39: u'₉',
	  0x2d: u'₋'}

supers = {0x30: u'⁰', 0x31: u'¹', 0x32: u'²', 0x33: u'³', 0x34: u'⁴',
	  0x35: u'⁵', 0x36: u'⁶', 0x37: u'⁷', 0x38: u'⁸', 0x39: u'⁹',
	  0x2d: u'⁻'}

def sub(n):  n = str(n); return '_{' + n + '}' if len(n) > 1 else '_' + n
def subU(n): return unicode(n).translate(subs)

def sup(n):  n = str(n); return '^{' + n + '}' if len(n) > 1 else '^' + n
def supU(n): return unicode(n).translate(supers)

def uniexp(str):
    def mogrify(match):
	(cmd, val1, val2) = match.groups()
	return (val1 or val2).translate(subs if cmd == u'_' else supers)
    return re.sub(ur'([_^])(?:([-\d])|\{(-?\d*)\})', mogrify, unicode(str))

def multish(x,y):
    if x == '1': return y
    elif y == '1': return x
    else: return x + y

def shexp(x,i):
    if i == 0: return '1'
    elif i == 1: return x
    else: return x + sup(i)

def cycOrd(n,x): return n // gcd(x,n)

def showbinop(x,op,y):
    x = str(x)
    y = str(y)
    if ' ' in x: x = '(' + x + ')'
    if ' ' in y: y = '(' + y + ')'
    return x + ' ' + op + ' ' + y

def showbinopU(x,op,y):
    x = unicode(x)
    y = unicode(y)
    if u' ' in x: x = u'(' + x + u')'
    if u' ' in y: y = u'(' + y + u')'
    return x + u' ' + op + u' ' + y

def factorial(n):
    x=1
    for i in range(2,n+1):
	x *= i
    return x

def gcd(x,y):
    (a,b) = (abs(x), abs(y))
    if a == 0 and b == 0: return 0
    elif a == 0 or b == 0: return a or b
    while b != 0:
	(a,b) = (b, a % b)
    return a

def lcm(x,y): d = gcd(x,y); return 0 if d == 0 else abs(x*y) // d

def modInverse(a,n):
    (u, uc) = (abs(n), 0)
    (l, lc) = (a % u, 1)
    while l > 1:
	(u, uc, l, lc) = (l, lc, u % l, uc - lc * (u//l))
    if l == 1: return lc % abs(n)
    else: raise ValueError('%d has no multiplicative inverse modulo %d' % (a,n))

def isPair(x): return isinstance(x, tuple) and len(x) == 2