# Proto-Altekhsnan Text Converter #

### About ###
This project is a fairly simple Flask-based web application that serves as tool to generate Proto-Altekhsnan passage from plain text input. This application is developed as part of collaborative original fantasy fiction project *Lascantia of the Horizon* project, intended for manually rendering constructed language Proto-Altekhsnan in case the OpenType lookup table feature of the font file does not work.


### Requirements ###
To run this application locally, the latest version of following packages are required:
* Python 3
* Flask and its dependencies
* virtualenv (not necessary, but may be needed to run the server in isolated environment)

### Installing and running the application ###
The author uses Python distribution provided by Conda, specifically [Miniconda](https://conda.io/miniconda.html). To get the application up and running using (Mini)conda distribution, the steps are:
* Download and install the Miniconda3 (NOT Miniconda, which is based on Python 2.7) distribution for your platform.
* Open the command line and create a new environment. For example, to create a new environment called 'myenv' with the aforementioned packages, type:
    conda create --name myenv python flask
* Type 'y' when prompted. This will create a new Conda environment. Make sure you are connected to the Internet to download the packages.
* Once the environment is successfully created, type:
    source activate myenv
    activate myenv (Windows)
* Redirect to the directory of this project. Before running the server, set the environment variable FLASK_APP to the name of the application's Python file, i.e. *transliteration.py*. For example:
    D:\projects\ProtoAltekhsnanLangToolkit\>set FLASK_APP=transliteration.py (CLI)
    PS D:\projects\ProtoAltekhsnanLangToolkit\>$env:FLASK_APP = "transliteration.py" (PowerShell)
    $ export FLASK_APP=transliteration.py (Bash)
* Run the server by typing:
    flask run
    python -m flask run
* Open the browser and access the application at http://127.0.0.1:5000/

Do note that if you make changes to the code and the debugger mode of Flask is not turned on, you have to manually restart the server.

### Testing ###
This application is tested on Google Chrome browser running on Windows 10 64-bit so far.

### Current issues ###
* In-lore, the Proto-Altekhsnan language has limited use, and therefore limited characters. The language has no numerical system, and punctuations are almost nonexistent in the language (only four symbols are used within the font file, namely '-' to remove vowels, '=' to separate syllables manually, and <> as quotation marks). However, the text area currently does not limit the input, and thus weird things may happen if characters outside the ones established within the font file are inputted.
* Related to above, the syllable breakdown currently utilizes for loop which while functionally works for 'normal' input, is not properly equipped to anticipate the 'illegal' inputs.
* Improper rendering when '<' and/or '>' is within input.

### Contact ###
Twitter: @euclapetus/@exclaebur
E-mail: claedonica@gmail.com
### Contact ###
