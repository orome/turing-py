## Data visualization scratch

A project for incubating and tempating basic data visualization and wrangling using Python 3.8.

### Setup

```bash
cd .../automata
```

```bash
mkvirtualenv --python=`which python3` automata
[automata] pip install -r environment.txt
[automata] pip install -r requirements.txt
```

```bash
[automata] python -m ipykernel install --user --name 'automata_env' --display-name 'automata (Python 3, venv)'
[automata] jupyter labextension install @pyviz/jupyterlab_pyviz
[automata] jupyter labextension install @jupyterlab/git
[automata] jupyter labextension install @jupyterlab/toc
[automata] jupyter serverextension enable --py jupyterlab_git
[automata] jupyter nbextension enable --py widgetsnbextension --sys-prefix
[automata] jupyter labextension install @jupyter-widgets/jupyterlab-manager
[automata] jupyter labextension list
```

### Use

```bash
cd .../automata
[automata] workon automata
[automata] jupyter lab
```

Optionally, before `jupyter lab`, update packages:

```bash
[automata] pip install -U -r environment.txt
[automata] pip install -U -r requirements.txt
[automata] jupyter labextension install @pyviz/jupyterlab_pyviz
[automata] jupyter labextension install @jupyterlab/git
[automata] jupyter labextension install @jupyterlab/toc
[automata] jupyter serverextension enable --py jupyterlab_git
[automata] jupyter nbextension enable --py widgetsnbextension --sys-prefix
[automata] jupyter labextension install @jupyter-widgets/jupyterlab-manager
[automata] jupyter labextension list
```

```bash
[dataviz] pip list --outdated
```

### TBD

#### Additional commands

```bash
jupyter labextension list
```
#### Environment

- See about using the extension manager?
- More [detailed configuration](http://holoviews.org/user_guide/Installing_and_Configuring.html) (esp. overcoming rate limiting)
- Review [Jupyter Lab features and extensions](https://towardsdatascience.com/jupyter-lab-evolution-of-the-jupyter-notebook-5297cacde6b)
- Better collapsing or section navigation?

