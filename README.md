<p float="left">
<img src="./img/logos/logos.png" width="350">
</p>

# JPEG Transcoding for DNA based storage 
## Bachelor Semester Project - École Polytechnique Fédérale de Lausanne, Computer and Communication Sciences

The goal of this project is to study the state of the art in DNA storage and coding, and develop a transcoding module that encodes the quantized DCT coefficients of an already compressed JPEG file with DNA nucleotides, which in turn is then integrated with a DNA sequencing, storage and synthesis simulator. 
This repository contains the transcoding module which has been built by modifying the software used to encode DNA images - JPEG DNA - developed by the Mediacoding group in the I3S laboratory, in agreement with the standards described by the Jpeg DNA research group in - *DNA-based Media Storage - State-of-the-Art, Challenges, Use Cases and Requirements*. 

## Installation
To install the required packages and set up the transcoder you need to have *pip* and *homebrew* installed.

#### First we set up the JPEG_DNA_Transcoder repository:
To install the repository use the following command at the root of the repository’s folder:
```
pip install -r requirements.txt
```
To use the commands from the terminal install the following package at the root of the folder: 
```
python setup.py install
```
#### Then we set up the Python wrapper for the *ibjpeg* C library:
```
brew install libjpeg
```
```
pip install Cython
```
Please update the include and lib paths in *setupWrapper.py* such that they point to your installation. 
```python
libjpeg_include_dir = "path/to/libjpeg/build/include"
libjpeg_lib_dir = "path/to/libjpeg/build/lib"
```
Tip: Run the following command in order to find the path to *libjpeg*:
```
brew info libjpeg
```
To install the header files needed to build Python extensions: (you can probably skip this step if you already have all the needed developer tools like gcc,...)
```
pip install python3-dev
```
Finally, to compile the extension for use in the project’s root directory, run the following in the
root of the */Jpeg_DNA_Transcoder* directory: 
```
python setupWrapper.py build_ext −−inplace
```

## Functionality
### Encoding
To encode a JPEG file into DNA nucleotides you will have to specify the path of your JPEG image and the path on which you would like to store the output DNA sequence.
```
 python -m jpegdna.scripts.jpegdnargb_encode $IMG_PATH.jpg $DNA_OUT_PATH
 ```
 Please note that the terminal will print the type of Chroma Subsampling of the JPEG file. You will have to remember this when decoding the DNA sequence.
 
 ### Decoding
To decode a DNA sequence back to a JPEG file you will have to specify first the type of Chroma Subsampling of the original JPEG image (simply copy the output of the encoder), the path of the DNA sequence, and finally the path on which you would like to store the output decoded PNG file. You also have to specify that no formatting was used.
 ```
 python -m jpegdna.scripts.jpegdnargb_decode $SUBSAMPLING $DNA_IN_PATH $IMG_OUT_PATH.png no_format
```
Example for first parameter: $SUBSAMPLING = 4:2:0

### Credit:
The original JPEG DNA software can be found on [Jpeg_DNA_Python](https://github.com/jpegdna-mediacoding/Jpeg_DNA_Python). <br>
The adapted python wrapper can be found on [dct-coefficient-decoder](https://github.com/btlorch/dct-coefficient-decoder).