import imp, ast, sys, inspect


def on_error_resume_next(path):
    file_ = open(path)
    tree = ast.parse(file_.read(), path)
    OnErrorResumeNextVisitor().visit(tree)
    ast.fix_missing_locations(tree)
    return compile(tree, path, 'exec')


class OnErrorResumeNextFinder(object):
    def _find_module(self, name, path):
        name = name.split('.')[-1]
        file_, file_path, desc = imp.find_module(name, path)
        if file_:
            file_.close()
        return file_path, desc

    def find_module(self, name, search_path=None):
        file_path, desc = self._find_module(name, search_path)
        if desc[2] == imp.PKG_DIRECTORY:
            return OnErrorResumeNextLoader(file_path+'/__init__.py',
                                           [file_path])
        elif desc[2] == imp.PY_SOURCE:
            return OnErrorResumeNextLoader(file_path)
        else:
            return


class OnErrorResumeNextLoader(object):
    def __init__(self, file_path, module_path=None):
        self.file_path = file_path
        self.module_path = module_path

    def _compile(self):
        return on_error_resume_next(self.file_path)

    def load_module(self, name):
        mod = sys.modules.setdefault(name, imp.new_module(name))
        mod.__loader__ = self
        co = self._compile()
        if self.module_path:
            mod.__path__ = self.module_path
            mod.__package__ = name
        else:
            mod.__package__ = name.rpartition('.')[0]
        mod.__file__ = self.file_path
        exec(co, mod.__dict__)
        return mod

    def get_code(self, name):
        return self._compile()

    def get_source(self, name):
        return open(self.file_path).read()

    def get_filename(self, name):
        return self.file_path


class OnErrorResumeNextVisitor(ast.NodeTransformer):
    stmt = (
        ast.FunctionDef,
        ast.ClassDef,
        ast.Return,
        ast.Delete,
        ast.Assign,
        ast.AugAssign,
        ast.Print,
        ast.For,
        ast.While,
        ast.If,
        ast.With,
        ast.Raise, # This seems like a bad plan
        ast.TryExcept,
        ast.TryFinally,
        ast.Assert, # I like this one
        ast.Import,
        ast.ImportFrom,
        ast.Exec,
        ast.Global,
        ast.Expr,
        ast.Pass, # I hate when pass fails
        ast.Break,
        ast.Continue
    )

    def visit(self, node):
        node = ast.NodeTransformer.visit(self, node)
        if isinstance(node, self.stmt):
            node = ast.TryExcept([node],
                                 [ast.ExceptHandler(None, None, [ast.Pass()])],
                                 [])
        return node

# Patch the world
sys.meta_path.insert(0, OnErrorResumeNextFinder())

# If this import was from the main module rerun it
stack = inspect.stack()
try:
    if len(stack) == 2 and stack[1][0].f_locals.get('__name__') == '__main__':
        file_path = stack[1][1]
        mod = imp.new_module('__main__')
        mod.__name__ = '__main__'
        sys.modules['__main__'] = mod
        code = on_error_resume_next(file_path)
        eval(code, mod.__dict__)
        sys.exit()
finally:
    del stack
