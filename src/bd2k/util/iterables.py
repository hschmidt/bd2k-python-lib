from itertools import takewhile, izip, izip_longest, dropwhile, imap, chain


def common_prefix( xs, ys ):
    """
    >>> list( common_prefix('','') )
    []
    >>> list( common_prefix('A','') )
    []
    >>> list( common_prefix('','A') )
    []
    >>> list( common_prefix('A','A') )
    ['A']
    >>> list( common_prefix('AB','A') )
    ['A']
    >>> list( common_prefix('A','AB') )
    ['A']
    >>> list( common_prefix('A','B') )
    []
    """
    return imap( lambda (x, y): x, takewhile( lambda (a, b): a == b, izip( xs, ys ) ) )


def disparate_suffix( xs, ys ):
    """
    >>> list( disparate_suffix('','') )
    []
    >>> list( disparate_suffix('A','') )
    [('A', None)]
    >>> list( disparate_suffix('','A') )
    [(None, 'A')]
    >>> list( disparate_suffix('A','A') )
    []
    >>> list( disparate_suffix('AB','A') )
    [('B', None)]
    >>> list( disparate_suffix('A','AB') )
    [(None, 'B')]
    >>> list( disparate_suffix('A','B') )
    [('A', 'B')]
    """
    return dropwhile( lambda (a, b): a == b, izip_longest( xs, ys ) )


def flatten( iterables ):
    return chain.from_iterable( iterables )


# noinspection PyPep8Naming
class concat( object ):
    """
    A literal iterable that lets you combine sequence literals (lists, set) with generators or list
    comprehensions. Instead of

    >>> [ -1 ] + [ x * 2 for x in range( 3 ) ] + [ -1 ]
    [-1, 0, 2, 4, -1]

    you can write

    >>> list( concat( -1, ( x * 2 for x in range( 3 ) ), -1 ) )
    [-1, 0, 2, 4, -1]

    This is slightly shorter (not counting the list constructor) and does not involve array
    construction or concatenation.

    Note that concat() flattens (or chains) all iterable arguments into a single result iterable:

    >>> list( concat( 1, xrange( 2, 4 ), 4 ) )
    [1, 2, 3, 4]

    It only does so one level deep. If you need to recursively flatten a data structure,
    check out crush().

    If you want to prevent that flattening for an iterable argument, wrap it in concat():

    >>> list( concat( 1, concat( xrange( 2, 4 ) ), 4 ) )
    [1, xrange(2, 4), 4]

    Some more example.

    >>> list( concat() ) # empty concat
    []
    >>> list( concat( 1 ) ) # non-iterable
    [1]
    >>> list( concat( concat() ) ) # empty iterable
    []
    >>> list( concat( concat( 1 ) ) ) # singleton iterable
    [1]
    >>> list( concat( 1, concat( 2 ), 3 ) ) # flattened iterable
    [1, 2, 3]
    >>> list( concat( 1, [2], 3 ) ) # flattened iterable
    [1, 2, 3]
    >>> list( concat( 1, concat( [2] ), 3 ) ) # protecting an iterable from being flattened
    [1, [2], 3]
    >>> list( concat( 1, concat( [2], 3 ), 4 ) ) # protection only works with a single argument
    [1, 2, 3, 4]
    >>> list( concat( 1, 2, concat( 3, 4 ), 5, 6 ) )
    [1, 2, 3, 4, 5, 6]
    >>> list( concat( 1, 2, concat( [ 3, 4 ] ), 5, 6 ) )
    [1, 2, [3, 4], 5, 6]

    Note that while strings are technically iterable, concat() does not flatten them.

    >>> list( concat( 'ab' ) )
    ['ab']
    >>> list( concat( concat( 'ab' ) ) )
    ['ab']
    """

    def __init__( self, *args ):
        super( concat, self ).__init__( )
        self.args = args

    def __iter__( self ):
        def expand( x ):
            if isinstance( x, concat ) and len( x.args ) == 1:
                i = x.args
            else:
                try:
                    i = x.__iter__( )
                except AttributeError:
                    i = x,
            return i

        return flatten( imap( expand, self.args ) )


# noinspection PyPep8Naming
class crush( object ):
    """
    >>> list(crush([]))
    []
    >>> list(crush([[]]))
    []
    >>> list(crush([1]))
    [1]
    >>> list(crush([[1]]))
    [1]
    >>> list(crush([[[]]]))
    []
    >>> list(crush([1,(),['two'],([3, 4],),{5}]))
    [1, 'two', 3, 4, 5]

    >>> list(crush(1))
    Traceback (most recent call last):
    ...
    TypeError: 'int' object is not iterable

    >>> list(crush('123'))
    ['1', '2', '3']

    The above is a bit of an anomaly since strings occurring inside iterables are not broken up:

    >>> list(crush(['123']))
    ['123']
    """

    def __init__( self, iterables ):
        super( crush, self ).__init__( )
        self.iterables = iterables

    def __iter__( self ):
        def expand( x ):
            try:
                # Using __iter__() instead of iter() prevents breaking up of strings
                return crush( x.__iter__( ) )
            except AttributeError:
                return x,

        return flatten( imap( expand, self.iterables ) )
