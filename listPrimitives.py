from program import Primitive, Program
from grammar import Grammar
from type import tlist, tint, tbool, arrow, t0, t1, t2

import math

def _flatten(l): return [x for xs in l for x in xs]

def _if(c): return lambda t: lambda f: t if c else f
def _and(x): return lambda y: x and y
def _or(x): return lambda y: x or y
def _addition(x): return lambda y: x + y
def _subtraction(x): return lambda y: x - y
def _multiplication(x): return lambda y: x*y
def _negate(x): return -x
def _reverse(x): return list(reversed(x))
def _append(x): return lambda y: x + y
def _cons(x): return lambda y: [x] + y
def _car(x): return x[0]
def _cdr(x): return x[1:]
def _isEmpty(x): return x == []
def _single(x): return [x]
def _slice(x): return lambda y: lambda l: l[x:y]
def _map(f): return lambda l: map(f, l)
def _mapi(f): return lambda l: map(lambda (i,x): f(i)(x), enumerate(l))
def _reduce(f): return lambda x0: lambda l: reduce(lambda a, x: f(a)(x), l, x0)
def _reducei(f): return lambda x0: lambda l: reduce(lambda a, (i,x): f(i)(a)(x), enumerate(l), x0)
def _eq(x): return lambda y: x == y
def _eq0(x): return x == 0
def _a1(x): return x + 1
def _d1(x): return x - 1
def _mod(x): return lambda y: x%y
def _not(x): return not x
def _gt(x): return lambda y: x > y
def _index(j): return lambda l: l[j]
def _replace(f): return lambda lnew: lambda lin: _flatten(lnew if f(i)(x) else [x] for i, x in enumerate(lin))
def _isPrime(n):
    return n in {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199}
def _isSquare(n):
    return int(math.sqrt(n)) ** 2 == n

def _appendmap(f): lambda xs: [y for x in xs for y in f(x)]
def _filter(f): return lambda l: filter(f, l)
def _any(f): return lambda l: any(f(x) for x in l)
def _all(f): return lambda l: all(f(x) for x in l)
def _find(x):
    def _inner(l):
        try:
            return l.index(x)
        except ValueError:
            return -1
    return _inner
def _unfold(p): return lambda f: lambda n: lambda x: __unfold(p,f,n,x)
def __unfold(p,f,n,x):
    if p(x): return []
    return [f(x)] + __unfold(p,f,n,n(x))

class RecursionDepthExceeded(Exception): pass
def _fix(argument):
    def inner(body):
        recursion_limit = [20]

        def fix(x):
            def r(z):
                recursion_limit[0] -= 1
                if recursion_limit[0] <= 0:
                    raise RecursionDepthExceeded()
                else: return fix(z)
                
            return body(r)(x)
        return fix(argument)

    return inner

def curry(f): return lambda x: lambda y: f((x,y)) 
def _fix2(a1):
    return lambda a2: lambda body: \
        _fix((a1,a2))(lambda r: lambda (n,l): body(curry(r))(n)(l))

primitiveRecursion1 = Primitive("fix1",
                               arrow(t0,
                                     arrow(arrow(t0,t1), t0,t1),
                                     t1),
                               _fix)

primitiveRecursion2 = Primitive("fix2",
                               arrow(t0, t1,
                                     arrow(arrow(t0,t1,t2), t0,t1,t2),
                                     t2),
                                _fix2)

def _match(l):
    return lambda b: lambda f: b if l == [] else f(l[0])(l[1:])


def primitives():
    return [ Primitive(str(j), tint, j) for j in xrange(6) ] + [
        Primitive("empty", tlist(t0), []),
        Primitive("singleton", arrow(t0, tlist(t0)), _single),
        Primitive("range", arrow(tint, tlist(tint)), range),
        Primitive("++", arrow(tlist(t0), tlist(t0), tlist(t0)), _append),
        # Primitive("map", arrow(arrow(t0, t1), tlist(t0), tlist(t1)), _map),
        Primitive("mapi", arrow(arrow(tint, t0, t1), tlist(t0), tlist(t1)), _mapi),
        # Primitive("reduce", arrow(arrow(t1, t0, t1), t1, tlist(t0), t1), _reduce),
        Primitive("reducei", arrow(arrow(tint, t1, t0, t1), t1, tlist(t0), t1), _reducei),

        Primitive("true", tbool, True),
        Primitive("not", arrow(tbool, tbool), _not),
        Primitive("and", arrow(tbool, tbool, tbool), _and),
        Primitive("or", arrow(tbool, tbool, tbool), _or),
        # Primitive("if", arrow(tbool, t0, t0, t0), _if),

        Primitive("sort", arrow(tlist(tint), tlist(tint)), sorted),
        Primitive("+", arrow(tint, tint, tint), _addition),
        Primitive("*", arrow(tint, tint, tint), _multiplication),
        Primitive("negate", arrow(tint, tint), _negate),
        Primitive("mod", arrow(tint, tint, tint), _mod),
        Primitive("eq?", arrow(tint, tint, tbool), _eq),
        Primitive("gt?", arrow(tint, tint, tbool), _gt),
        Primitive("is-prime", arrow(tint, tbool), _isPrime),
        Primitive("is-square", arrow(tint, tbool), _isSquare),

        # these are achievable with above primitives, but unlikely
        #Primitive("flatten", arrow(tlist(tlist(t0)), tlist(t0)), _flatten),
        ## (lambda (reduce (lambda (lambda (++ $1 $0))) empty $0))
        Primitive("sum", arrow(tlist(tint), tint), sum),
        # (lambda (lambda (reduce (lambda (lambda (+ $0 $1))) 0 $0)))
        Primitive("reverse", arrow(tlist(t0), tlist(t0)), _reverse),
        # (lambda (reduce (lambda (lambda (++ (singleton $0) $1))) empty $0))
        Primitive("all", arrow(arrow(t0, tbool), tlist(t0), tbool), _all),
        # (lambda (lambda (reduce (lambda (lambda (and $0 $1))) true (map $1 $0))))
        Primitive("any", arrow(arrow(t0, tbool), tlist(t0), tbool), _any),
        # (lambda (lambda (reduce (lambda (lambda (or $0 $1))) true (map $1 $0))))
        Primitive("index", arrow(tint, tlist(t0), t0), _index),
        # (lambda (lambda (reducei (lambda (lambda (lambda (if (eq? $1 $4) $0 0)))) 0 $0)))
        Primitive("filter", arrow(arrow(t0, tbool), tlist(t0), tlist(t0)), _filter),
        # (lambda (lambda (reduce (lambda (lambda (++ $1 (if ($3 $0) (singleton $0) empty)))) empty $0)))
        #Primitive("replace", arrow(arrow(tint, t0, tbool), tlist(t0), tlist(t0), tlist(t0)), _replace),
        ## (FLATTEN (lambda (lambda (lambda (mapi (lambda (lambda (if ($4 $1 $0) $3 (singleton $1)))) $0)))))
        Primitive("slice", arrow(tint, tint, tlist(t0), tlist(t0)), _slice),
        # (lambda (lambda (lambda (reducei (lambda (lambda (lambda (++ $2 (if (and (or (gt? $1 $5) (eq? $1 $5)) (not (or (gt? $4 $1) (eq? $1 $4)))) (singleton $0) empty))))) empty $0))))
    ]


def basePrimitives():
    "These are really powerful but hard to learn to use."
    return [ Primitive(str(j), tint, j) for j in xrange(6) ] + [
        Primitive("empty", tlist(t0), []),
        #Primitive("singleton", arrow(t0, tlist(t0)), _single),
        Primitive("cons", arrow(t0, tlist(t0), tlist(t0)), _cons),
        Primitive("range", arrow(tint, tlist(tint)), range),
        #Primitive("++", arrow(tlist(t0), tlist(t0), tlist(t0)), _append),
        # Primitive("mapi", arrow(arrow(tint, t0, t1), tlist(t0), tlist(t1)), _mapi),
        Primitive("reducei", arrow(arrow(tint, t1, t0, t1), t1, tlist(t0), t1), _reducei),

        #Primitive("true", tbool, True),
        # Primitive("not", arrow(tbool, tbool), _not),
        # Primitive("and", arrow(tbool, tbool, tbool), _and),
        # Primitive("or", arrow(tbool, tbool, tbool), _or),
        Primitive("if", arrow(tbool, t0, t0, t0), _if),

        Primitive("sort", arrow(tlist(tint), tlist(tint)), sorted),
        Primitive("+", arrow(tint, tint, tint), _addition),
        Primitive("*", arrow(tint, tint, tint), _multiplication),
        Primitive("negate", arrow(tint, tint), _negate),
        Primitive("mod", arrow(tint, tint, tint), _mod),
        Primitive("eq?", arrow(tint, tint, tbool), _eq),
        Primitive("gt?", arrow(tint, tint, tbool), _gt),
        Primitive("is-prime", arrow(tint, tbool), _isPrime),
        Primitive("is-square", arrow(tint, tbool), _isSquare),
    ]

def McCarthyPrimitives():
    "These are ~ primitives provided by 1959 lisp as introduced by McCarthy"
    return [
        Primitive("empty", tlist(t0), []),
        Primitive("cons", arrow(t0, tlist(t0), tlist(t0)), _cons),
        Primitive("car", arrow(tlist(t0), t0), _car),
        Primitive("cdr", arrow(tlist(t0), tlist(t0)), _cdr),
        Primitive("empty?", arrow(tlist(t0), tbool), _isEmpty),
        primitiveRecursion1,
        primitiveRecursion2,
        Primitive("if", arrow(tbool, t0, t0, t0), _if),
        Primitive("eq?", arrow(tint, tint, tbool), _eq),

        # The hope is that it learns these quickly
        # Primitive("eq0", arrow(tint, tbool), _eq0),
        # Primitive("+1", arrow(tint, tint), _a1),
        # Primitive("-1", arrow(tint, tint), _d1),
        # Primitive("unfold", arrow(arrow(t0,tbool),
        #                           arrow(t0,t1),
        #                           arrow(t0,t0),
        #                           t0,
        #                           tlist(t1)),
        #           _unfold),
        
        Primitive("+", arrow(tint, tint, tint), _addition),
        Primitive("-", arrow(tint, tint, tint), _subtraction),
        ] + [ Primitive(str(j), tint, j) for j in xrange(2) ]

if __name__ == "__main__":
    g = Grammar.uniform(McCarthyPrimitives())

    p = Program.parse("(lambda (lambda (lambda (if (empty? $0) empty (cons (+ (car $0) (car $1)) ($2 (cdr $0) (cdr $1)))))))")
    t = arrow(tlist(tint),tlist(tint),tlist(tint))
    print g.logLikelihood(arrow(t,t), p)
    assert False

    print "??"
    p = Program.parse("#(lambda (#(lambda (lambda (lambda (fix1 $0 (lambda (lambda (if (empty? $0) $3 ($4 (car $0) ($1 (cdr $0)))))))))) (lambda $1) 1))")
    for j in xrange(10):
        l = range(j)
        print l,p.evaluate([])(lambda x: x*2)(l)
        print
    print 

    print "multiply"
    p = Program.parse("(lambda (lambda (lambda (if (eq? $0 0) 0 (+ $1 ($2 $1 (- $0 1)))))))")
    print g.logLikelihood(arrow(arrow(tint,tint,tint),tint,tint,tint), p)
    print

    print "take until 0"
    p = Program.parse("(lambda (lambda (if (eq? $1 0) empty (cons $1 $0))))")
    print g.logLikelihood(arrow(tint,tlist(tint),tlist(tint)), p)
    print 

    print "countdown primitive"
    p = Program.parse("(lambda (lambda (if (eq? $0 0) empty (cons (+ $0 1) ($1 (- $0 1))))))")
    print g.logLikelihood(arrow(arrow(tint,tlist(tint)), arrow(tint,tlist(tint))), p)
    print _fix(9)(p.evaluate([]))
    print "countdown w/ better primitives"
    p = Program.parse("(lambda (lambda (if (eq0 $0) empty (cons (+1 $0) ($1 (-1 $0))))))")
    print g.logLikelihood(arrow(arrow(tint,tlist(tint)), arrow(tint,tlist(tint))), p)

    
    print 

    print "prepend zeros"
    p = Program.parse("(lambda (lambda (lambda (if (eq? $1 0) $0 (cons 0 ($2 (- $1 1) $0))))))")
    print g.logLikelihood(arrow(arrow(tint,tlist(tint),tlist(tint)),tint,tlist(tint),tlist(tint)), p)
    print
    assert False

    p = Program.parse("(lambda (fix1 $0 (lambda (lambda (if (empty? $0) 0 (+ 1 ($1 (cdr $0))))))))")
    print p.evaluate([])(range(17))
    print g.logLikelihood(arrow(tlist(tbool),tint),p)

    p = Program.parse("(lambda (lambda (if (empty? $0) 0 (+ 1 ($1 (cdr $0))))))")
    print g.logLikelihood(arrow(arrow(tlist(tbool),tint),arrow(tlist(tbool),tint)),p)

    p = Program.parse("(lambda (fix1 $0 (lambda (lambda (if (empty? $0) 0 (+ (car $0) ($1 (cdr $0))))))))")
    
    print p.evaluate([])(range(4))
    print g.logLikelihood(arrow(tlist(tint),tint),p)

    p = Program.parse("(lambda (lambda (if (empty? $0) 0 (+ (car $0) ($1 (cdr $0))))))")
    print p
    print g.logLikelihood(arrow(arrow(tlist(tint),tint),tlist(tint),tint),p)

    print "take"
    p = Program.parse("(lambda (lambda (lambda (if (eq? $1 0) empty (cons (car $0) ($2 (- $1 1) (cdr $0)))))))")
    print p
    print g.logLikelihood(arrow(arrow(tint,tlist(tint),tlist(tint)),tint,tlist(tint),tlist(tint)),
                                p)
    assert False
    
    
    print p.evaluate([])(range(4))
    print g.logLikelihood(arrow(tlist(tint),tlist(tint)),p)
    
    p = Program.parse("""(lambda (fix (lambda (lambda (match $0 0 (lambda (lambda (+ $1 ($3 $0))))))) $0))""")
    print p.evaluate([])(range(4))
    print g.logLikelihood(arrow(tlist(tint),tint),p)
    
