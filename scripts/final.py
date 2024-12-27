

# The data is here
root_path = "/Volumes/MENTALFIT/MENTALFIT/ESTUDIO 2/3.BD_Análisis/CASCO EEG MENTALFIT TODO"


df = build_dataframe_with_paths(root_path)
"""
df is:

identifier | Gender | Centre | title | sampling_rate | channels | headset | path
-----------+--------+--------+---------------+----------+---------+-------}
01         | XX     | C1      |"titl" |                                     root_path + path_to_edf_01
02         | XX     | C1      |"titl" |                                     root_path + path_to_edf_02
03         | XX     | C1      |"titl" |                                     root_path + path_to_edf_03
04         | XX     | C1      |"titl" |                                     root_path + path_to_edf_04
...

"""

# filter the dataframe with all files
df_ = df[ df["sampling_rate"] == 128 & df["Centre"] == "C1" ]

# get path files
paths_to_edf = df_["path"]


# define functio to be applied

def function(raw):
    # sampling
    raw.sample(125)

    # 
    raw = raw.pick(ch_names)
    montage = mne.channels.make_standard_montage('standard_1020') 
    
    raw.info.set_montage(montage)
    raw.info.get_montage().get_positions()

    ica = mne.preprocessing.ICA(
        method=method,
        n_components=n_components, 
        noise_cov=cov, 
        max_iter=max_iter, 
        fit_params=fit_params, 
        verbose=True)

    ica.fit(sample.raw)   
    ica_srcs = ica.get_sources(sample.raw).get_data()
    return ica_srcs

## 
# resultados = apply_to_files(paths_to_edf, function)
resultados = apply_to_raw(paths_to_edf, function)

{ "path_edf_01": ica_srcs_edf_01}


print()