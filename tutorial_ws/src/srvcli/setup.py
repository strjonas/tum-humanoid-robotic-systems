from setuptools import find_packages, setup

package_name = 'srvcli'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jonas',
    maintainer_email='48125614+strjonas@users.noreply.github.com',
    description='String processing service server and keyboard client.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'server = srvcli.server:main',
            'client = srvcli.client:main',
        ],
    },
)
