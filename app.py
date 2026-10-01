"""Proyek Mini #2 - Sistem Klasifikasi Data dengan Himpunan (Pertemuan 6)
Jalankan: streamlit run app.py
"""
from itertools import combinations
import io

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib_venn import venn2, venn3

# ---------- Dataset contoh (kolom: item, kategori) ----------
SAMPLES = {
    "Dataset 1 - Ekstrakurikuler Mahasiswa": {
        "Basket": {"Ani", "Budi", "Citra", "Dedi", "Eka", "Fajar"},
        "Musik": {"Citra", "Eka", "Gita", "Hana", "Indra"},
        "Programming": {"Budi", "Eka", "Hana", "Joko", "Kiki", "Citra"},
    },
    "Dataset 2 - Pelanggan Toko Online": {
        "Buku": {"P01", "P02", "P03", "P04", "P05"},
        "Elektronik": {"P03", "P05", "P06", "P07"},
        "Fashion": {"P02", "P05", "P07", "P08", "P09", "P10"},
    },
}


def load_csv(file) -> dict:
    df = pd.read_csv(file)
    df.columns = [c.strip().lower() for c in df.columns]
    out = {}
    for kat, grp in df.groupby("kategori"):
        out[str(kat)] = set(grp["item"].astype(str))
    return out


# ---------- Operasi himpunan ----------
def universe(data):
    return set().union(*data.values())


def union(*sets):
    return set().union(*sets)


def intersection(*sets):
    return set.intersection(*sets)


def difference(a, b):
    return a - b


def complement(a, U):
    return U - a


# ---------- Prinsip Inklusi-Eksklusi ----------
def pie_steps(data: dict):
    """Kembalikan (total, daftar_suku). Suku: (tanda, kombinasi, ukuran)."""
    names = list(data)
    terms, total = [], 0
    for r in range(1, len(names) + 1):
        sign = 1 if r % 2 == 1 else -1
        for combo in combinations(names, r):
            size = len(set.intersection(*(data[n] for n in combo)))
            terms.append((sign, combo, size))
            total += sign * size
    return total, terms


# ---------- Visualisasi ----------
def draw_venn(data: dict, names: list):
    fig, ax = plt.subplots(figsize=(5, 5))
    sets = [data[n] for n in names]
    if len(sets) == 2:
        venn2(sets, set_labels=names, ax=ax)
    elif len(sets) == 3:
        venn3(sets, set_labels=names, ax=ax)
    else:
        st.info("Diagram Venn hanya untuk 2 atau 3 himpunan.")
        return None
    return fig


# ---------- UI ----------
st.title("Sistem Klasifikasi Data dengan Himpunan")
src = st.sidebar.radio("Sumber data", list(SAMPLES) + ["Unggah CSV"])
if src == "Unggah CSV":
    f = st.sidebar.file_uploader("CSV dengan kolom: item, kategori", type="csv")
    data = load_csv(f) if f else {}
else:
    data = SAMPLES[src]

if not data:
    st.warning("Pilih dataset atau unggah CSV (kolom: item,kategori).")
    st.stop()

U = universe(data)
st.subheader("1. Data input")
st.write(f"Semesta U ({len(U)} elemen): {sorted(U)}")
st.dataframe(pd.DataFrame({k: [", ".join(sorted(v))] for k, v in data.items()},
                          index=["Anggota"]).T)

st.subheader("2. Operasi himpunan")
op = st.selectbox("Operasi", ["Union (∪)", "Intersection (∩)",
                               "Difference (A − B)", "Complement (A')"])
cats = list(data)
if op.startswith(("Union", "Intersection")):
    pick = st.multiselect("Pilih kategori", cats, default=cats[:2])
    if len(pick) >= 2:
        sets = [data[k] for k in pick]
        res = union(*sets) if op.startswith("Union") else intersection(*sets)
        st.success(f"Hasil ({len(res)}): {sorted(res)}")
elif op.startswith("Difference"):
    a = st.selectbox("A", cats, 0)
    b = st.selectbox("B", cats, min(1, len(cats) - 1))
    res = difference(data[a], data[b])
    st.success(f"{a} − {b} ({len(res)}): {sorted(res)}")
else:
    a = st.selectbox("A", cats)
    res = complement(data[a], U)
    st.success(f"Komplemen {a} terhadap U ({len(res)}): {sorted(res)}")

st.subheader("3. Diagram Venn")
vp = st.multiselect("Kategori untuk Venn (2-3)", cats, default=cats[:3], key=f"venn_{src}")
if len(vp) in (2, 3):
    fig = draw_venn(data, vp)
    st.pyplot(fig)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    st.download_button("Unduh PNG", buf.getvalue(), "venn.png", "image/png")

st.subheader("4. Prinsip Inklusi-Eksklusi (PIE)")
pp = st.multiselect("Kategori untuk PIE", cats, default=cats, key=f"pie_{src}")
if pp:
    total, terms = pie_steps({k: data[k] for k in pp})
    rows = [{"Tanda": "(+) tambah" if s > 0 else "(−) kurang",
             "Irisan": " ∩ ".join(c), "|Irisan|": n} for s, c, n in terms]
    st.table(pd.DataFrame(rows))
    expr = " ".join(f"{'+' if s > 0 else '-'} {n}" for s, _, n in terms).lstrip("+ ")
    actual = len(union(*(data[k] for k in pp)))
    st.write(f"|∪| = {expr} = **{total}**")
    st.write(f"Verifikasi dengan union langsung: {actual} → "
             f"{'✅ cocok' if total == actual else '❌ tidak cocok'}")


# ---------- Tambahan sesuai materi Pertemuan 6 ----------
def regions3(a, b, c, U):
    """8 daerah Diagram Venn 3 himpunan (2^3 = 8), termasuk di luar semuanya."""
    return {
        "Hanya A  (A ∩ B' ∩ C')": a - b - c,
        "Hanya B  (A' ∩ B ∩ C')": b - a - c,
        "Hanya C  (A' ∩ B' ∩ C)": c - a - b,
        "A dan B saja (A ∩ B ∩ C')": (a & b) - c,
        "A dan C saja (A ∩ B' ∩ C)": (a & c) - b,
        "B dan C saja (A' ∩ B ∩ C)": (b & c) - a,
        "A, B, dan C (A ∩ B ∩ C)": a & b & c,
        "Bukan A/B/C  (A ∪ B ∪ C)'": U - (a | b | c),
    }


def sql_equivalents(data, x, y):
    """Jalankan UNION / INTERSECT / EXCEPT di SQLite dan kembalikan hasilnya."""
    import sqlite3
    con = sqlite3.connect(":memory:")
    for name, key in (("tx", x), ("ty", y)):
        con.execute(f"CREATE TABLE {name}(item TEXT)")
        con.executemany(f"INSERT INTO {name} VALUES (?)", [(i,) for i in data[key]])
    q = {
        "UNION": "SELECT item FROM tx UNION SELECT item FROM ty",
        "INTERSECT": "SELECT item FROM tx INTERSECT SELECT item FROM ty",
        "EXCEPT": "SELECT item FROM tx EXCEPT SELECT item FROM ty",
    }
    return {k: (v, {r[0] for r in con.execute(v)}) for k, v in q.items()}


st.subheader("5. Tabel 8 daerah (3 himpunan)")
if len(cats) >= 3:
    t3 = st.multiselect("Pilih tepat 3 kategori", cats, default=cats[:3], key=f"r3_{src}")
    if len(t3) == 3:
        reg = regions3(*(data[k] for k in t3), U)
        st.table(pd.DataFrame([{"Daerah": k, "Jumlah": len(v), "Anggota": ", ".join(sorted(v))}
                               for k, v in reg.items()]))
        st.caption(f"Total semua daerah = {sum(len(v) for v in reg.values())} = |U| = {len(U)}")

st.subheader("6. Kalkulator PIE dari angka kardinalitas")
st.caption("Masukkan angka seperti pada soal cerita. Aplikasi memeriksa konsistensi terhadap |U|.")
mode = st.radio("Jumlah himpunan", [2, 3], horizontal=True)
c1, c2, c3 = st.columns(3)
nA = c1.number_input("|A|", 0, value=600 if mode == 3 else 25)
nB = c2.number_input("|B|", 0, value=500 if mode == 3 else 18)
nAB = c3.number_input("|A∩B|", 0, value=250 if mode == 3 else 10)
uni = st.number_input("|U| (semesta)", 0, value=1000 if mode == 3 else 40)
if mode == 2:
    tot = nA + nB - nAB
    st.write(f"|A∪B| = {nA} + {nB} − {nAB} = **{tot}**")
else:
    d1, d2, d3, d4 = st.columns(4)
    nC = d1.number_input("|C|", 0, value=400)
    nAC = d2.number_input("|A∩C|", 0, value=150)
    nBC = d3.number_input("|B∩C|", 0, value=100)
    nABC = d4.number_input("|A∩B∩C|", 0, value=50)
    tot = nA + nB + nC - nAB - nAC - nBC + nABC
    st.write(f"|A∪B∪C| = {nA}+{nB}+{nC} − {nAB} − {nAC} − {nBC} + {nABC} = **{tot}**")
if tot > uni:
    st.error(f"Inkonsisten: gabungan ({tot}) > semesta ({uni}). Periksa integritas dataset.")
else:
    st.success(f"Konsisten. Di luar semua himpunan: {uni - tot}")

st.subheader("7. Padanan operasi SQL (SQLite)")
if len(cats) >= 2:
    sx = st.selectbox("Tabel X", cats, 0, key=f"sx_{src}")
    sy = st.selectbox("Tabel Y", cats, 1, key=f"sy_{src}")
    for k, (query, rows) in sql_equivalents(data, sx, sy).items():
        py = {"UNION": data[sx] | data[sy], "INTERSECT": data[sx] & data[sy],
              "EXCEPT": data[sx] - data[sy]}[k]
        st.code(query, language="sql")
        st.write(f"{sorted(rows)} — {'✅ sama dengan operasi set Python' if rows == py else '❌ beda'}")
