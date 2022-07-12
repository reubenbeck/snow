# snow

Used conda environment, a .yml, file to load in the packages. 

Came up with an error: Original error was: DLL load failed: The specified module could not be found.

This happened when selecting Conda Environment as the python interpreter. 
Solution:
https://stackoverflow.com/questions/54063285/numpy-is-already-installed-with-anaconda-but-i-get-an-importerror-dll-load-fail

Added these to the System Environment Path: Settings-->System-->Advanced System Settings --> Environment Variables --> User variables --> Path --> New: then add below
C:\Users\<myusername>\AppData\Local\Continuum\Anaconda3\Scripts\
C:\Users\<myusername>\AppData\Local\Continuum\Anaconda3\Library\
C:\Users\<myusername>\AppData\Local\Continuum\Anaconda3\Library\bin\
C:\Users\<myusername>\AppData\Local\Continuum\Anaconda3\Library\mingw-w64\bin\

(Directories may look different depending on where Anaconda is installed)
