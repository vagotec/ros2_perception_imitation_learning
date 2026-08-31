from setuptools import find_packages, setup

package_name = 'zed2_object_localization'

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
            'pixel_to_3d = zed2_object_localization.step01_pixel_to_3d:main',
            'object_to_3d = zed2_object_localization.step02_object_to_3d:main',
            'zed_object_detection = zed2_object_localization.step03_zed_object_detection:main',
            'object_to_robot_frame = zed2_object_localization.step04_object_to_robot_frame:main',
        ],
    },
)
