import streamlit as st
import requests
import pandas as pd
from base64 import b64encode
from datetime import datetime, date
import time

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="WICS Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styling ───────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .block-container { padding: 2rem 2.5rem 2rem 2.5rem; }

  /* KPI cards */
  .kpi-card {
    background: #ffffff;
    border: 1px solid #e8ecf0;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    text-align: center;
  }
  .kpi-value {
    font-size: 2.4rem;
    font-weight: 700;
    color: #0f172a;
    line-height: 1;
    margin-bottom: 0.3rem;
  }
  .kpi-label {
    font-size: 0.78rem;
    font-weight: 500;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }
  .kpi-delta-pos { color: #16a34a; font-size: 0.82rem; }
  .kpi-delta-neg { color: #dc2626; font-size: 0.82rem; }

  /* Status pills */
  .pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
  }
  .pill-green  { background:#dcfce7; color:#15803d; }
  .pill-blue   { background:#dbeafe; color:#1d4ed8; }
  .pill-orange { background:#ffedd5; color:#c2410c; }
  .pill-gray   { background:#f1f5f9; color:#475569; }

  /* Section headers */
  .section-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #0f172a;
    margin: 1.5rem 0 0.8rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e2e8f0;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: #0f172a;
  }
  [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stMultiSelect label { color: #94a3b8 !important; }

  /* Hide streamlit branding */
  #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Opdrachtgevers config ─────────────────────────────────────
OPDRACHTGEVERS = [
    {
        "naam": "All Set Professional",
        "key": "VYTFbhwXkqNhaXGCVGzU",
        "secret": "jNWZfJBznJWxlMabCULG",
        "url": "https://servicelayer.wics.nl",
    },
    {
        "naam": "Amaya Amsterdam",
        "key": "fofyzcGmBLpEYlAauJEh",
        "secret": "xGewtRknyUqJLzRHLmpC",
        "url": "https://servicelayer.wics.nl",
    },
]

STATUS_LABELS = {
    "00": ("Aangemaakt",    "pill-gray"),
    "10": ("Ingevoerd",     "pill-gray"),
    "20": ("Vrijgegeven",   "pill-blue"),
    "30": ("Bevestigd",     "pill-blue"),
    "40": ("In uitvoering", "pill-orange"),
    "50": ("Gepickt",       "pill-orange"),
    "60": ("Afgehandeld",   "pill-green"),
    "70": ("Verzonden",     "pill-green"),
    "90": ("Geannuleerd",   "pill-gray"),
}

PRIORITY_MAP = {1: "🔴 Hoog", 2: "🟡 Normaal", 3: "🟢 Laag"}

# ── API helpers ───────────────────────────────────────────────
def auth_header(key: str, secret: str) -> dict:
    token = b64encode(f"{key}:{secret}".encode()).decode()
    return {"Authorization": f"Basic {token}", "Content-Type": "application/json"}


def fetch_orders(naam: str, key: str, secret: str, base_url: str) -> list[dict]:
    headers = auth_header(key, secret)
    all_orders, page = [], 1
    while True:
        try:
            r = requests.get(
                f"{base_url}/api/order",
                headers=headers,
                params={"page": page, "pageSize": 100},
                timeout=15,
            )
            if r.status_code != 200:
                break
            data = r.json().get("data", [])
            if not data:
                break
            for o in data:
                o["_opdrachtgever"] = naam
            all_orders.extend(data)
            page += 1
            time.sleep(0.1)   # respecteer rate limit
        except Exception:
            break
    return all_orders


@st.cache_data(ttl=3600, show_spinner=False)
def load_all_orders(selected_names: tuple) -> pd.DataFrame:
    rows = []
    for o in OPDRACHTGEVERS:
        if o["naam"] in selected_names:
            rows.extend(fetch_orders(o["naam"], o["key"], o["secret"], o["url"]))
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    # Normaliseer kolommen
    rename = {
        "number":              "Ordernummer",
        "reference":           "Referentie",
        "additionalReference": "Extra Referentie",
        "deliveryDate":        "Leverdatum",
        "statusCode":          "StatusCode",
        "method":              "Methode",
        "webshopId":           "Webshop ID",
        "paid":                "Betaald",
        "priority":            "Prioriteit",
        "rideNumber":          "Rit",
        "termsOfDelivery":     "Leveringsconditie",
        "_opdrachtgever":      "Opdrachtgever",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    if "Leverdatum" in df.columns:
        df["Leverdatum"] = pd.to_datetime(df["Leverdatum"], errors="coerce").dt.date

    if "StatusCode" in df.columns:
        df["Status"] = df["StatusCode"].map(lambda c: STATUS_LABELS.get(str(c), (str(c), "pill-gray"))[0])
    else:
        df["Status"] = "Onbekend"

    if "Prioriteit" in df.columns:
        df["Prioriteit"] = df["Prioriteit"].map(lambda p: PRIORITY_MAP.get(p, str(p)))

    if "Betaald" in df.columns:
        df["Betaald"] = df["Betaald"].map(lambda b: "✅ Ja" if b else "❌ Nee")

    return df


# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📦 WICS")
    st.markdown("---")

    alle_namen = [o["naam"] for o in OPDRACHTGEVERS]
    geselecteerd = st.multiselect(
        "Opdrachtgevers",
        options=alle_namen,
        default=alle_namen,
    )

    st.markdown("---")
    st.markdown("**Filter op status**")
    alle_statussen = [v[0] for v in STATUS_LABELS.values()]
    status_filter = st.multiselect("Status", alle_statussen, default=alle_statussen)

    st.markdown("**Filter op periode**")
    datum_van = st.date_input("Van", value=date(2024, 1, 1))
    datum_tot = st.date_input("Tot", value=date.today())

    st.markdown("---")
    if st.button("🔄 Data verversen", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown(f"<small style='color:#475569'>Laatste refresh:<br>{datetime.now().strftime('%d-%m-%Y %H:%M')}</small>", unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────
st.markdown("# 📦 WICS Order Dashboard")
st.markdown(f"Overzicht van orders voor **{', '.join(geselecteerd) if geselecteerd else '—'}**")

if not geselecteerd:
    st.warning("Selecteer minimaal één opdrachtgever in de zijbalk.")
    st.stop()

with st.spinner("Orders ophalen uit WICS..."):
    df = load_all_orders(tuple(sorted(geselecteerd)))

if df.empty:
    st.error("Geen data ontvangen. Controleer de API-verbinding of credentials.")
    st.stop()

# Datumfilter
if "Leverdatum" in df.columns:
    df = df[
        (df["Leverdatum"] >= datum_van) &
        (df["Leverdatum"] <= datum_tot)
    ]

# Statusfilter
if "Status" in df.columns and status_filter:
    df = df[df["Status"].isin(status_filter)]

# ── KPI row ───────────────────────────────────────────────────
totaal       = len(df)
afgehandeld  = len(df[df["Status"].isin(["Afgehandeld", "Verzonden"])]) if "Status" in df.columns else 0
in_uitvoer   = len(df[df["Status"] == "In uitvoering"]) if "Status" in df.columns else 0
openstaand   = len(df[df["Status"].isin(["Aangemaakt", "Ingevoerd", "Vrijgegeven", "Bevestigd"])]) if "Status" in df.columns else 0
pct_verwerkt = round(afgehandeld / totaal * 100) if totaal > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)
kpis = [
    (col1, str(totaal),          "Totaal orders",       ""),
    (col2, str(afgehandeld),     "Afgehandeld",         f"<span class='kpi-delta-pos'>↑ {pct_verwerkt}%</span>"),
    (col3, str(in_uitvoer),      "In uitvoering",       ""),
    (col4, str(openstaand),      "Openstaand",          ""),
    (col5, str(len(geselecteerd)), "Opdrachtgevers",    ""),
]
for col, val, label, delta in kpis:
    with col:
        st.markdown(f"""
        <div class='kpi-card'>
          <div class='kpi-value'>{val}</div>
          <div class='kpi-label'>{label}</div>
          {delta}
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts ────────────────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.markdown("<div class='section-title'>Orders per status</div>", unsafe_allow_html=True)
    if "Status" in df.columns:
        status_counts = df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Aantal"]
        st.bar_chart(status_counts.set_index("Status"), color="#3b82f6")

with c2:
    st.markdown("<div class='section-title'>Orders per opdrachtgever</div>", unsafe_allow_html=True)
    if "Opdrachtgever" in df.columns:
        opdracht_counts = df["Opdrachtgever"].value_counts().reset_index()
        opdracht_counts.columns = ["Opdrachtgever", "Aantal"]
        st.bar_chart(opdracht_counts.set_index("Opdrachtgever"), color="#8b5cf6")

# Trend over tijd
if "Leverdatum" in df.columns:
    st.markdown("<div class='section-title'>Orders over tijd (leverdatum)</div>", unsafe_allow_html=True)
    trend = df.groupby("Leverdatum").size().reset_index(name="Aantal")
    trend = trend.sort_values("Leverdatum")
    st.line_chart(trend.set_index("Leverdatum"), color="#10b981")

# ── Tabel ─────────────────────────────────────────────────────
st.markdown("<div class='section-title'>Orderoverzicht</div>", unsafe_allow_html=True)

toon_kolommen = [k for k in [
    "Opdrachtgever", "Ordernummer", "Referentie",
    "Status", "Leverdatum", "Prioriteit", "Betaald", "Methode"
] if k in df.columns]

zoek = st.text_input("🔍 Zoek op ordernummer of referentie", placeholder="bijv. SO510001")
df_tabel = df[toon_kolommen].copy()
if zoek:
    mask = df_tabel.apply(lambda col: col.astype(str).str.contains(zoek, case=False, na=False)).any(axis=1)
    df_tabel = df_tabel[mask]

st.dataframe(
    df_tabel.sort_values("Leverdatum", ascending=False) if "Leverdatum" in df_tabel.columns else df_tabel,
    use_container_width=True,
    height=450,
    hide_index=True,
)

st.caption(f"{len(df_tabel)} orders weergegeven")
