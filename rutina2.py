# Aplicación interactiva optimizada para iPhone (Streamlit Mobile Friendly)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time
import hashlib

st.set_page_config(page_title="Entrenamiento Personal", layout="centered")
st.markdown("""
<style>
    /* Estilo general más compacto para móviles */
    html, body, [class*="css"]  {
        font-size: 16px;
    }
    .block-container {
        padding: 1rem;
    }
    .stButton>button {
        width: 100%;
        height: 3em;
        font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏋️ Mi Rutina (iPhone Edition)")

# Archivos
USUARIOS_FILE = "usuarios.csv"
DATA_FILE = "progreso_rutina.csv"
RUTINA_FILE = "rutinas_personalizadas.csv"

# Inicializar usuarios
try:
    usuarios_df = pd.read_csv(USUARIOS_FILE)
except FileNotFoundError:
    usuarios_df = pd.DataFrame(columns=["usuario", "password"])
    usuarios_df.to_csv(USUARIOS_FILE, index=False)

# Login básico
st.header("🔐 Inicia sesión")
login_usuario = st.text_input("Usuario")
login_pass = st.text_input("Contraseña", type="password")
login_btn = st.button("Entrar")

hash_pass = lambda x: hashlib.sha256(x.encode()).hexdigest()

if login_btn:
    login_hash = hash_pass(login_pass)
    if ((usuarios_df["usuario"] == login_usuario) & (usuarios_df["password"] == login_hash)).any():
        st.session_state["usuario"] = login_usuario
        st.success(f"Bienvenido, {login_usuario}")
    else:
        st.error("Usuario o contraseña incorrecta")

with st.expander("🆕 Crear usuario"):
    new_user = st.text_input("Nuevo usuario")
    new_pass = st.text_input("Nueva contraseña", type="password")
    if st.button("Registrar"):
        if new_user in usuarios_df["usuario"].values:
            st.warning("Ese usuario ya existe.")
        else:
            usuarios_df = pd.concat([
                usuarios_df,
                pd.DataFrame([[new_user, hash_pass(new_pass)]], columns=usuarios_df.columns)
            ], ignore_index=True)
            usuarios_df.to_csv(USUARIOS_FILE, index=False)
            st.success("Usuario registrado")

if "usuario" in st.session_state:
    usuario = st.session_state["usuario"]

    try:
        df = pd.read_csv(DATA_FILE)
    except:
        df = pd.DataFrame(columns=["Usuario", "Fecha", "Día", "Ejercicio", "Serie", "Reps", "Peso (lb)", "RPE", "Notas"])

    try:
        rutinas_df = pd.read_csv(RUTINA_FILE)
    except:
        rutinas_df = pd.DataFrame(columns=["Usuario", "Día", "Ejercicio"])

    if rutinas_df[rutinas_df["Usuario"] == usuario].empty:
        base = {
            "Día 1": ["Barbell Bench Press", "Incline Barbell Bench Press", "Chest Fly (Machine)", "Machine Shoulder Press", "Dumbbell Lateral Raise", "Triceps Pushdown", "Cable Overhead Triceps Extension"],
            "Día 2": ["Barbell Squat", "Hip Thrust (Barbell)", "Leg Press", "Leg Extension", "Bulgarian Split Squat", "Seated Calf Raise"],
            "Día 3": ["Deadlift (Barbell)", "Lat Pulldown (Wide Grip)", "Seated Row (Cable)", "Straight Arm Pulldown", "Incline Dumbbell Curl", "Cable Curl", "Hammer Curl"],
            "Día 4": ["Goblet Squat to Press", "Romanian Deadlift (Dumbbells)", "Seated Row (Cable)", "Lat Pulldown (Medium Grip)", "Dumbbell Shrug", "Face Pull", "Crunch Machine", "Cable Woodchopper"],
            "Día 5": ["Step-up (Dumbbell)", "Lying Leg Curl (Machine)", "Hip Thrust (Barbell)", "Seated Leg Curl (Machine)", "Reverse Lunge (Dumbbell)", "Seated Calf Raise", "Crunch Machine", "Cable Woodchopper"]
        }
        for dia, ejercicios in base.items():
            for ejercicio in ejercicios:
                rutinas_df = pd.concat([
                    rutinas_df,
                    pd.DataFrame([[usuario, dia, ejercicio]], columns=rutinas_df.columns)
                ], ignore_index=True)
        rutinas_df.to_csv(RUTINA_FILE, index=False)

    st.header("📅 Tu rutina")
    fecha = st.date_input("Fecha", value=datetime.date.today())
    dia = st.selectbox("Elige el día", sorted(rutinas_df[rutinas_df["Usuario"] == usuario]["Día"].unique()))
    descanso = st.slider("⏱️ Descanso entre series (segundos)", 15, 180, 60)

    ejercicios = rutinas_df[(rutinas_df["Usuario"] == usuario) & (rutinas_df["Día"] == dia)]["Ejercicio"].tolist()

    for ejercicio in ejercicios:
        with st.expander(f"🏋️ {ejercicio}"):
            num_series = st.number_input(f"Series", min_value=1, max_value=6, step=1, key=f"s_{ejercicio}")
            for s in range(1, num_series+1):
                st.markdown(f"**Serie {s}**")
                rep = st.number_input("Reps", min_value=1, step=1, key=f"r_{ejercicio}_{s}")
                peso = st.number_input("Peso (lb)", min_value=0.0, step=0.5, key=f"p_{ejercicio}_{s}")
                rpe = st.slider("RPE", 1, 10, 7, key=f"rpe_{ejercicio}_{s}")
                nota = st.text_input("Notas", key=f"n_{ejercicio}_{s}")
                if st.button(f"💾 Guardar serie {s}", key=f"g_{ejercicio}_{s}"):
                    fila = pd.DataFrame([[usuario, fecha, dia, ejercicio, s, rep, peso, rpe, nota]], columns=df.columns)
                    df = pd.concat([df, fila], ignore_index=True)
                    df.to_csv(DATA_FILE, index=False)
                    st.success("✅ Guardado")
                if st.button(f"⏱️ Descansar {s}", key=f"d_{ejercicio}_{s}"):
                    with st.empty():
                        for t in range(descanso, 0, -1):
                            st.info(f"⌛ {t}s restantes... 💤")
                            time.sleep(1)
                        st.success("¡Siguiente serie! 💪🔥")

    st.markdown("---")
    st.caption("Hecho para iPhone. Ejecuta con: streamlit run rutina.py")

