# Analysis of the scratch (wound-healing) assay repo

Companion repository for "Proton-gated anion transport governs endocytic vacuole shrinkage" by Mariia Zeziulia, Sandy Blin, Franziska W. Schmitt, Martin Lehmann, Thomas J. Jentsch

# Installation 

To run the Python code in this repo, we recommend building a virtual environment using `venv` and the provided `requirements.txt` file, which 
will install all of the required dependencies for you:

```
python3 -m venv my_env
source my_env/bin/activate
pip install -r requirements.txt
```

# Usage

You can run the code using an IPython kernel (e.g. in VSCode or Spyder or Pycharm) open up the file `run.py` in your IDE of choice and then provide the path to a folder with images for analysis and enter all conditions in 1 line separated with spaces

Every step in image analysis has a plotting function included, which can be deleted or commented out for the time reasons