## Data visualization scratch

A project for incubating and tempating basic data visualization and wrangling using Python 3.9.

### Setup

```bash
cd .../automata
```

```bash
mkvirtualenv --python=`which python` automata
[automata] pip install -r environment.txt
[automata] pip install -r requirements.txt
```

```bash
[automata] python -m ipykernel install --user --name 'automata_env' --display-name 'automata (Python 3, venv)'
[automata] jupyter labextension list
```

#### Clean start

```bash
[automata] jupyter kernelspec remove automata_env
rmvirtualenv automata
```

or if Jupyter is the problem just try

```bash
jupyter lab clean --all
jupyter lab build
```

### Use

```bash
cd .../automata
workon automata
[automata] jupyter lab
```

Optionally (before `jupyter lab`), update packages:

```bash
[automata] pip install -U -r environment.txt --upgrade-strategy eager
[automata] pip install -U -r requirements.txt --upgrade-strategy eager
```

and then either

```bash
[dataviz] jupyter lab build
[dataviz] jupyter labextension list
```
or manage extensions using the extension manager.


### TBD

#### Additional commands

```bash
[dataviz] jupyter labextension list
```

```bash
[dataviz] pip list --outdated
```

#### Environment

- More [detailed configuration](http://holoviews.org/user_guide/Installing_and_Configuring.html) (esp. overcoming rate limiting)
- Review [Jupyter Lab features and extensions](https://towardsdatascience.com/jupyter-lab-evolution-of-the-jupyter-notebook-5297cacde6b)
- Better collapsing or section navigation?

