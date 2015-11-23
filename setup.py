
from setuptools import setup

setup(name='My_Python_Apps', version='1.0',
      description='Code for Image to Thumbnails and text files to PDF conversion.',
      author='S S Krishna Vutukuri', author_email='sskrishna.vutukuri@gmail.com',
      url='http:localhost:/5000/upload',

      #  Uncomment one or more lines below in the install_requires section
      #  for the specific client drivers/modules your application needs.
      install_requires=['flask', 'PIL', 'wkhtmltopdf', 'Image', 'python-crontab']
     )
