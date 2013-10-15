try:
    eval('1 if True else 2')
except SyntaxError:
    raise ImportError('To run QUAST, Python 2.5 or greater is required.')