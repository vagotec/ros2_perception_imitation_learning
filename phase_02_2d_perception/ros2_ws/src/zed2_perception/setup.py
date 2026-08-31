from setuptools import find_packages, setup

package_name = 'zed2_perception'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sarvg',
    maintainer_email='sarvg@web.de',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'zed_rgb_viewer = zed2_perception.step01_zed_rgb_viewer:main',
            'zed_2d_perception = zed2_perception.step02_2d_perception:main',
        ],
    },
)
