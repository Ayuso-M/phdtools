# phdtools
Library with tools for my PhD.

## How to install the library

If you want to install in editable mode (changes in the source code are reflected), use:

```terminal
python -m pip install -e .
```

Otherwise, you can just do:

```terminal
python -m pip install .
```

The only dependency is [mne](mne.tools).
If you want to install also the extra libraries such as Jupyter Notebooks and IPython, just do:

```terminal
python -m pip install '.[extra]'
```
