# Workflow eeg preprocessing and processing
## Resampling
### Nyquist frequency

El casco lo tenemos sampleando a 256 Hz, entonces: 128 Hz 

#### Teoría:

La frecuencia de Nyquist es la mitad de la frecuencia de muestreo y marca la frecuencia máxima que puede
representarse sin errores al digitalizar una señal. Si grabas a 256 Hz, la frecuencia de Nyquist es 128 Hz;
al hacer resampling a 128 Hz, pasa a ser 64 Hz.
Antes de reducir el muestreo, se filtran las frecuencias mayores al nuevo límite (64 Hz) para evitar
distorsión (aliasing).

[Wikipedia-Nyquist](https://en.wikipedia.org/wiki/Nyquist_frequency)

#### Codigo

```python
raw = raw.resample(125)
```

## Bp filter (2nd step)

### Teoría: 

Cuando pasa filtros probablemente sobre eso te haga fft y luego te la deshaga!

High pass – 50 Hz
Low pass – 1 Hz

### Python Código from mne: 

 ```python
 raw.filter(l_freq=1, h_freq=50)
 ```
