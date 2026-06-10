import streamlit as st
import requests
import pandas as pd
from base64 import b64encode
from datetime import datetime, date
import time
import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

st.set_page_config(
    page_title="WICS Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  .block-container { padding: 2rem 2.5rem 2rem 2.5rem; }
  .kpi-card {
    background: #ffffff;
    border: 1px solid #e8ecf0;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    text-align: center;
  }
  .kpi-value { font-size: 2.4rem; font-weight: 700; color: #0f172a; line-height: 1; margin-bottom: 0.3rem; }
  .kpi-label { font-size: 0.78rem; font-weight: 500; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; }
  .kpi-delta-pos { color: #16a34a; font-size: 0.82rem; }
  .pill { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
  .pill-green  { background:#dcfce7; color:#15803d; }
  .pill-blue   { background:#dbeafe; color:#1d4ed8; }
  .pill-orange { background:#ffedd5; color:#c2410c; }
  .pill-gray   { background:#f1f5f9; color:#475569; }
  .section-title { font-size: 1.05rem; font-weight: 600; color: #0f172a; margin: 1.5rem 0 0.8rem 0; padding-bottom: 0.5rem; border-bottom: 2px solid #e2e8f0; }
  [data-testid="stSidebar"] { background: #0f172a; }
  [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
  #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Opdrachtgevers ────────────────────────────────────────────
OPDRACHTGEVERS = [
    {"naam": "MyBrakka", "ref": "10002", "key": "NFKagRJKVYaJhaaEhLrG", "secret": "FyzdufStPFBQsWFGwCEb"},
    {"naam": "Nimya", "ref": "10026", "key": "nJrhPBVRnbKvcKRDTxpw", "secret": "PsAWpdqbkNdRVLxSMINh"},
    {"naam": "NL Diffusion BV", "ref": "2005", "key": "mzbROhOTyJaRNknbshBb", "secret": "XCXAWvqznHEagOklJhiK"},
    {"naam": "Noa Sports", "ref": "10040", "key": "VySKpJXFJZyrLTivSwol", "secret": "oeZpZDUBEndDLlFwFmQM"},
    {"naam": "Organimal", "ref": "10008", "key": "YdVgIVVvuXqcIzBsmxWD", "secret": "RBXSxApBDyGiNvTZasAE"},
    {"naam": "PavoCouture", "ref": "10039", "key": "FPcIishwiJuQjMdEmBon", "secret": "WvjQCKLAmNuEFDJPLgMz"},
    {"naam": "PouchDirect", "ref": "10036", "key": "FBewJuvRNbXzSdEQSUUw", "secret": "kuWRQWYSQdsJKYvhzEfu"},
    {"naam": "Rehall", "ref": "2009", "key": "wPfPzCOFVaGYwtzsNSey", "secret": "ekaMaIifzbsvsKjNzehx"},
    {"naam": "Sacred Shop", "ref": "10035", "key": "iCcUmIeigrKGuaXiJFpr", "secret": "KRusJttjxTWQYDytyCkM"},
    {"naam": "Seen In Ibiza", "ref": "10038", "key": "mDaoSTgZAOfjrsZajoqi", "secret": "tehPgAIeLYXGIvdCkmqv"},
    {"naam": "Stappie", "ref": "10031", "key": "jvWfRrMjLnsREDSzisSp", "secret": "ygqfgMSzEsVYXSMARLRt"},
    {"naam": "Studio Amaya", "ref": "20015", "key": "JDgQsKLACVvGvQhGeeZa", "secret": "GhqPEtDHblOCDjwRmwHR"},
    {"naam": "Tameson", "ref": "10009", "key": "KScFIJSRnlWCLgTfrGcf", "secret": "eEFddcmBuDOWaKYteMPT"},
    {"naam": "The Launch", "ref": "10004", "key": "VkthfxeivuAzlawmqJnd", "secret": "QqezmMnYUEqOlxHCBHpf"},
    {"naam": "The View Yoga", "ref": "10000", "key": "nNaZCkezkjQLCMTNxzPk", "secret": "QFHvxhRGeFxfXwpEbVQB"},
    {"naam": "Volumehair", "ref": "10013", "key": "JeALRxQdvCECkeurIhMj", "secret": "PHIjpVzFUrHHmmnbtPVh"},
    {"naam": "Wallien", "ref": "10041", "key": "bZhBKRIlhPNQmlCIPsTE", "secret": "ItetzfQqRLHDDxEfRbeu"},
    {"naam": "Wallien B2B", "ref": "100410", "key": "vVFIeqHCfVQpLbfkJToG", "secret": "wycuDHREaottiJpRfIPj"},
    {"naam": "All Set", "ref": "10003", "key": "VYTFbhwXkqNhaXGCVGzU", "secret": "jNWZfJBznJWxlMabCULG"},
    {"naam": "Amaya Amsterdam", "ref": "20016", "key": "fofyzcGmBLpEYlAauJEh", "secret": "xGewtRknyUqJLzRHLmpC"},
    {"naam": "Batterijenstunter.nl", "ref": "10044", "key": "fXnCIdCuGBRGtclsUOlB", "secret": "CdgxCsWIHysEveBTXWvL"},
    {"naam": "Boorkopen.nl", "ref": "10043", "key": "sJHcZtdddEavsEtXpOoF", "secret": "lCOTAkpqCUDLwmJNNkfH"},
    {"naam": "Brandfusion Holland B.V.", "ref": "2006", "key": "PabQLIPjJOxawULUYhUr", "secret": "YUjoPmchNhCaBpAkiGsC"},
    {"naam": "Brandfusion Holland B.V. W", "ref": "2004", "key": "EbkXjLskXhmLboxomhSL", "secret": "RnKfBTLSEkFcDXVJHOxE"},
    {"naam": "Brandmarc - Sales B.V.", "ref": "2002", "key": "xvYiCPRorprKSeYcmXah", "secret": "ABxWjhyydKOxTKTgsLdY"},
    {"naam": "ByNoud", "ref": "10025", "key": "RohCGhOgnvxbnLiDXsWF", "secret": "wWJhlfZAERBhMuuHsyVd"},
    {"naam": "Cacaoii", "ref": "10034", "key": "ZNmZbYWUpFOIGizydZpe", "secret": "VtHRZWgJpJQEwbiUhedm"},
    {"naam": "Casual Lads", "ref": "10006", "key": "ooYGPAkzPTcrjbXqlmRr", "secret": "ZnLDJqVxPrSqvqYWcrax"},
    {"naam": "Celeste", "ref": "10028", "key": "MrhmAUVkLQhbGvwnICyk", "secret": "kPbHCmOqeulZysfKUgBa"},
    {"naam": "CultureCulture", "ref": "10042", "key": "QKhpsZMGCpuroEayYZIH", "secret": "FXhBGAXmROpUADagKQjD"},
    {"naam": "Ellastiek", "ref": "10007", "key": "VYEvFlklZSyVGhJwLmVG", "secret": "uRTXPyyEsMicUwYCcnvi"},
    {"naam": "Frankie & Liberty", "ref": "10030", "key": "UyqcoLSnWDkwVunkSceS", "secret": "FqPpPUNweOtXUmBhBLaU"},
    {"naam": "Greenfield Distribution", "ref": "10029", "key": "JlkMybstHHLqtwWMBWAW", "secret": "ShZJijHJcjzjvbXYsTVQ"},
    {"naam": "Huidvisie", "ref": "10001", "key": "oEJsvJfsGHGDilMUxJLg", "secret": "CuZhNuhFtDgrzZukthhd"},
    {"naam": "Lou Lilly", "ref": "10014", "key": "dVUKWNIghJbrgFHiFOIZ", "secret": "aDERZuxwELivtBmYffNQ"},
    {"naam": "MesVoeuxWear", "ref": "10037", "key": "KsLbdGQbiILptCJWrplW", "secret": "qiqMilbEXhysbyLSQDNP"},
]

BASE_URL = "https://servicelayer.wics.nl"

STATUS_LABELS = {
    "00": ("Aangemaakt", "pill-gray"), "10": ("Ingevoerd", "pill-gray"),
    "20": ("Vrijgegeven", "pill-blue"), "30": ("Bevestigd", "pill-blue"),
    "40": ("In uitvoering", "pill-orange"), "50": ("Gepickt", "pill-orange"),
    "60": ("Afgehandeld", "pill-green"), "70": ("Verzonden", "pill-green"),
    "90": ("Geannuleerd", "pill-gray"),
}
PRIORITY_MAP = {1: "🔴 Hoog", 2: "🟡 Normaal", 3: "🟢 Laag"}

# ── API helpers ───────────────────────────────────────────────
def auth_header(key, secret):
    token = b64encode(f"{key}:{secret}".encode()).decode()
    return {"Authorization": f"Basic {token}", "Content-Type": "application/json"}

def fetch_all(endpoint, key, secret):
    headers = auth_header(key, secret)
    results, page = [], 1
    while True:
        try:
            r = requests.get(
                f"{BASE_URL}/{endpoint}",
                headers=headers,
                params={"page": page, "pageSize": 100},
                timeout=15,
            )
            if r.status_code != 200:
                break
            data = r.json().get("data", [])
            if not data:
                break
            results.extend(data)
            page += 1
            time.sleep(0.1)
        except Exception:
            break
    return results

@st.cache_data(ttl=3600, show_spinner=False)
def load_all_orders(selected_names: tuple) -> pd.DataFrame:
    rows = []
    for o in OPDRACHTGEVERS:
        if o["naam"] in selected_names:
            items = fetch_all("api/order", o["key"], o["secret"])
            for item in items:
                item["_opdrachtgever"] = o["naam"]
            rows.extend(items)
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    rename = {
        "number": "Ordernummer", "reference": "Referentie",
        "additionalReference": "Extra Referentie", "deliveryDate": "Leverdatum",
        "statusCode": "StatusCode", "method": "Methode", "webshopId": "Webshop ID",
        "paid": "Betaald", "priority": "Prioriteit", "rideNumber": "Rit",
        "_opdrachtgever": "Opdrachtgever",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    if "Leverdatum" in df.columns:
        df["Leverdatum"] = pd.to_datetime(df["Leverdatum"], errors="coerce").dt.date
    if "StatusCode" in df.columns:
        df["Status"] = df["StatusCode"].map(lambda c: STATUS_LABELS.get(str(c), (str(c), "pill-gray"))[0])
    if "Prioriteit" in df.columns:
        df["Prioriteit"] = df["Prioriteit"].map(lambda p: PRIORITY_MAP.get(p, str(p)))
    if "Betaald" in df.columns:
        df["Betaald"] = df["Betaald"].map(lambda b: "✅ Ja" if b else "❌ Nee")
    return df

# ── Excel inslagen builder ────────────────────────────────────
def build_inslagen_excel(geselecteerde_opdrachtgevers):
    wb = Workbook()
    wb.remove(wb.active)

    header_fill = PatternFill("solid", start_color="1F4E79")
    header_font = Font(bold=True, color="FFFFFF", name="Arial", size=10)
    thin = Side(style="thin", color="D0D7DE")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    light_fill = PatternFill("solid", start_color="EBF3FB")

    HEADERS = [
        "Inslagnummer", "Referentie", "Inslag Datum", "Magazijn",
        "Status Code", "Status", "Voorraad Status Code", "Voorraad Status",
        "Type Code", "Type Omschrijving", "Opdrachtgever Nr"
    ]

    overzicht_ws = wb.create_sheet("📋 Overzicht", 0)
    overzicht_ws.append(["Opdrachtgever", "Referentie Nr", "Aantal Inslagen"])
    for col, w in zip("ABC", [30, 16, 18]):
        overzicht_ws.column_dimensions[col].width = w

    overzicht_rijen = []

    progress = st.progress(0, text="Inslagen ophalen...")
    totaal = len(geselecteerde_opdrachtgevers)

    for i, o in enumerate(geselecteerde_opdrachtgevers):
        progress.progress((i) / totaal, text=f"Ophalen: {o['naam']}...")
        receipts = fetch_all("api/receipt", o["key"], o["secret"])

        sheet_naam = o["naam"][:31]
        ws = wb.create_sheet(sheet_naam)
        ws.append(HEADERS)

        # Header opmaak
        for col in range(1, len(HEADERS) + 1):
            cell = ws.cell(row=1, column=col)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border
        ws.row_dimensions[1].height = 28

        for j, r in enumerate(receipts):
            ws.append([
                r.get("number", ""),
                r.get("reference", ""),
                r.get("receiptDate", ""),
                r.get("warehouseCode") or r.get("warehouse", ""),
                r.get("statusCode", ""),
                r.get("statusDescription", ""),
                r.get("stockStatusCode", ""),
                r.get("stockStatusDescription", ""),
                r.get("typeCode", ""),
                r.get("typeDescription", ""),
                o["ref"],
            ])
            # Zebra styling
            if j % 2 == 1:
                for col in range(1, len(HEADERS) + 1):
                    ws.cell(row=j + 2, column=col).fill = light_fill
            for col in range(1, len(HEADERS) + 1):
                ws.cell(row=j + 2, column=col).font = Font(name="Arial", size=9)
                ws.cell(row=j + 2, column=col).border = border

        # Kolombreedtes
        for col, w in zip(range(1, len(HEADERS) + 1), [14, 22, 14, 12, 12, 22, 16, 24, 10, 24, 16]):
            ws.column_dimensions[get_column_letter(col)].width = w

        ws.freeze_panes = "A2"
        ws.auto_filter.ref = f"A1:{get_column_letter(len(HEADERS))}1"

        overzicht_rijen.append((o["naam"], o["ref"], len(receipts)))

    # Overzicht tabblad vullen
    for naam, ref, aantal in overzicht_rijen:
        overzicht_ws.append([naam, ref, aantal])

    # Overzicht opmaak
    for col in range(1, 4):
        cell = overzicht_ws.cell(row=1, column=col)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
    overzicht_ws.row_dimensions[1].height = 28
    for row in range(2, len(overzicht_rijen) + 2):
        for col in range(1, 4):
            overzicht_ws.cell(row=row, column=col).font = Font(name="Arial", size=9)
            overzicht_ws.cell(row=row, column=col).border = border
            if row % 2 == 1:
                overzicht_ws.cell(row=row, column=col).fill = light_fill
    overzicht_ws.freeze_panes = "A2"

    progress.progress(1.0, text="Excel gereed!")
    time.sleep(0.5)
    progress.empty()

    # Naar bytes
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📦 WICS")
    st.markdown("---")

    alle_namen = [o["naam"] for o in OPDRACHTGEVERS]
    geselecteerd = st.multiselect("Opdrachtgevers", options=alle_namen, default=alle_namen[:2])

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


# ── Tabs ──────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📊 Orders Dashboard", "📥 Inslagen Export"])

# ══════════════════════════════════════════════════════════════
# TAB 1 — ORDERS
# ══════════════════════════════════════════════════════════════
with tab1:
    st.markdown("# 📦 WICS Order Dashboard")
    st.markdown(f"Overzicht van orders voor **{', '.join(geselecteerd) if geselecteerd else '—'}**")

    if not geselecteerd:
        st.warning("Selecteer minimaal één opdrachtgever in de zijbalk.")
        st.stop()

    with st.spinner("Orders ophalen uit WICS..."):
        df = load_all_orders(tuple(sorted(geselecteerd)))

    if df.empty:
        st.error("Geen data ontvangen. Controleer de API-verbinding of credentials.")
    else:
        if "Leverdatum" in df.columns:
            df = df[(df["Leverdatum"] >= datum_van) & (df["Leverdatum"] <= datum_tot)]
        if "Status" in df.columns and status_filter:
            df = df[df["Status"].isin(status_filter)]

        totaal = len(df)
        afgehandeld = len(df[df["Status"].isin(["Afgehandeld", "Verzonden"])]) if "Status" in df.columns else 0
        in_uitvoer = len(df[df["Status"] == "In uitvoering"]) if "Status" in df.columns else 0
        openstaand = len(df[df["Status"].isin(["Aangemaakt", "Ingevoerd", "Vrijgegeven", "Bevestigd"])]) if "Status" in df.columns else 0
        pct = round(afgehandeld / totaal * 100) if totaal > 0 else 0

        col1, col2, col3, col4, col5 = st.columns(5)
        for col, val, label, delta in [
            (col1, str(totaal), "Totaal orders", ""),
            (col2, str(afgehandeld), "Afgehandeld", f"<span class='kpi-delta-pos'>↑ {pct}%</span>"),
            (col3, str(in_uitvoer), "In uitvoering", ""),
            (col4, str(openstaand), "Openstaand", ""),
            (col5, str(len(geselecteerd)), "Opdrachtgevers", ""),
        ]:
            with col:
                st.markdown(f"<div class='kpi-card'><div class='kpi-value'>{val}</div><div class='kpi-label'>{label}</div>{delta}</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='section-title'>Orders per status</div>", unsafe_allow_html=True)
            if "Status" in df.columns:
                st.bar_chart(df["Status"].value_counts().rename_axis("Status").reset_index(name="Aantal").set_index("Status"), color="#3b82f6")
        with c2:
            st.markdown("<div class='section-title'>Orders per opdrachtgever</div>", unsafe_allow_html=True)
            if "Opdrachtgever" in df.columns:
                st.bar_chart(df["Opdrachtgever"].value_counts().rename_axis("Opdrachtgever").reset_index(name="Aantal").set_index("Opdrachtgever"), color="#8b5cf6")

        if "Leverdatum" in df.columns:
            st.markdown("<div class='section-title'>Orders over tijd</div>", unsafe_allow_html=True)
            trend = df.groupby("Leverdatum").size().reset_index(name="Aantal").sort_values("Leverdatum")
            st.line_chart(trend.set_index("Leverdatum"), color="#10b981")

        st.markdown("<div class='section-title'>Orderoverzicht</div>", unsafe_allow_html=True)
        toon_kolommen = [k for k in ["Opdrachtgever", "Ordernummer", "Referentie", "Status", "Leverdatum", "Prioriteit", "Betaald", "Methode"] if k in df.columns]
        zoek = st.text_input("🔍 Zoek op ordernummer of referentie")
        df_tabel = df[toon_kolommen].copy()
        if zoek:
            mask = df_tabel.apply(lambda col: col.astype(str).str.contains(zoek, case=False, na=False)).any(axis=1)
            df_tabel = df_tabel[mask]
        st.dataframe(df_tabel.sort_values("Leverdatum", ascending=False) if "Leverdatum" in df_tabel.columns else df_tabel, use_container_width=True, height=450, hide_index=True)
        st.caption(f"{len(df_tabel)} orders weergegeven")

# ══════════════════════════════════════════════════════════════
# TAB 2 — INSLAGEN EXPORT
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("# 📥 Inslagen Export")
    st.markdown("Genereer een Excel-bestand met alle inslagen per opdrachtgever, elk op een eigen tabblad.")

    st.markdown("---")

    # Opdrachtgever selectie voor export
    alle_namen_export = [o["naam"] for o in OPDRACHTGEVERS]
    export_selectie = st.multiselect(
        "Selecteer opdrachtgevers voor export",
        options=alle_namen_export,
        default=alle_namen_export,
        key="export_selectie"
    )

    # Periode filter voor export
    col_a, col_b = st.columns(2)
    with col_a:
        export_van = st.date_input("Inslagen vanaf", value=date(2024, 1, 1), key="export_van")
    with col_b:
        export_tot = st.date_input("Inslagen tot", value=date.today(), key="export_tot")

    st.markdown("---")

    if not export_selectie:
        st.warning("Selecteer minimaal één opdrachtgever.")
    else:
        st.info(f"📋 **{len(export_selectie)} opdrachtgevers** geselecteerd — elk krijgt een eigen tabblad in de Excel.")

        if st.button("📊 Genereer Excel", type="primary", use_container_width=False):
            geselecteerde_opdracht = [o for o in OPDRACHTGEVERS if o["naam"] in export_selectie]
            excel_bytes = build_inslagen_excel(geselecteerde_opdracht)

            bestandsnaam = f"WICS_Inslagen_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"

            st.download_button(
                label="⬇️ Download Excel",
                data=excel_bytes,
                file_name=bestandsnaam,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=False,
            )
            st.success(f"✅ Excel gegenereerd met {len(export_selectie)} tabbladen + overzichtstabblad!")
