from glob import glob
from setuptools import setup

setup(
    name='gaia_op3_sim', version='0.1.0',
    packages=['gaia_op3_sim'],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/gaia_op3_sim']),
        ('share/gaia_op3_sim', ['package.xml', 'LICENSE']),
        ('share/gaia_op3_sim/launch', glob('launch/*.launch.py')),
        ('share/gaia_op3_sim/config', glob('config/*.yaml')),
        ('share/gaia_op3_sim/worlds', glob('worlds/*.sdf')),
    ],
    install_requires=['setuptools'], zip_safe=True,
    maintainer='Equipe Gaia',
    maintainer_email='pedronsjaja@users.noreply.github.com',
    description='Laboratorio de simulacao OP3 para a equipe Gaia',
    license='MIT',
)
