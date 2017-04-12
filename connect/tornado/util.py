import os, pkgutil

def get_root_path(import_name):
    loader = pkgutil.get_loader(import_name)
    if loader is None or import_name == '__main__':
        return os.getcwd()
    if hasattr(loader, 'get_filename'):
        filepath = loader.get_filename(import_name)
    else:
        __import__(import_name)
        filepath = sys.modules[import_name].__file__
    return os.path.dirname(os.path.abspath(filepath))
