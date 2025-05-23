# -*- coding: utf-8 -*-
"""komposisi

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1uV1vlEdXlWeaD91oXpMyuJrrOsBEWlys
"""

import pandas as pd

from google.colab import drive
drive.mount('/content/drive')

# Replace 'your_file_path.csv' with the actual path to your CSV file in Google Drive
df = pd.read_csv('/content/drive/MyDrive/DATA MINING/skinsort produk.csv')
print(df.head())

df.info()

"""# CEK DUPLICATED"""

df.duplicated().sum()

"""# CEK MISSING VALUE"""

df.isnull().sum()

"""# PENANGANAN MISSING VALUE"""

# Fill missing values in numerical columns with the mean
for col in df.select_dtypes(include=['number']):
    df[col] = df[col].fillna(df[col].mean())

# Fill missing values in categorical columns with the mode (most frequent value)
for col in df.select_dtypes(include=['object']):
    df[col] = df[col].fillna(df[col].mode()[0])

print(df.isnull().sum())

"""# PROSES ONEHOT ENCODING

> KOLOM EFEK SAMPING
"""

# 2. Bersihkan semua karakter aneh, lalu split dan buang item kosong
df['concerns'] = df['concerns'].apply(
    lambda x: [
        i.strip().replace('[','').replace(']','').replace('"','').replace("'", '')
        for i in x.split(',')
        if i.strip().replace('[','').replace(']','').replace('"','').replace("'", '') != ''
    ]
)

# Explode dan filter NaN
all_concerns = df['concerns'].explode()
all_concerns = all_concerns[all_concerns.notna()]  # <-- penting
unique_concerns = sorted(all_concerns.unique())

print("concerns unik:")
for i, concerns in enumerate(unique_concerns, 1):
    print(f"{i}. {concerns}")

for m in unique_concerns:
    df[m] = df['concerns'].apply(lambda x: 1 if m in x else 0)

# Tampilkan hasil
print("\nContoh data setelah one-hot encoding concerns:")
print(df.head())

df.info()

"""# MENGHAPUS KOLOM YANG TIDAK TERPAKAI"""

df = df.drop(columns=['web scraper order','web scraper start url','link','link href','klaim','deskripsi','match()','manfaat','concerns','komposisi_utama','manfaat','brand','nama_produk'])
df.info()

"""# MENGUBAH NAMA KOLOM

> mengubah nama kolom tipe menjadi kategori
"""

df = df.rename(columns={'tipe': 'kategori'})

"""

> mengubah nama kolom menjadi huruf kecil semua

"""

df.columns = df.columns.str.lower()

df.head(5)

"""# TEKS PREPROCESSING"""

import re

"""KOLOM KOMPOSISI"""

print(df['komposisi'])

def bersihkan_komposisi(teks):
    if not teks or not isinstance(teks, str):
        return ''
    # Lowercase
    teks = teks.lower()
    # Hapus angka yang diikuti persen (contoh: '2%', '5%')
    teks = re.sub(r'\d+\s*%', '', teks)
    # Hapus karakter non-alfanumerik kecuali koma
    teks = re.sub(r'[^\w\s,]', '', teks)
    # Hilangkan spasi sebelum/sesudah koma
    teks = ','.join([i.strip() for i in teks.split(',') if i.strip()])
    # Hilangkan spasi berlebih
    teks = re.sub(r'\s+', ' ', teks).strip()
    return teks

df['komposisi'] = df['komposisi'].apply(bersihkan_komposisi)
print(df['komposisi'])

"""# PROSES TF IDF KOLOM KOMPOSISI_UTAMA"""

from sklearn.feature_extraction.text import TfidfVectorizer

# Inisialisasi TF-IDF Vectorizer
tfidf_vectorizer = TfidfVectorizer(
    min_df = 1,
    max_features= 5000,      # maksimal fitur yang diambil
    ngram_range = (1,3)
)

# TF-IDF Vectorizer dengan tokenisasi koma
tfidf = TfidfVectorizer(token_pattern=r'[^,]+')
X_tfidf = tfidf.fit_transform(df['komposisi'])

# Lihat dimensi hasil TF-IDF matrix
print(f"Shape TF-IDF matrix: {X_tfidf.shape}")

feature_names = tfidf.get_feature_names_out()

# Print all feature names
print("All Feature Names:")
for feature in feature_names:
    print(feature)

tfidf_df = pd.DataFrame(X_tfidf.toarray(), columns=feature_names)
print(tfidf_df.head(10))

"""# SIMPAN DATASET YANG SUDAH BERSIH"""

df.to_csv('/content/drive/MyDrive/DATA MINING/cleaned_skinsort_last.csv', index=False)

"""# SPLIT DATA"""

print(df.columns[2:8])

# Pastikan kolom composition_cleaned sudah ada dan berisi string bahan
X = X_tfidf
y = df.iloc[:, 2:8]    # kolom target

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

"""# IMBALANCED CLASS"""

# 5. Transform TF-IDF setelah split agar panjangnya konsisten
X_train = tfidf.transform(X_train_text)
X_test = tfidf.transform(X_test_text)

!pip install --upgrade scikit-learn

from imblearn.over_sampling import SMOTE

# 5. SMOTE per label (label-wise)
X_res_all = []
y_res_all = []

for col in y_train.columns:
    sm = SMOTE(random_state=42)
    X_col_res, y_col_res = sm.fit_resample(X_train, y_train[col])

    X_res_all.append(X_col_res)
    y_res_all.append(pd.DataFrame(y_col_res, columns=[col]))

"""# MODEL RANDOM FOREST"""

# Replace 'your_file_path.csv' with the actual path to your CSV file in Google Drive
df2 = pd.read_csv('/content/drive/MyDrive/DATA MINING/DATASETCLEAR.csv')
print(df2.head())

from sklearn.ensemble import RandomForestClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, hamming_loss

target_columns = [
    'acne fighting', 'anti aging', 'brightening', 'dark spots',
    'good for oily skin', 'hydrating', 'redness reducing',
    'reduces irritation', 'reduces large pores', 'scar healing',
    'skin texture', 'acne trigger', 'drying', 'eczema', 'irritating',
    'may worsen oily skin', 'rosacea'
]

# Ambil fitur dan target
X = X_tfidf  # hasil TF-IDF dari komposisi_utama
y = df2[target_columns].values  # target multi-label biner

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Inisialisasi model
model = OneVsRestClassifier(RandomForestClassifier(random_state=42))

# Training
model.fit(X_train, y_train)

# Prediksi
y_pred = model.predict(X_test)

# Evaluasi
print(classification_report(y_test, y_pred, target_names=target_columns))
print("Hamming Loss:", hamming_loss(y_test, y_pred))

# prompt: evaluasi model

# Evaluasi model dengan metrik tambahan
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# ... (sebelumnya kode yang sudah ada)

# Prediksi
y_pred = model.predict(X_test)

# Evaluasi
print(classification_report(y_test, y_pred, target_names=target_columns))
print("Hamming Loss:", hamming_loss(y_test, y_pred))

# Metrik tambahan
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='micro')  # Gunakan 'micro' untuk multi-label
recall = recall_score(y_test, y_pred, average='micro')
f1 = f1_score(y_test, y_pred, average='micro')

print(f"Accuracy: {accuracy}")
print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1-score: {f1}")

"""# Imbalanced Data"""

import matplotlib.pyplot as plt

df2[target_columns].sum().sort_values().plot(kind='barh', figsize=(10,6))
plt.title('Jumlah Label Positif per Kategori')
plt.xlabel('Jumlah')
plt.ylabel('Label')
plt.show()

import matplotlib.pyplot as plt

# Hitung jumlah label 0 (negatif) untuk setiap kolom
negatif_counts = (df2[target_columns] == 0).sum().sort_values()

# Visualisasikan
negatif_counts.plot(kind='barh', figsize=(10,6), color='salmon')
plt.title('Jumlah Label Negatif (0) per Kategori')
plt.xlabel('Jumlah')
plt.ylabel('Label')
plt.show()