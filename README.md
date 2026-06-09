# 📦 WICS Order Dashboard

Streamlit dashboard dat orders en orderstatussen ophaalt uit de WICS WMS API voor meerdere opdrachtgevers.

---

## 🚀 Deployment via GitHub + Railway

### Stap 1 — Zet het op GitHub

1. Maak een nieuw repository aan op [github.com](https://github.com/new)
   - Naam: `wics-dashboard`
   - Zet op **Private** (bevat API credentials)
2. Upload deze bestanden:
   - `app.py`
   - `requirements.txt`
   - `README.md`

Of via de terminal:
```bash
git init
git add .
git commit -m "Initial WICS dashboard"
git remote add origin https://github.com/JOUWGEBRUIKERSNAAM/wics-dashboard.git
git push -u origin main
```

---

### Stap 2 — Deploy op Railway

1. Ga naar [railway.app](https://railway.app) en log in met je GitHub account
2. Klik op **"New Project"** → **"Deploy from GitHub repo"**
3. Selecteer je `wics-dashboard` repository
4. Railway detecteert automatisch dat het een Python app is

**Start command instellen:**
- Ga naar je service → **Settings** → **Deploy**
- Zet het start command op:
```
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

5. Klik op **Deploy** — na ~2 minuten is je dashboard live!
6. Ga naar **Settings** → **Domains** → genereer een publieke URL

---

## ➕ Nieuwe opdrachtgever toevoegen

Open `app.py` en voeg een rij toe in de `OPDRACHTGEVERS` lijst bovenaan:

```python
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
    # Voeg hier nieuwe opdrachtgevers toe:
    {
        "naam": "Nieuwe Klant BV",
        "key": "NIEUWE_API_KEY",
        "secret": "NIEUWE_API_SECRET",
        "url": "https://servicelayer.wics.nl",
    },
]
```

Commit en push naar GitHub → Railway herdeployt automatisch.

---

## 🔒 Veiligheid (aanbevolen voor productie)

Voor een veiligere setup kun je de credentials als environment variables instellen in Railway:

1. Railway → je service → **Variables**
2. Voeg toe: `ALLSET_KEY`, `ALLSET_SECRET`, `AMAYA_KEY`, `AMAYA_SECRET`
3. Pas `app.py` aan om `os.environ.get("ALLSET_KEY")` te gebruiken

---

## 📊 Functies

- ✅ Alle orders per opdrachtgever met automatische paginering
- ✅ KPI-kaarten: totaal, afgehandeld, in uitvoering, openstaand
- ✅ Grafieken: orders per status, per opdrachtgever, trend over tijd
- ✅ Zoekfunctie op ordernummer of referentie
- ✅ Filter op status, periode en opdrachtgever
- ✅ Data wordt 1 uur gecached (minder API-calls)
- ✅ Handmatig verversen via de knop in de zijbalk
