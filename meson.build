project('purelib-and-platlib', 'c')

py = import('python').find_installation(pure: false)

py.extension_module(
    'pyhaloxmlc',
    'src/pyhaloxmlc/pyhaloxmlc.c',
    install: true,
)

install_subdir('src/pyhaloxml', install_dir : py.get_install_dir(pure: false))