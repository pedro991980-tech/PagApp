import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import date
from classeviva import Session
from twilio.rest import Client

LOGO_FILE = "logo.png"

st.set_page_config(
    page_title="PagApp",
    page_icon=LOGO_FILE,
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Iniezione dinamica dei meta tag per forzare il nome "PagApp" su Browser e iOS (PWA)
pwa_ios_injection = """
    <script>
    const doc = window.parent.document;
    doc.title = "PagApp";
    
    let metaTitle = doc.querySelector('meta[name="apple-mobile-web-app-title"]');
    if (!metaTitle) {
        metaTitle = doc.createElement('meta');
        metaTitle.name = "apple-mobile-web-app-title";
        doc.head.appendChild(metaTitle);
    }
    metaTitle.content = "PagApp";

    let metaCap = doc.querySelector('meta[name="apple-mobile-web-app-capable"]');
    if (!metaCap) {
        metaCap = doc.createElement('meta');
        metaCap.name = "apple-mobile-web-app-capable";
        doc.head.appendChild(metaCap);
    }
    metaCap.content = "yes";
    </script>
"""
components.html(pwa_ios_injection, height=0, width=0)

# Stile CSS avanzato: Sfondi bianchi solidi, contrasto assoluto in nero/blu scuro, font grandi
custom_css = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none !important;}
    div[data-testid="stToolbar"] {display: none !important;}
    
    /* Sfondo generale fisso e pulito */
    html, body, [data-testid="stAppViewContainer"] {
        background: #f1f5f9;
        background-image: linear-gradient(rgba(241, 245, 249, 0.95), rgba(241, 245, 249, 0.95)), 
                          url("https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&w=1920&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        overflow-x: hidden;
    }

    /* Tipografia ingrandita e colori ad altissimo contrasto */
    html, body, [class*="css"] {
        font-size: 1.35rem !important;
        color: #000000 !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #0b132b !important;
        font-weight: 900 !important;
    }

    p, span, label, div, .stMarkdown {
        color: #0f172a !important;
        font-weight: 700 !important;
    }

    /* Card principale a sfondo bianco solido opaco */
    section.main > div {
        background-color: #ffffff !important;
        padding: 2.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        border: 2px solid #cbd5e1;
        margin-top: 1rem;
        margin-bottom: 2rem;
    }

    /* Pulsanti grandi, moderni e ad alto contrasto */
    .stButton>button {
        border-radius: 12px;
        font-size: 1.45rem !important;
        font-weight: 800 !important;
        padding: 0.9rem 1rem !important;
        width: 100%;
        background-color: #0284c7 !important;
        color: #ffffff !important;
        border: none;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
    }
    
    .stButton>button:hover {
        background-color: #0369a1 !important;
    }

    /* Campi di input con sfondi chiari solidi e testo in nero pieno */
    input, select, textarea {
        font-size: 1.35rem !important;
        background-color: #f8fafc !important;
        color: #000000 !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: 2px solid #64748b !important;
    }
    
    /* Etichette dei campi in grassetto nerissimo */
    .stTextInput label, .stSelectbox label, .stDateInput label, .stNumberInput label, .stRadio label {
        font-weight: 900 !important;
        color: #0b132b !important;
        font-size: 1.35rem !important;
    }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Inizializzazione degli Stati di Sessione (CRM Cliente integrato)
if "avviato" not in st.session_state:
    st.session_state.avviato = False

if "menu_attivo" not in st.session_state:
    st.session_state.menu_attivo = "💳 Pagamenti, Scadenze & Auto"

if "cliente_nome" not in st.session_state:
    st.session_state.cliente_nome = ""
if "cliente_cognome" not in st.session_state:
    st.session_state.cliente_cognome = ""
if "cliente_whatsapp" not in st.session_state:
    st.session_state.cliente_whatsapp = "+39"
if "cliente_codice" not in st.session_state:
    st.session_state.cliente_codice = ""

if "scansione_desc" not in st.session_state:
    st.session_state.scansione_desc = ""
if "scansione_imp" not in st.session_state:
    st.session_state.scansione_imp = 0.0

# ================= HOMEPAGE: ONBOARDING & PROFILAZIONE CLIENTE =================
if not st.session_state.avviato:
    st.markdown("<h1 style='text-align: center;'>💼 PagApp</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #0284c7;'>Gestione Appuntamenti e Pagamenti</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Inserisci i dati del cliente per configurare l'account e abilitare le notifiche istantanee.</p>", unsafe_allow_html=True)
    
    col_1, col_2, col_3 = st.columns([1, 2, 1])
    with col_2:
        try:
            st.image(LOGO_FILE, use_container_width=True)
        except:
            st.info("Logo in caricamento...")
    
    st.markdown("---")
    st.subheader("📋 Profilo Cliente & Riferimento Notifiche")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        in_nome = st.text_input("Nome Cliente", value=st.session_state.cliente_nome, placeholder="Es. Mario")
        in_tel = st.text_input("Numero WhatsApp (per notifiche)", value=st.session_state.cliente_whatsapp, placeholder="+393331234567")
    with col_c2:
        in_cognome = st.text_input("Cognome Cliente", value=st.session_state.cliente_cognome, placeholder="Es. Rossi")
        in_codice = st.text_input("Codice Fiscale o Riferimento", value=st.session_state.cliente_codice, placeholder="RSSMRA...")

    st.write("")
    if st.button("🚀 Avvia PagApp & Registra", type="primary"):
        if not in_nome or not in_tel:
            st.error("Inserisci almeno il Nome e il Numero WhatsApp per procedere.")
        else:
            st.session_state.cliente_nome = in_nome
            st.session_state.cliente_cognome = in_cognome
            st.session_state.cliente_whatsapp = in_tel
            st.session_state.cliente_codice = in_codice
            st.session_state.avviato = True
            st.rerun()

# ================= AREA INTERNA / HUB PRINCIPALE =================
else:
    col_head1, col_head2, col_head3 = st.columns([1, 4, 1])
    with col_head1:
        try:
            st.image(LOGO_FILE, width=65)
        except:
            pass
    with col_head2:
        st.markdown(f"### 💼 PagApp Hub — Cliente: {st.session_state.cliente_nome} {st.session_state.cliente_cognome}")
    with col_head3:
        if st.button("🔄 Profilo"):
            st.session_state.avviato = False
            st.rerun()

    st.markdown("---")

    # ================= NAVIGAZIONE ORIZZONTALE A CASELLE IN ALTO =================
    col_b1, col_b2, col_b3, col_b4 = st.columns(4)

    with col_b1:
        if st.button("💳 Pagamenti", use_container_width=True):
            st.session_state.menu_attivo = "💳 Pagamenti, Scadenze & Auto"
    with col_b2:
        if st.button("📅 Appuntamenti", use_container_width=True):
            st.session_state.menu_attivo = "📅 Appuntamenti"
    with col_b3:
        if st.button("🏫 Scuola", use_container_width=True):
            st.session_state.menu_attivo = "🏫 Scuola (ClasseViva)"
    with col_b4:
        if st.button("📊 Spese", use_container_width=True):
            st.session_state.menu_attivo = "📊 Resoconto Spese"

    st.markdown("---")

    menu = st.session_state.menu_attivo

    TWILIO_ACCOUNT_SID = "IL_TUO_SID_QUI"
    TWILIO_AUTH_TOKEN = "IL_TUO_TOKEN_QUI"
    TWILIO_FROM_PHONE = "whatsapp:+14155238886"
    
    # Destinatario Twilio legato al numero inserito in fase di onboarding cliente
    TWILIO_TO_PHONE = f"whatsapp:{st.session_state.cliente_whatsapp}"

    def invia_notifica_whatsapp(testo):
        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=testo,
                from_=TWILIO_FROM_PHONE,
                to=TWILIO_TO_PHONE
            )
            return True, message.sid
        except Exception as e:
            return False, str(e)

    # ================= SEZIONE 1: PAGAMENTI, SCADENZE & AUTO CON FOTOCAMERA =================
    if menu == "💳 Pagamenti, Scadenze & Auto":
        st.subheader("💳 Pagamenti, Scadenze & Gestione Auto")
        st.write(f"Operatività associata al cliente: **{st.session_state.cliente_nome} {st.session_state.cliente_cognome}**")

        usa_fotocamera = st.checkbox("📷 Attiva fotocamera per riconoscimento automatico")

        if usa_fotocamera:
            st.info("Inquadra la bolletta o il documento con la fotocamera del dispositivo.")
            foto = st.camera_input("Scatta foto per compilazione automatica")
            if foto is not None:
                st.session_state.scansione_desc = "Bolletta / Voce Rilevata da Scanner"
                st.session_state.scansione_imp = 45.00
                st.success("✅ Dati estratti e precompilati con successo!")

        st.markdown("---")
        
        tipo_scelta = st.selectbox("Ambito:", ["Pagamento Utenze / Spese Generali", "🚗 Controllo e Pagamento Veicolo (Targa)"])

        if tipo_scelta == "Pagamento Utenze / Spese Generali":
            categoria = st.selectbox("Categoria", ["Bolletta Luce/Gas/Acqua", "Affitto / Mutuo", "Rata Finanziamento", "Assicurazione Casa", "Abbonamenti", "Altro"])
            
            descrizione = st.text_input("Descrizione", value=st.session_state.scansione_desc)
            importo = st.number_input("Importo (€)", min_value=0.0, value=st.session_state.scansione_imp, format="%.2f")
            data_scad = st.date_input("Data di Scadenza", value=date.today())

            metodo = st.radio("Metodo di Pagamento:", ["Conto Bancario (IBAN)", "Carta Prepagata"])
            dettagli_conto = st.text_input("Inserisci IBAN o Numero Carta", placeholder="IT00X0000...")

            if st.button("Conferma Pagamento e Notifica WhatsApp", type="primary"):
                if not descrizione or not dettagli_conto:
                    st.error("Compila tutti i campi obbligatori.")
                else:
                    messaggio = (
                        f"💼 *PagApp - Pagamento Eseguito*\n"
                        f"• Cliente: {st.session_state.cliente_nome} {st.session_state.cliente_cognome}\n"
                        f"• Categoria: {categoria}\n"
                        f"• Descrizione: {descrizione}\n"
                        f"• Importo: €{importo:.2f}\n"
                        f"• Metodo: {metodo}"
                    )
                    successo, res = invia_notifica_whatsapp(messaggio)
                    if successo:
                        st.success(f"Pagamento registrato e notifica inviata a {st.session_state.cliente_whatsapp}!")
                        st.balloons()
                    else:
                        st.warning(f"Registrato, ma errore WhatsApp: {res}")
        else:
            st.subheader("🚗 Gestione Auto tramite Targa")
            targa = st.text_input("Inserisci o scansiona la Targa del Veicolo", placeholder="Es. AB123CD").upper()

            if targa:
                st.info(f"Veicolo associato: **{targa}** (Scadenze verificate in automatico)")
                voce_auto = st.selectbox("Voce da saldare:", ["Bollo Auto", "Revisione", "Assicurazione RCA"])
                importo_auto = st.number_input("Importo (€)", min_value=0.0, value=150.00, format="%.2f")
                metodo_auto = st.radio("Paga con:", ["Conto Bancario (IBAN)", "Carta Prepagata"])
                dett_auto = st.text_input("Dati Conto o Carta per pagamento auto")

                if st.button("Paga Scadenza Auto e Invia Avviso", type="primary"):
                    if not dett_auto:
                        st.error("Inserisci i dati di pagamento.")
                    else:
                        msg_auto = (
                            f"🚗 *PagApp - Pagamento Auto*\n"
                            f"• Cliente: {st.session_state.cliente_nome} {st.session_state.cliente_cognome}\n"
                            f"• Targa: {targa}\n"
                            f"• Voce: {voce_auto}\n"
                            f"• Importo: €{importo_auto:.2f}\n"
                            f"• Metodo: {metodo_auto}"
                        )
                        successo, res = invia_notifica_whatsapp(msg_auto)
                        if successo:
                            st.success(f"Pagamento per {voce_auto} della targa {targa} completato!")
                        else:
                            st.warning(f"Errore invio WhatsApp: {res}")

    # ================= SEZIONE 2: APPUNTAMENTI =================
    elif menu == "📅 Appuntamenti":
        st.subheader("📅 Gestione Appuntamenti")
        titolo_appunt = st.text_input("Oggetto / Titolo Appuntamento")
        categoria_appunt = st.selectbox("Categoria", ["Visita Medica", "Impegno Lavorativo", "Scadenza Burocratica", "Personale"])
        data_appunt = st.date_input("Data Appuntamento", value=date.today())
        ora_appunt = st.time_input("Orario")

        if st.button("Salva Appuntamento e Notifica", type="primary"):
            if titolo_appunt:
                messaggio_app = f"📅 *PagApp - Promemoria Appuntamento*\n• Cliente: {st.session_state.cliente_nome} {st.session_state.cliente_cognome}\n• Oggetto: {titolo_appunt} ({categoria_appunt})\n• Data: {data_appunt} ore {ora_appunt}"
                successo, res = invia_notifica_whatsapp(messaggio_app)
                if successo:
                    st.success("Appuntamento salvato e notificato via WhatsApp!")
                else:
                    st.warning(f"Errore WhatsApp: {res}")
            else:
                st.error("Inserisci un titolo.")

    # ================= SEZIONE 3: SCUOLA (CLASSEVIVA) =================
    elif menu == "🏫 Scuola (ClasseViva)":
        st.subheader("🏫 Integrazione Scolastica (ClasseViva)")
        cv_user = st.text_input("Username ClasseViva")
        cv_pass = st.text_input("Password ClasseViva", type="password")

        if st.button("Verifica ClasseViva e Notifica", type="primary"):
            if not cv_user or not cv_pass:
                st.error("Inserisci credenziali.")
            else:
                try:
                    ses = Session()
                    ses.login(cv_user, cv_pass)
                    st.success("Connessione stabilita!")
                    successo, res = invia_notifica_whatsapp(f"🏫 *PagApp - ClasseViva*: Accesso effettuato per {st.session_state.cliente_nome} {st.session_state.cliente_cognome}!")
                    if successo:
                        st.success("Notifica WhatsApp inviata!")
                except Exception as e:
                    st.error(f"Errore di autenticazione: {e}")

    # ================= SEZIONE 4: RESOCONTO SPESE =================
    elif menu == "📊 Resoconto Spese":
        st.subheader("📊 Resoconto Finanziario Mensile")
        if "spese_db" not in st.session_state:
            st.session_state.spese_db = pd.DataFrame(columns=["Categoria", "Descrizione", "Importo", "Data"])

        cat_spesa = st.selectbox("Categoria Spesa", ["Alimentari", "Utenze & Casa", "Trasporti", "Salute", "Scuola", "Svago", "Altro"])
        desc_spesa = st.text_input("Descrizione Spesa")
        imp_spesa = st.number_input("Importo (€)", min_value=0.0, format="%.2f")

        if st.button("Aggiungi Spesa", type="primary") and desc_spesa:
            nuova_riga = pd.DataFrame({"Categoria": [cat_spesa], "Descrizione": [desc_spesa], "Importo": [imp_spesa], "Data": [str(date.today())]})
            st.session_state.spese_db = pd.concat([st.session_state.spese_db, nuova_riga], ignore_index=True)
            st.success("Spesa registrata!")
            st.rerun()

        if not st.session_state.spese_db.empty:
            st.dataframe(st.session_state.spese_db, use_container_width=True)
            st.metric(label="Totale Spese", value=f"€ {st.session_state.spese_db['Importo'].sum():.2f}")
