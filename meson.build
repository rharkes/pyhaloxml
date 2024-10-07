project('pyhaloxml',
  'c',
  version: '3.1.2',
  license: 'GPL-3',
  meson_version: '>= 1.5.2',
  default_options: [
    'c_std=c17',
  ],
)

py = import('python').find_installation(pure: false)

py.extension_module(
    'pyhaloxmlc',
    'src/pyhaloxmlc/pyhaloxmlc.c',
    install: true,
)

install_subdir('src/pyhaloxml', install_dir : py.get_install_dir(pure: false))