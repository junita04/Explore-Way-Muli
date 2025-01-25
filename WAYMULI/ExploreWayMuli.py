import streamlit as st
from streamlit_option_menu import option_menu
import requests
from PIL import Image, ImageOps
from io import BytesIO
import os
import base64  # Untuk encoding gambar ke base64
import streamlit.components.v1 as components

# Direktori untuk menyimpan file yang diunggah
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Menyimpan data admin terdaftar
admins = {"explorewaymuli@gmail.com": "WayMuli123"}  # Admin yang terdaftar (username: password)

# Fungsi untuk memuat gambar
@st.cache_data
def load_image(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img = ImageOps.exif_transpose(img)
    return img

# Fungsi untuk menampilkan gambar dan informasi
def display_images_with_data(data_list):
    cols = st.columns(3)
    for i, data in enumerate(data_list):
        with cols[i % 3]:
            st.markdown(f"[Buka Lokasi di Google Maps]({data['gmaps_link']})")
            st.image(data["image"], use_column_width=True, caption=data["Nama"])
            with st.expander(f"Detail {data['Nama']}"):
                st.write(f"**Deskripsi:** {data['Deskripsi']}")
                st.write(f"**Harga/Tiket:** {data['Harga']}")
                st.write(f"**Kontak:** {data['Kontak']}")

# Fungsi untuk mengunggah file dan menampilkan pratinjau
def upload_new_content():
    st.markdown("## Tambahkan Informasi Baru")

    # Pilihan kategori: UMKM atau Wisata
    kategori = st.radio("Pilih Kategori", ("UMKM", "Tempat Wisata"), key="kategori_radio")

    # Unggah file gambar
    uploaded_file = st.file_uploader("Unggah Foto Baru", type=["jpg", "jpeg", "png"], key="file_uploader")
    image = None
    if uploaded_file is not None:
        # Simpan file ke direktori lokal
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        # Menampilkan pratinjau gambar
        image = file_path
        img = Image.open(file_path)
        st.image(img, caption="Pratinjau Gambar", use_column_width=True)

    # Input detail informasi
    nama = st.text_input("Nama Tempat/Produk")
    deskripsi = st.text_area("Deskripsi")
    harga = st.text_input("Harga/Tiket")
    kontak = st.text_input("Kontak")
    gmaps_link = st.text_input("Link Google Maps")

    # Tambahkan data baru
    if st.button("Tambahkan"):
        if not gmaps_link:
            st.error("Harap masukkan link Google Maps terlebih dahulu.")
            return

        data = {
            "Nama": nama,
            "Deskripsi": deskripsi,
            "Harga": harga,
            "Kontak": kontak,
            "gmaps_link": gmaps_link,
            "image": image,
        }

        if kategori == "UMKM":
            st.session_state["umkm_data"].append(data)
            st.success(f"Data UMKM '{nama}' berhasil ditambahkan!")
        elif kategori == "Tempat Wisata":
            st.session_state["wisata_data"].append(data)
            st.success(f"Data Tempat Wisata '{nama}' berhasil ditambahkan!")

        # Memicu refresh halaman
        st.session_state["rerun"] = True

# Fungsi untuk menghapus data
def delete_content():
    st.markdown("## Hapus Data")
    kategori = st.radio("Pilih Kategori", ("UMKM", "Tempat Wisata"), key="kategori_hapus")
    
    if kategori == "UMKM":
        data_list = st.session_state["umkm_data"]
    else:
        data_list = st.session_state["wisata_data"]
    
    if not data_list:
        st.warning("Tidak ada data yang tersedia untuk dihapus.")
        return
    
    item_to_delete = st.selectbox("Pilih item yang ingin dihapus", [item["Nama"] for item in data_list])
    
    if st.button("Hapus"):
        for item in data_list:
            if item["Nama"] == item_to_delete:
                data_list.remove(item)
                st.success(f"Data '{item_to_delete}' telah dihapus.")
                st.session_state["rerun"] = True
                break

# Fungsi untuk menampilkan video YouTube dalam pop-up kecil di bawah kanan dan looping
def show_video_popup():
    video_url = "https://www.youtube.com/embed/8H64R9-DQSI?autoplay=1&loop=1&playlist=8H64R9-DQSI"  # URL embed video YouTube dengan autoplay dan loop
    video_html = f"""
    <div id="video-popup" style="display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 640px; height: 360px; background: rgba(0, 0, 0, 0.8); z-index: 9999; border-radius: 10px;">
    <iframe width="100%" height="100%" src="{video_url}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
    <button onclick="closeVideoPopup()" style="position: absolute; top: 5px; right: 5px; background-color: #ff4d4d; color: white; border: none; padding: 5px 10px; font-size: 12px; cursor: pointer; border-radius: 5px;">X</button>
</div>


    <script>
    function closeVideoPopup() {{
        document.getElementById("video-popup").style.display = "none";
    }}

    window.onload = function() {{
        document.getElementById("video-popup").style.display = "block";
    }};
    </script>
    """
    components.html(video_html, height=250)


# Fungsi login admin
def admin_login():
    st.markdown("## Login Admin")
    
    # Input username dan password
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Validasi login
    if st.button("Login"):
        if username in admins and admins[username] == password:
            st.session_state.is_admin = True
            st.success("Login berhasil!")
            st.session_state["rerun"] = True
        else:
            st.error("Username atau password salah!")

# Fungsi untuk menambahkan latar belakang gambar
def set_background(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url({image_url});
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# Inisialisasi data
if "umkm_data" not in st.session_state:
    st.session_state["umkm_data"] = []

if "wisata_data" not in st.session_state:
    st.session_state["wisata_data"] = []

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

#  URL gambar latar belakang
background_image_url = "https://res.cloudinary.com/dbpjz2gn6/image/upload/v1737723899/Tambahkan_sedikit_teks_isi_wbcxiu.png "

# Set latar belakang gambar
set_background(background_image_url)


# Header Halaman
st.markdown(
    """
    <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; background-color: #C3316C; padding: 10px; border-radius: 10px; text-align: center;">
    <h1 style="font-family: 'Poppins', sans-serif; font-size: 2.5em; color: #f0f0f0; font-weight: bold;">EXPLORE DESA WAY MULI</h1>
    <p style="font-family: 'Times New Roman', sans-serif; font-size: 1.2em; color: #f0f0f0;">Jelajahi Keindahan Desa Way Muli dan Dukung Produk Lokal dengan Sepenuh Hati</p>
    <p style="font-family: 'Times New Roman', sans-serif; font-size: 0.9em; color: #f0f0f0;">Temukan Harmoni Alam, Budaya, dan Kuliner yang Menggugah di Destinasi Tersembunyi Ini</p>
        </div>
        <div>
    </div>
    """,
    unsafe_allow_html=True,
)


# Menu Navigasi
def streamlit_menu():
    selected = option_menu(
        menu_title=None,
        options=["Home", "UMKM", "Tempat Wisata", "Contact Us", "Tambah Konten", "Hapus Konten"],
        icons=["house-door", "shop", "map", "envelope", "plus-circle", "trash"],
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#144259"},
            "icon": {"color": "#BD55A8", "font-size": "20px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "center",
                "margin": "0px",
                "color": "#fff",
                "--hover-color": "#00427F",
                "border-radius": "5px",
            },
            "nav-link-selected": {"background-color": "#00427F"},
        },
    )
    return selected

menu = streamlit_menu()

# Teks berjalan di bawah menu
st.markdown(
    """
    <marquee style="font-size: 1.2em; color: #FFFFFF; background-color: #144259; padding: 10px; border-radius: 5px;">
        Selamat datang di Explore Desa Way Muli! Temukan keindahan alam, budaya, dan kuliner autentik di Desa Way Muli. 
        Mari dukung UMKM lokal untuk kemajuan ekonomi bersama!
    </marquee>
    """,
    unsafe_allow_html=True,
)

# Menampilkan halaman sesuai menu
if menu == "Home":
    st.markdown("<h1 style='text-align: center; color: #144259;'>Tentang Kami</h1>", unsafe_allow_html=True)
    st.markdown(
        """
            <img src="https://res.cloudinary.com/dbpjz2gn6/image/upload/v1737713695/IMG-20250124-WA0000_hinslo.jpg" alt="Beberapa UMKM dan Tempat Wisata Desa Way Muli" style="height: 400px; border-radius: 10px; display: block; margin: 10px auto;">
             <p style="text-align: center; font-family: 'Times New Roman', sans-serif; font-size: 1.2em; color: #144259; font-weight: bold;">Beberapa UMKM dan Tempat Wisata Desa Way Muli</p>
        <div style="text-align: justify; font-size: 1.2em; line-height: 1.8;">
        Desa Way Muli, yang terletak di Kecamatan Rajabasa, Lampung Selatan, adalah destinasi yang kaya akan keindahan alam dan potensi ekonomi lokal. 
        Dikelilingi oleh panorama pantai yang memukau dan perbukitan hijau, desa ini menawarkan berbagai tempat wisata menarik, seperti pantai eksotis dan spot snorkeling yang memanjakan mata. 
        Selain itu, Way Muli juga dikenal dengan UMKM kreatif yang menghadirkan produk-produk khas, mulai dari olahan hasil laut hingga kerajinan tangan bernilai tinggi. 
        Dengan kombinasi pesona alam dan inovasi warganya, Desa Way Muli menjadi pilihan sempurna bagi wisatawan yang ingin menikmati keindahan alam sekaligus mendukung perekonomian lokal.
        </div>
        <div style='text-align: center;'>
        """,
        unsafe_allow_html=True,
    )

elif menu == "UMKM":
    st.markdown("<h1 style='text-align: center; color: #144259;'>Produk Lokal UMKM</h1>", unsafe_allow_html=True)
    display_images_with_data(st.session_state["umkm_data"]) # Menggunakan data_list untuk gambar

elif menu == "Tempat Wisata":
    st.markdown("<h1 style='text-align: center; color: #144259;'>Tempat Wisata</h1>", unsafe_allow_html=True)
    display_images_with_data(st.session_state["wisata_data"])

elif menu == "Tambah Konten":
    if st.session_state.is_admin:
        upload_new_content()
    else:
        admin_login()

elif menu == "Hapus Konten":
    if st.session_state.is_admin:
        delete_content()
    else:
        admin_login()

        
elif menu == "Contact Us":
    st.markdown("<h1 style='text-align: center; color: #144259;'>Hubungi Kami</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <p style="font-family: 'Times New Roman', sans-serif;font-size: 1.2em; line-height: 1.8;">
        Untuk informasi lebih lanjut atau pertanyaan, silakan hubungi kami melalui:
        </p>
        <ul>
            <li><b>Email:</b> info@waymuli.opendesa.id</li>
            <li><b>Alamat:</b> Jl. Pesisir Desa Way Muli Kecamatan Rajabasa, Desa Way Muli, Kec. Raja Basa Kab. LAMPUNG SELATAN</li>
        </ul>
        <p style="font-family: 'Times New Roman', sans-serif; font-size: 1.2em; margin-top: 20px;">
        Kunjungi website resmi kami untuk informasi lebih lengkap:
        <a href="https://www.waymuli.rajabasa.id" target="_blank" style="color: #0A66C2; font-weight: bold;">
        www.waymuli.rajabasa.id</a>
        </p>
        """,
        unsafe_allow_html=True,
    )

# Panggil fungsi untuk menampilkan video pop-up saat halaman dimuat
show_video_popup()