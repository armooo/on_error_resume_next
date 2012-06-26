import imp, ast, sys, inspect


def on_error_resume_next(file_, path):
    tree = ast.parse(file_.read(), path)
    OnErrorResumeNextVisitor().visit(tree)
    ast.fix_missing_locations(tree)
    return compile(tree, path, 'exec')


class OnErrorResumeNextHook(object):
    def __init__(self):
        self.module_code = {}

    def find_module(self, name, path=None):
        file_, path, desc = imp.find_module(name, path)
        if not file_:
            return
        try:
            if desc[2] != imp.PY_SOURCE:
                return None
            code  = on_error_resume_next(file_)
        finally:
            file_.close()
        self.module_code[name] = code
        return self

    def load_module(self, name):
        mod = imp.new_module(name)
        co = self.module_code.pop(name)
        eval(co, mod.__dict__)
        sys.modules[name] = mod
        return mod


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
sys.meta_path.insert(0, OnErrorResumeNextHook())

# If this import was from the main module rerun it
stack = inspect.stack()
try:
    if len(stack) == 2 and stack[1][0].f_locals.get('__name__') == '__main__':
        file_path = stack[1][1]
        mod = imp.new_module('__name__')
        sys.modules['__name__'] = mod
        code = on_error_resume_next(open(file_path), file_path)
        eval(code, mod.__dict__)
        sys.exit()
finally:
    del stack
