<p float="left">
<img src="./img/logos/logos.png" width="350">
</p>

# JPEG Transcoding for DNA based storage 
## Bachelor Semester Project - École Polytechnique Fédérale de Lausanne (EPFL), Computer and Communication Sciences

The goal of this project is to study the state of the art in DNA storage and coding, and develop a transcoding module that encodes the quantized DCT coefficients of an already compressed JPEG file with DNA nucleotides, which in turn is then integrated with a DNA sequencing, storage and synthesis simulator. 
This repository contains the transcoding module which has been built by modifying the software used to encode DNA images - JPEG DNA - developed by the Mediacoding group in the I3S laboratory, in agreement with the standards described by the Jpeg DNA research group in their public document - *DNA-based Media Storage - State-of-the-Art, Challenges, Use Cases and Requirements*. The original software can be found on [Jpeg_DNA_Python](https://github.com/jpegdna-mediacoding/Jpeg_DNA_Python).

## Installation
First we set up the JPEG_DNA_Transcoder repository:
You need to have *pip* installed.
To install the repository use the following command at the root of the repository’s folder:
```
pip install -r requirements.txt
```
To use the commands from the terminal you need to also install the following package at the root of the folder: 
```
python setup.py install
```
We also need to set up the Python wrapper for the *ibjpeg* library:
You need to have  *homebrew* installed and run the following lines in your terminal:
```
brew install libjpeg
```
You also need to install Cython:
```
pip install Cython
```
Please update the include and lib paths in *setupWrapper.py* such that they point to your installation. 
```python
libjpeg_include_dir = "path/to/libjpeg/build/include"
libjpeg_lib_dir = "path/to/libjpeg/build/lib"
```
For this run the following command line in order to find the path to *libjpeg*:
```
brew info libjpeg
```
Run the following to install the header files needed to build Python extensions.
```
pip install python3-dev
```
tFinally to compile the extension for use in the project’s root directory, run the following in the
root of the folder */Jpeg_DNA_Transcoder*: 
```
python setupWrapper.py build_ext −−inplace
```

## Functionality
### Encoding
To encode a JPEG file into DNA nucleotides you will have to specifiy the path of your JPEG image, the path on which you would like to store the output DNA sequence and the path you would like to store the quantization tables of the JPEG file which will be needed for encoding.
```
 python -m jpegdna.scripts.jpegdnargb_encode \$IMG_PATH.jpg \$DNA_OUT_PATH
 \$QUANTIZATION_TABLES_OUT_PATH.npz
 ```
 
 ### Decoding
To decode a DNA sequence back to a JPEG file you will have to specify first the type of Chroma Subsampling of the original JPEG image (simply copy the ouput of the encoder), the path of the quantization tables, the path of the DNA sequence, and finally the path on which you would like to store the output decoded PNG file.
 ```
 python -m jpegdna.scripts.jpegdnargb_decode \$SUBSAMPLING \$QUANTIZATION_TABLES_PATH.npz
 \$DNA_IN_PATH \$IMG_OUT_PATH.png no_format
  ```