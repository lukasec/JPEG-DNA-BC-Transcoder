"""Setting up package for pip"""
from setuptools import setup, find_packages
with open("README.md", "r", encoding="UTF-8") as fh:
    long_description = fh.read()

setup(name="jpegdna",
      version="0.0b1",
      author="Xavier Pic, Eva Gil San Antonio, Melpomeni Dimopoulou, Marc Antonini",
      author_email="xpic@i3s.unice.fr, gilsanan@i3s.unice.Fr, dimopoulou@i3s.unice.fr, am@i3s.unice.fr",
      description="Packages gathering methods \
          for compressing and encoding images into DNA",
      long_description=long_description,
      long_description_content_type="test/markdown",
      url="https://github.com/jpegdna-mediacoding/Jpeg_DNA_Python",
      packages=find_packages(),
      package_data={'jpegdna': ['data/*', '../img/*']},
      python_requires=">=3.8",
      install_requires=["numpy", "scipy", "scikit-image", "argparse", "configparser", "opencv-python", "pandas"],
      entry_points="""
      [console_scripts]
      jdnae = jpegdna.scripts.encode:main
      jdnad = jpegdna.scripts.decode:main
      jdnat = jpegdna.scripts.eval:main
      """)
