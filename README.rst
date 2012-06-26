On Error Resume Next
---------------------------------------------------------------------------
Need the best of VB in python. Now you can have even better, on error resume
will infect all modules imported after it.  It preforms an AST transformation
on all imported modules that replaces each statement with a try/except/pass.
If you import it from a main module it will rewrite the module then rerun it.

Examples
---------------------------------------------------------------------------

Single File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

sample1.py::

    import on_error_resume_next

    a = '1'
    print 1, a
    a = b
    print 2, a
    a = '7'
    print 3, a
    raise Exception('Bad times')
    a = j
    print 4, a

run::

    $ python test.py
    1 1
    2 1
    3 7
    4 7

Multiple File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

sample3.py::

    def fail():
        raise Exception('foo')

sample2.py::

    import on_error_resume_next
    import sample3

    print 'test'
    sample3.fail()
    print 'still testing'

run::

    $ python sample2.py
    test
    still testing


Bugs
---------------------------------------------------------------------------
The __main__ module will be run twice if on_error_resume_next is not the first
import. :(
