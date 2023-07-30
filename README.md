# Online-Trivia
SFU CMPT 371 Project - Group 23

## Frontend setup
***the complete app will be eventually be deployed onto the streamlit website, so feel free to skip this if you don't care about running it locally before then!!!***

HIGHLY recommend to install Streamlit in a virtual environment since it installs so many dependencies. Conda is recommended and easy to use, but feel free to use your preferred package management tool.

- Install Conda: https://docs.conda.io/en/latest/miniconda.html
- (only if using Windows) Open the Anaconda Prompt (miniconda3)
- Create Conda environment
```
conda create -n trivia
conda activate trivia
```
- Install Streamlit in Conda virtual env

```
pip install streamlit
```
- Activate whenever you want to run the app :)
```
conda activate trivia
cd Multiplayer-Trivia
streamlit run app.py
```

See the website for more information on installation: https://docs.streamlit.io/library/get-started/installation
