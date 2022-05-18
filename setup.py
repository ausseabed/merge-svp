from setuptools import setup, find_packages

setup(
    name='merge-svp',
    namespace_packages=['mergesvp'],
    version='0.0.1',
    url='https://github.com/ausseabed/merge-svp',
    author=(
        "Lachlan Hurst;"
    ),
    author_email=(
        "lachlan.hurst@gmail.com;"
    ),
    description=(
        "Command line utility for merging Sound Velocity "
        "Profiles into single file format supported by Teledyne CARIS"
    ),
    entry_points={
        "gui_scripts": [],
        "console_scripts": [
            'mergesvp = mergesvp.mergesvp:main',
        ],
    },
    packages=[
        'mergesvp',
        'mergesvp.lib'
    ],
    zip_safe=False,
    package_data={},
    install_requires=[
        'Click'
    ],
    tests_require=['pytest'],
)
