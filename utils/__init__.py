import platform

if platform.system() == 'Windows':
    from .insulation_windows import get_cache_path
elif platform.system() == 'Linux':
    from .insulation_linux import get_cache_path
else:
    raise Exception('Unsupported platform.')

