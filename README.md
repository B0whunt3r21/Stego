# Stego
LSB - Steganography tool

![Stego Icon](/assets/Stego.png)


Uses a password to encrypt / decrypt a message into a given image.

 - Supports UTF-8 charset.
 - Random seeded bit positions
 - AES cypher


## Installation
To install the tool, copy the repo and use pip to install the requirements.

 > pip install -r requirements.txt


 It is recommended to create an virtual environment (venv) first.


## Usage
After the installation just place the image you want to de- / en-code inte the 'in' folder of the project ond run the main.
Also add the file you want to mask in the image to the folder.

 > python main.py

 After starting the application, a TUI interfare should appear where one can select the mode, input file(s) - depending en the mode, name the output file (.png in encode mode can be omitted, arbitrary suffix in decode mode), and set the password.

> [!WARNING]
 > For the encoding a lossless image type, like png is needed. jpg would currupt the data.

All the output file are to be found in the 'out' directory.


### TODO
 - Labels Vertical alignment
 - Optional: Image embedding?

