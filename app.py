import streamlit as st
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, date, timezone, timedelta
import datetime as dt_module
import time
import re

load_dotenv()

def get_secret(key):
    try:
        return st.secrets[key]
    except:
        return os.getenv(key, "")

st.set_page_config(page_title="Canlı Skor + AI", page_icon="⚽", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.team-name{font-size:14px;font-weight:600}
.score-box{font-size:22px;font-weight:bold;text-align:center}
.status-live{color:#ff4444;font-size:11px;font-weight:bold}
.status-finished{color:#888;font-size:11px}
.status-upcoming{color:#3b82f6;font-size:11px}
.ai-box{border:1px solid rgba(102,126,234,.35);border-radius:10px;padding:12px;margin-top:8px;
        background:rgba(102,126,234,.05);line-height:1.7;font-size:14px}
.pred-box{border:2px solid #22c55e;border-radius:10px;padding:10px;margin:8px 0;
          background:rgba(34,197,94,.07);text-align:center}
.pred-score{font-size:26px;font-weight:900;color:#16a34a;letter-spacing:1px}
.pred-label{font-size:11px;color:#16a34a;opacity:.8}
.bulk-result{border:1px solid rgba(234,179,8,.4);border-radius:8px;padding:10px;
             margin:6px 0;background:rgba(234,179,8,.05);font-size:13px;line-height:1.6}
.divider{border-top:1px solid rgba(128,128,128,.12);margin:8px 0}
.cache-info{font-size:11px;color:var(--color-text-tertiary);margin-top:4px}
.model-badge{display:inline-block;font-size:10px;padding:1px 6px;border-radius:10px;margin-left:6px;vertical-align:middle}
.mb-groq{background:#FAEEDA;color:#633806}
.mb-gemini{background:#EAF3DE;color:#27500A}
.mb-claude{background:#EEEDFE;color:#3C3489}
.mb-gpt{background:#E6F1FB;color:#0C447C}
.news-box{background:rgba(59,130,246,.06);border:1px solid rgba(59,130,246,.2);
          border-radius:8px;padding:10px;margin:6px 0;font-size:13px;line-height:1.6}
/* ── SKOR TEK SATIR ── */
.pred-score{white-space:nowrap !important}
/* ── SCROLL TO TOP ── */
#scroll-top-btn{
  position:fixed;bottom:24px;right:18px;z-index:9999;
  width:46px;height:46px;border-radius:50%;
  background:#4e8cff;color:#fff;border:2px solid rgba(255,255,255,.3);
  font-size:20px;cursor:pointer;box-shadow:0 3px 12px rgba(0,0,0,.3);
  display:flex;align-items:center;justify-content:center;
  opacity:0;transition:opacity .25s,transform .2s;pointer-events:none;transform:scale(.8)
}
#scroll-top-btn.visible{opacity:1;pointer-events:auto;transform:scale(1)}
/* ── BUTONLAR: MOBİLDE YAN YANA ── */
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
  flex: 1 1 0 !important;
  min-width: 0 !important;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div > div > button {
  width: 100% !important;
  padding: 0.25rem 0.3rem !important;
  font-size: 12px !important;
  white-space: nowrap !important;
  overflow: hidden !important;
}
@media(max-width:768px){
  .team-name{font-size:13px}
  .score-box{font-size:20px}
  .pred-score{font-size:22px}
  .ai-box{font-size:13px;padding:10px}
  div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div > div > button {
    font-size: 11px !important;
    padding: 0.2rem 0.2rem !important;
  }
}
</style>
""", unsafe_allow_html=True)

# ── SCROLL TO TOP BUTONU (sabit, sağ alt) ─────────────────────────
st.markdown("""
<button id="scroll-top-btn" onclick="window.scrollTo({top:0,behavior:'smooth'})" title="Yukarı çık">⬆</button>
<script>
(function(){
  var btn = document.getElementById('scroll-top-btn');
  if(!btn) return;
  var ticking = false;
  function onScroll(){
    if(!ticking){
      window.requestAnimationFrame(function(){
        btn.classList.toggle('visible', window.scrollY > 300);
        ticking = false;
      });
      ticking = true;
    }
  }
  window.addEventListener('scroll', onScroll, {passive:true});
  // Streamlit içinde iframe varsa parent'a da bak
  try{
    var frame = window.frameElement;
    if(frame){
      var parentWin = frame.ownerDocument.defaultView;
      parentWin.addEventListener('scroll', onScroll, {passive:true});
    }
  }catch(e){}
})();
</script>
""", unsafe_allow_html=True)

API_KEY    = get_secret("API_SPORTS_KEY")
GEMINI_KEY = get_secret("GEMINI_API_KEY")
GROQ_KEY   = get_secret("GROQ_API_KEY")
OPENAI_KEY   = get_secret("OPENAI_API_KEY")
DEEPSEEK_KEY = get_secret("DEEPSEEK_API_KEY")


MAJOR_IDS = {39,140,135,78,61,94,88,144,207,2,3,848,1,12,120,57}

SPORT_CONFIG = {
    "⚽ Futbol":     {"key":"football",  "base":"https://v3.football.api-sports.io",  "emoji":"⚽"},
    "🏀 Basketbol":  {"key":"basketball","base":"https://v1.basketball.api-sports.io","emoji":"🏀"},
    "🎾 Tenis":      {"key":"tennis",    "base":"https://v1.tennis.api-sports.io",    "emoji":"🎾"},
    "🏐 Voleybol":   {"key":"volleyball","base":"https://v1.volleyball.api-sports.io","emoji":"🏐"},
    "🏒 Hokey":      {"key":"hockey",    "base":"https://v1.hockey.api-sports.io",    "emoji":"🏒"},
    "🤾 Hentbol":    {"key":"handball",  "base":"https://v1.handball.api-sports.io",  "emoji":"🤾"},
    "🏉 Rugby":      {"key":"rugby",     "base":"https://v1.rugby.api-sports.io",     "emoji":"🏉"},
    "🤼 MMA":        {"key":"mma",       "base":"https://v1.mma.api-sports.io",       "emoji":"🤼"},
    "🏎️ Formula 1": {"key":"formula-1", "base":"https://v1.formula-1.api-sports.io", "emoji":"🏎️"},
}

AI_MODELS = {
    "🟡 Groq – Llama 3.3":    {"id":"groq",      "cost":"Ücretsiz",      "badge":"mb-groq"},
    "🟢 Gemini 2.0 Flash":    {"id":"gemini",    "cost":"~$0/ay",        "badge":"mb-gemini"},
    "⚪ GPT-4o Mini":          {"id":"gpt",       "cost":"~$1-2/ay",      "badge":"mb-gpt"},
    "🔴 DeepSeek V3":         {"id":"deepseek",  "cost":"~$0.01-0.1/ay", "badge":"mb-groq"},
}

LIVE_SH  = {"1H","2H","ET","BT","P","LIVE","HT","Q1","Q2","Q3","Q4","OT"}
DONE_SH  = {"FT","AET","PEN","AOT","FINISHED","ENDED","COMPLETE"}
WAIT_SH  = {"NS"}
TZ_TR    = timezone(timedelta(hours=3))

# ── SESSION STATE ─────────────────────────────────────────────────
for k,v in [("bulk_results",{}),("selected",set()),("live_loaded",False),("live_data",[]),("live_ts",None),("analysis_history",[]),("gemini_fallback",{}),("detail_match",None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# Type safety - ensure gemini_fallback is always a dict
if not isinstance(st.session_state.gemini_fallback, dict):
    st.session_state.gemini_fallback = {}

# ── HELPERS ───────────────────────────────────────────────────────
def get_sh(m, sk):
    if sk=="football": return m["fixture"]["status"]["short"]
    s = m.get("status",{})
    return s.get("short",s.get("long","?")) if isinstance(s,dict) else str(s)

def kickoff_tr(m, sk):
    try:
        if sk=="football":
            ds = m["fixture"]["date"]
        elif sk=="tennis":
            ds = m.get("date","") or m.get("time","") or ""
        else:
            ds = m.get("date","") or m.get("time","") or m.get("timestamp","") or ""
        if not ds: return ""
        # Handle unix timestamp
        if isinstance(ds, (int, float)):
            from datetime import datetime as _dt
            return _dt.fromtimestamp(ds, tz=TZ_TR).strftime("%H:%M")
        ds = str(ds)
        dt = datetime.fromisoformat(ds.replace("Z","+00:00"))
        if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(TZ_TR).strftime("%H:%M")
    except: return ""

# ── API ───────────────────────────────────────────────────────────
def api_get(url, params=None):
    try:
        r = requests.get(url, headers={"x-apisports-key":API_KEY}, params=params, timeout=10)
        if r.status_code==200:
            d=r.json()
            errs=d.get("errors",{})
            if errs and errs not in ([],{}):
                msg=list(errs.values())[0] if isinstance(errs,dict) else str(errs)
                print(f"API error: {msg}")
                return None
            return d
        print(f"HTTP {r.status_code}: {url}")
    except Exception as e:
        print(f"API exception: {e}")
    return None

# Maç öncesi: günlük cache (sabah 1 kez çekilir, gün boyunca sabit)
@st.cache_data(ttl=86400, show_spinner=False)
def fetch_prematch_cached(sk, base, ds, _api_key):
    ep={"mma":"fights","formula-1":"races"}.get(sk,"games")
    if sk=="football": ep="fixtures"
    try:
        r=requests.get(f"{base}/{ep}",headers={"x-apisports-key":_api_key},params={"date":ds},timeout=10)
        if r.status_code==200:
            d=r.json()
            errs=d.get("errors",{})
            if errs and errs not in ([],{}): return [],None
            raw=[m for m in d.get("response",[]) if get_sh(m,sk) in WAIT_SH]
            ts=datetime.now(TZ_TR).strftime("%H:%M")
            return raw, ts
    except: pass
    return [], None

# Canlı: cache yok, her tetiklemede taze veri
def fetch_live_now(sk, base, ds):
    ep={"mma":"fights","formula-1":"races"}.get(sk,"games")
    if sk=="football": ep="fixtures"
    d=api_get(f"{base}/{ep}",{"date":ds})
    if not d: return []
    return [m for m in d.get("response",[]) if get_sh(m,sk) in (LIVE_SH|DONE_SH)]

@st.cache_data(ttl=60, show_spinner=False)
def fetch_stats(fid):
    d=api_get("https://v3.football.api-sports.io/fixtures/statistics",{"fixture":fid})
    return d.get("response",[]) if d else []

@st.cache_data(ttl=60, show_spinner=False)
def fetch_events(fid):
    d=api_get("https://v3.football.api-sports.io/fixtures/events",{"fixture":fid})
    return d.get("response",[]) if d else []

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_form(tid,lid,season):
    d=api_get("https://v3.football.api-sports.io/fixtures",{"team":tid,"league":lid,"season":season,"last":5})
    return d.get("response",[]) if d else []

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_tstat(tid,lid,season):
    d=api_get("https://v3.football.api-sports.io/teams/statistics",{"team":tid,"league":lid,"season":season})
    return d.get("response",{}) if d else {}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_injuries(tid,season):
    d=api_get("https://v3.football.api-sports.io/injuries",{"team":tid,"season":season})
    return d.get("response",[]) if d else []

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_h2h(h_id,a_id):
    d=api_get("https://v3.football.api-sports.io/fixtures/headtohead",{"h2h":f"{h_id}-{a_id}","last":5})
    return d.get("response",[]) if d else []

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_standings(lid,season):
    d=api_get("https://v3.football.api-sports.io/standings",{"league":lid,"season":season})
    try: return d["response"][0]["league"]["standings"][0] if d else []
    except: return []

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_predictions(fid):
    d=api_get("https://v3.football.api-sports.io/predictions",{"fixture":fid})
    return d.get("response",[{}])[0] if d else {}

# ── AI ────────────────────────────────────────────────────────────
def call_groq(prompt):
    if not GROQ_KEY: return None,"⚠️ Groq key bulunamadı (.env → GROQ_API_KEY)"
    try:
        from groq import Groq
        r=Groq(api_key=GROQ_KEY).chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":prompt}],
            max_tokens=900,temperature=0.7)
        return r.choices[0].message.content,None
    except Exception as e:
        err=str(e)
        # Rate limit → otomatik Gemini fallback
        if "429" in err or "rate_limit" in err or "TPD" in err:
            if GEMINI_KEY:
                st.toast("⚡ Groq limiti doldu, Gemini'ye geçiliyor...", icon="🔄")
                return call_gemini(prompt)
            # Kalan süreyi parse et
            import re as _re
            m=_re.search(r'try again in (\d+m\d+)', err)
            wait=m.group(1) if m else "bir süre"
            return None,f"⏳ Groq günlük limit doldu ({wait} bekle). Gemini veya başka model seç."
        return None,f"Groq hatası: {err[:120]}"

def call_gemini(prompt, use_search=False):
    if not GEMINI_KEY: return None,"⚠️ Gemini key bulunamadı (.env → GEMINI_API_KEY)"
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_KEY)
        if use_search:
            try:
                from google.genai import types
                search_tool = types.Tool(google_search=types.GoogleSearch())
                config = types.GenerateContentConfig(tools=[search_tool])
                r = client.models.generate_content(
                    model="gemini-2.5-flash", contents=prompt, config=config)
                return r.text, None
            except Exception as _se:
                # Any error with search → fallback to plain
                r = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                return r.text, None
        else:
            r = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            return r.text, None
    except Exception as e:
        err=str(e)
        if any(x in err for x in ["429","quota","EXHAUSTED"]):
            return None,"⚠️ Gemini günlük kotası doldu. Groq'a geç."
        return None,f"Gemini hatası: {err[:200]}"

def call_deepseek(prompt):
    if not DEEPSEEK_KEY: return None,"⚠️ DeepSeek key bulunamadı (.env → DEEPSEEK_API_KEY)"
    try:
        from openai import OpenAI
        r=OpenAI(api_key=DEEPSEEK_KEY,base_url="https://api.deepseek.com").chat.completions.create(
            model="deepseek-chat",
            messages=[{"role":"user","content":prompt}],
            max_tokens=900,temperature=0.7)
        return r.choices[0].message.content,None
    except Exception as e:
        return None,f"DeepSeek hatası: {e}"

def call_gpt(prompt):
    if not OPENAI_KEY: return None,"⚠️ OpenAI key bulunamadı (.env → OPENAI_API_KEY)"
    try:
        from openai import OpenAI
        r=OpenAI(api_key=OPENAI_KEY).chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            max_tokens=900,temperature=0.7)
        return r.choices[0].message.content,None
    except Exception as e:
        return None,f"GPT hatası: {e}"

def run_ai(prompt, model_name, use_web_search=False):
    mid=AI_MODELS[model_name]["id"]
    if mid=="groq":     return call_groq(prompt)
    if mid=="gemini":   return call_gemini(prompt, use_search=use_web_search)
    if mid=="deepseek": return call_deepseek(prompt)
    if mid=="gpt":      return call_gpt(prompt)
    return None,"Model bulunamadı"

def extract_pred(text, sport):
    """Extract FINAL score prediction only - ignore quarter/set/half scores."""
    if not text: return None
    sl = sport.lower()
    # Sadece basketbol yüksek skor kullanır (2-3 haneli)
    # Hokey futbol gibi küçük skor (3-2), voleybol set sayısı (3-1)
    is_basketball = any(w in sl for w in ["basket","nba"])
    is_volleyball = "voleybol" in sl

    final_keywords = ["final tahmin","maç tahmin","tahmin edilen skor","tahmin: ","sonuç tahmin","biteceğ","final skor","🔮","fİnal","fİnAl","tahmin edilen"]
    final_lines = " ".join(l for l in text.split("\n") if any(w in l.lower() for w in final_keywords))
    exclude_keywords = ["çeyrek","1.çeyrek","set","yarı","periyot","q1","q2","q3","q4"]

    if is_basketball:
        # Basketbol: her takım en az 60, en fazla 180 sayı yapar
        pat = r'\b(\d{2,3})\s*[-–]\s*(\d{2,3})\b'
        direct = re.search(r'(?:tahmin edilen skor|tahmin)[:\s]+([0-9]{2,3})\s*[-–]\s*([0-9]{2,3})', text, re.IGNORECASE)
        if direct:
            a,b = int(direct.group(1)), int(direct.group(2))
            if a >= 60 and b >= 60:
                return f"{a} – {b}"
        for src in [final_lines, text]:
            for m in re.finditer(pat, src):
                line_start = src.rfind("\n", 0, m.start()) + 1
                line_end = src.find("\n", m.end())
                if line_end == -1: line_end = len(src)
                line = src[line_start:line_end].lower()
                if any(w in line for w in exclude_keywords): continue
                a,b = int(m.group(1)), int(m.group(2))
                # Basketbolda her iki takım da en az 60 sayı yapar
                if a < 60 or b < 60: continue
                if a > 180 or b > 180: continue
                return f"{a} – {b}"
    else:
        # Direct pattern search first
        direct = re.search(r'(?:tahmin edilen skor|tahmin)[:\s]+([0-9]{1,2})\s*[-–]\s*([0-9]{1,2})', text, re.IGNORECASE)
        if direct:
            return f"{direct.group(1)} – {direct.group(2)}"
        is_set_sport = any(w in sport.lower() for w in ["voleybol","hentbol","rugby"])
        pat = r'\b([0-9]{1,2})\s*[-–]\s*([0-9]{1,2})\b'
        for src in [final_lines, text]:
            for m in re.finditer(pat, src):
                line_start = src.rfind("\n", 0, m.start()) + 1
                line_end = src.find("\n", m.end())
                if line_end == -1: line_end = len(src)
                line = src[line_start:line_end].lower()
                if any(w in line for w in exclude_keywords): continue
                a,b = int(m.group(1)), int(m.group(2))
                if is_set_sport:
                    # Voleybol: set sayısı 0-3 arası VEYA 20-30 arası set skoru
                    if (a <= 3 and b <= 3) or (20 <= a <= 35 and 20 <= b <= 35):
                        return f"{a} – {b}"
                else:
                    if a > 20 or b > 20: continue
                    return f"{a} – {b}"
    return None

def extract_sub_pred(text, sport):
    """Extract half-time/period prediction."""
    if not text: return {}
    sl = sport.lower()
    if any(w in sl for w in ["voleybol","formula","mma","rugby"]): return {}
    is_tennis  = "tenis" in sl
    is_basket  = any(w in sl for w in ["basket","nba"])
    is_hockey  = any(w in sl for w in ["hokey","hockey"])
    result = {}
    lines = text.split("\n")
    for line in lines:
        ll = line.lower()
        if is_tennis:
            if "1.set" in ll or "ilk set" in ll:
                m = re.search(r'(\d{1,2})\s*[-–]\s*(\d{1,2})', line)
                if m:
                    a,b = int(m.group(1)),int(m.group(2))
                    if a<=7 and b<=7: result["1.Set"] = f"{m.group(1)}–{m.group(2)}"
        elif is_basket:
            # Basketbol: 1.Yarı büyük skor (2 haneli)
            if any(w in ll for w in ["1.yarı","ilk yarı","yarı skor","halftime"]):
                m = re.search(r'(\d{2,3})\s*[-–]\s*(\d{2,3})', line)
                if m: result["1.Yarı"] = f"{m.group(1)}–{m.group(2)}"
        elif is_hockey:
            # Hokey: 1.Periyot küçük skor (0-3 arası)
            if any(w in ll for w in ["1.periyot","ilk periyot","birinci periyot","1st period"]):
                m = re.search(r'(\d{1,2})\s*[-–]\s*(\d{1,2})', line)
                if m:
                    a,b = int(m.group(1)), int(m.group(2))
                    if a <= 5 and b <= 5: result["1.Per"] = f"{m.group(1)}–{m.group(2)}"
        else:
            # Futbol/Hentbol: 1.Yarı
            if any(w in ll for w in ["1.yarı","ilk yarı","devre arası","halftime"]):
                m = re.search(r'(\d{1,2})\s*[-–]\s*(\d{1,2})', line)
                if m:
                    a,b = int(m.group(1)), int(m.group(2))
                    if a <= 10 and b <= 10:
                        result["1.Yarı"] = f"{m.group(1)}–{m.group(2)}"
    return result

def extract_consensus(results_dict, sport):
    """4 modelin tahminlerinden ortak paydaları çıkar."""
    sl = sport.lower()
    is_football = "futbol" in sl
    is_basketball = any(w in sl for w in ["basket","nba"])
    is_big = is_basketball  # Sadece basketbol yüksek skor mantığı kullanır
    
    preds = []
    for model_name, res in results_dict.items():
        if res.get("text") and not res.get("err"):
            p = extract_pred(res["text"], sport)
            if p:
                try:
                    parts = re.split(r'[-–]', p)
                    if len(parts)==2:
                        preds.append((int(parts[0].strip()), int(parts[1].strip()), model_name, res["text"]))
                except: pass
    
    if len(preds) < 2: return None
    
    consensus = {}
    scores_h = [p[0] for p in preds]
    scores_a = [p[1] for p in preds]
    totals = [p[0]+p[1] for p in preds]
    
    # Kazanan konsensüsü
    winners = []
    for h,a,_,_ in preds:
        if h > a: winners.append("ev")
        elif a > h: winners.append("dep")
        else: winners.append("beraberlik")
    
    from collections import Counter
    w_count = Counter(winners)
    top_winner = w_count.most_common(1)[0]
    w_names = {"ev": preds[0][2] if preds else "Ev", "dep": "Deplasman", "beraberlik": "Beraberlik"}
    
    if top_winner[1] >= 3:  # 3+ model aynı fikirde
        consensus["kazanan"] = ("✅ Güçlü konsensüs", f"{'Ev' if top_winner[0]=='ev' else 'Deplasman' if top_winner[0]=='dep' else 'Beraberlik'} kazanır ({top_winner[1]}/4 model)")
    elif top_winner[1] == 2:
        consensus["kazanan"] = ("⚡ Hafif üstünlük", f"{'Ev' if top_winner[0]=='ev' else 'Deplasman' if top_winner[0]=='dep' else 'Beraberlik'} lehine (2/4 model)")
    
    # Toplam gol/skor üst-alt
    avg_total = sum(totals) / len(totals)
    if is_football:
        line = 2.5
        over = sum(1 for t in totals if t > line)
        if over >= 3:
            consensus["üst/alt"] = ("📈 Üst", f"2.5 Üst ({over}/4 model, ort: {avg_total:.1f} gol)")
        elif over <= 1:
            consensus["üst/alt"] = ("📉 Alt", f"2.5 Alt ({4-over}/4 model, ort: {avg_total:.1f} gol)")
        
        # KG var/yok tahmini - text analizi
        kg_var = sum(1 for _,_,_,txt in preds if any(w in txt.lower() for w in ["kg var","karşılıklı gol","her iki takım da"]))
        if kg_var >= 3:
            consensus["kg"] = ("⚽ KG Var", f"Her iki takım da gol atar ({kg_var}/4 model)")
        elif kg_var <= 1:
            consensus["kg"] = ("🔒 KG Yok", f"Tek taraflı gol bekleniyor")
    
    elif is_big:
        avg_h = sum(scores_h)/len(scores_h)
        avg_a = sum(scores_a)/len(scores_a)
        avg_total = avg_h + avg_a
        consensus["skor_ort"] = ("📊 Ortalama Skor", f"Ev {avg_h:.0f} – Dep {avg_a:.0f} | Toplam: {avg_total:.0f} sayı")
        # Handikap
        spreads = [h-a for h,a,_,_ in preds]
        avg_spread = sum(spreads)/len(spreads)
        if abs(avg_spread) >= 8:
            favori = "Ev" if avg_spread > 0 else "Deplasman"
            consensus["handikap"] = ("🎯 Handikap", f"{favori} -7.5 handikap kazanır (ort fark: {abs(avg_spread):.0f})")
    
    return consensus if consensus else None

# ── PROMPTS ───────────────────────────────────────────────────────
def form_str(fxs,tid):
    out=[]
    for f in fxs[-5:]:
        hw=f["teams"]["home"]["winner"]; aw=f["teams"]["away"]["winner"]
        ih=f["teams"]["home"]["id"]==tid
        out.append("G" if (hw if ih else aw) else ("B" if (not hw and not aw) else "M"))
    return " ".join(out) if out else "Veri yok"

def season_str(ts,name):
    if not ts: return ""
    g=ts.get("goals",{}); fx=ts.get("fixtures",{})
    sc=g.get("for",{}).get("average",{}).get("total","?")
    cn=g.get("against",{}).get("average",{}).get("total","?")
    w=fx.get("wins",{}).get("total","?"); d=fx.get("draws",{}).get("total","?"); l=fx.get("loses",{}).get("total","?")
    fm=ts.get("form","")[-10:] if ts.get("form") else ""
    return f"{name}: {w}G/{d}B/{l}M | Ort {sc} attı / {cn} yedi | Form: {fm}"

def injuries_txt(injuries, team_name):
    if not injuries: return ""
    aktif = [i for i in injuries if i.get("player") and i.get("reason")]
    if not aktif: return ""
    lines = [f"  - {i['player']['name']} ({i.get('reason','?')})" for i in aktif[:5]]
    return team_name + " sakatlıklar:\n" + "\n".join(lines)

def h2h_txt(h2h_matches):
    if not h2h_matches: return ""
    lines = []
    for m in h2h_matches[-5:]:
        ht = m["teams"]["home"]["name"]; at = m["teams"]["away"]["name"]
        hg = m["goals"]["home"] or 0; ag = m["goals"]["away"] or 0
        dt = m["fixture"]["date"][:10]
        lines.append(f"  {dt}: {ht} {hg}-{ag} {at}")
    return "Son karşılaşmalar (H2H):\n" + "\n".join(lines)

def standings_txt(standings, home_id, away_id):
    if not standings: return ""
    h_row = next((s for s in standings if s["team"]["id"]==home_id), None)
    a_row = next((s for s in standings if s["team"]["id"]==away_id), None)
    parts = []
    if h_row: parts.append(f"  {h_row['team']['name']}: {h_row['rank']}. sira, {h_row['points']} puan")
    if a_row: parts.append(f"  {a_row['team']['name']}: {a_row['rank']}. sira, {a_row['points']} puan")
    return ("Puan durumu:\n" + "\n".join(parts)) if parts else ""

def predictions_txt(pred):
    if not pred: return ""
    try:
        winner = pred.get("predictions",{}).get("winner",{})
        pct = pred.get("predictions",{}).get("percent",{})
        w_name = winner.get("name","?")
        home_pct = pct.get("home","?"); draw_pct = pct.get("draws","?"); away_pct = pct.get("away","?")
        advice = pred.get("predictions",{}).get("advice","")
        return f"API Tahmini: {w_name} kazanır | Ev%{home_pct} Beraberlik%{draw_pct} Deplasman%{away_pct} | {advice}"
    except: return ""

def football_prompt(match,stats,events,hf,af,hs,as_,inj_h=None,inj_a=None,h2h=None,standings=None,pred=None):
    home=match["teams"]["home"]["name"]; away=match["teams"]["away"]["name"]
    hid=match["teams"]["home"]["id"];   aid=match["teams"]["away"]["id"]
    h_g=match["goals"]["home"] if match["goals"]["home"] is not None else "-"
    a_g=match["goals"]["away"] if match["goals"]["away"] is not None else "-"
    sh=match["fixture"]["status"]["short"]; el=match["fixture"]["status"].get("elapsed","")
    league=match["league"]["name"]; country=match["league"]["country"]; season=match["league"]["season"]
    durum={"NS":"Başlamadı","1H":f"1.Yarı {el}'","HT":"Devre Arası",
           "2H":f"2.Yarı {el}'","FT":"Bitti","ET":f"Uzatma {el}'"}.get(sh,sh)
    NL="\n"
    sl=[]
    if stats and len(stats)>=2:
        h2={s["type"]:s["value"] for s in stats[0].get("statistics",[])}
        a2={s["type"]:s["value"] for s in stats[1].get("statistics",[])}
        for k in ["Ball Possession","Total Shots","Shots on Goal","Corner Kicks","Fouls","Yellow Cards"]:
            hv=h2.get(k,"-"); av=a2.get(k,"-")
            if hv not in [None,"-"] or av not in [None,"-"]: sl.append(f"  {k}: {hv or'-'}/{av or'-'}")
    el2=[]
    if events:
        for e in events[:10]:
            if e["type"] in ["Goal","Card"]:
                t=e.get("time",{}).get("elapsed","?")
                el2.append(f"  {t}' {e['team']['name']} – {e.get('player',{}).get('name','')} ({e.get('detail',e['type'])})")
    sb=("MAÇ İÇİ İSTATİSTİK:\n"+NL.join(sl)) if sl else ""
    eb=("OLAYLAR:\n"+NL.join(el2)) if el2 else ""
    return f"""Sen profesyonel bir futbol analisti ve bahis danışmanısın. Türkçe, özgüvenli yaz.

MAÇ: {country} – {league} ({season})
{home} vs {away} | Skor: {h_g}–{a_g} | Durum: {durum}
FORM: {home}: {form_str(hf,hid)} | {away}: {form_str(af,aid)}
SEZON: {season_str(hs,home)} / {season_str(as_,away)}
{sb}
{eb}

GÖREVİN:
1. 📊 MAÇ ANALİZİ – Hangi takım üstün, neden?
2. 🔮 TAHMİN – Kesin final skoru. MUTLAKA yaz: "Tahmin edilen skor: X-Y"
3. ⚡ KRİTİK FAKTÖR – Maçı belirleyecek tek unsur
4. 💡 EK BİLGİ – Derbi, puan durumu, sakatlık, haber

5. 🔮 1.YARI TAHMİNİ – İlk yarı skoru (örn: 1-0)

6-8 cümle. Özgüvenli yaz."""

def generic_prompt(sport_name,home,away,status,league):
    sl=sport_name.lower()
    is_basketball = any(w in sl for w in ["basket","nba"])
    is_hockey     = any(w in sl for w in ["hokey","hockey"])
    is_volleyball = "voleybol" in sl
    is_handball   = "hentbol" in sl
    is_mma        = "mma" in sl
    is_rugby      = "rugby" in sl
    is_f1         = "formula" in sl
    is_tennis     = "tenis" in sl

    if is_basketball:
        fmt="102-95"; detail="""3. 🔮 1.ÇEYREK TAHMİNİ – İlk çeyrek skoru (örn: 28-25)
4. 🔮 FİNAL TAHMİNİ – Mutlaka yaz: "Tahmin edilen skor: X-Y" (örn: 102-95)
5. ⚡ KRİTİK FAKTÖR – Maçı belirleyecek unsur (3 sayı isabeti, ribaund vb.)"""
    elif is_hockey:
        fmt="3-2"; detail="""3. 🔮 1.PERIYOT TAHMİNİ – İlk periyot skoru (örn: 1-0)
4. 🔮 FİNAL TAHMİNİ – Mutlaka yaz: "Tahmin edilen skor: X-Y" (örn: 3-2)
5. ⚡ KRİTİK FAKTÖR – Kaleci performansı, güç oyunu vb."""
    elif is_volleyball:
        fmt="3-1"; detail="""3. 🔮 İLK SET TAHMİNİ – İlk set kazananı ve tahmini set skoru (örn: 25-22)
4. 🔮 MAÇ TAHMİNİ – Mutlaka yaz: "Tahmin edilen skor: X-Y" (set sayısı, örn: 3-1)
5. ⚡ KRİTİK FAKTÖR – Servis, blok vb."""
    elif is_handball:
        fmt="28-25"; detail="""3. 🔮 1.YARI TAHMİNİ – İlk yarı skoru (örn: 14-12)
4. 🔮 FİNAL TAHMİNİ – Mutlaka yaz: "Tahmin edilen skor: X-Y" (örn: 28-25)
5. ⚡ KRİTİK FAKTÖR – Kaleci kurtarışları, hızlı hücum vb."""
    elif is_mma:
        fmt="Karar/TKO"; detail="""3. 🔮 KAZANAN TAHMİNİ – Kim kazanır ve nasıl? Mutlaka yaz: "Tahmin: [İsim] ([Yöntem])"
4. 🔮 ROUND TAHMİNİ – Kaçıncı roundda biter?
5. ⚡ KRİTİK FAKTÖR – Dövüş stili, güreş/vuruş üstünlüğü"""
    elif is_f1:
        fmt="Pole pozisyon / İlk 3"; detail="""3. 🔮 POLE POZİSYON TAHMİNİ – Kim pole alır?
4. 🔮 PODYUM TAHMİNİ – Mutlaka yaz: "Tahmin: 1.[İsim] 2.[İsim] 3.[İsim]"
5. ⚡ KRİTİK FAKTÖR – Sıralama hızı, pit stratejisi vb."""
    elif is_tennis:
        fmt="2-0 veya 2-1"; detail="""3. 🔮 KAZANAN TAHMİNİ – Kim kazanır? Mutlaka yaz: "Tahmin edilen skor: [İsim] 2-0 veya 2-1"
4. 🔮 İLK SET – İlk seti kim kazanır? (örn: 1.Set: 7-5)
5. ⚡ KRİTİK FAKTÖR – Kort yüzeyi, form, H2H geçmişi"""
    else:
        fmt="2-1"; detail="""3. 🔮 FİNAL TAHMİNİ – Mutlaka yaz: "Tahmin edilen skor: X-Y" (örn: {fmt})
4. ⚡ KRİTİK FAKTÖR – Sonucu belirleyecek unsur"""

    return f"""Sen profesyonel bir {sport_name} analisti ve bahis danışmanısın. Türkçe, özgüvenli yaz.

MAÇ: {league} | {home} vs {away} | Durum: {status}

GÖREVİN:
1. 📊 MAÇ ANALİZİ – Nasıl bir maç bekleniyor / gidiyor?
2. 💡 EK BİLGİ – Bu takımlar hakkında önemli bilgi
{detail}

5-7 cümle. Özgüvenli, kesin ve net yaz."""

def bulk_prompt(matches_info,sport_name):
    big=any(w in sport_name.lower() for w in ["basket","nba","hokey","hockey","voleybol"])
    fmt="88-95" if big else "2-1"
    NL="\n"
    lines=[f"{i}. {m['home']} vs {m['away']} ({m['league']}) | {m['status']}" for i,m in enumerate(matches_info,1)]
    return f"""Sen profesyonel bir {sport_name} analisti ve bahis danışmanısın.
Her maç için Türkçe kısa tahmin yaz.

MAÇLAR:
{NL.join(lines)}

Her maç için TAM OLARAK bu formatı kullan:
[numara]. [Ev] vs [Dep]
🔮 Tahmin edilen skor: X-Y (örn: {fmt})
💡 [1-2 cümle gerekçe]
---
Özgüvenli ve net yaz."""

def build_news_prompt(home, away, sport_name, league=""):
    """Güçlendirilmiş Gemini haber/sakat/form prompt."""
    today = datetime.now(TZ_TR).strftime("%d %B %Y")
    sl = sport_name.lower()
    is_basketball = any(w in sl for w in ["basket","nba"])
    is_football   = "futbol" in sl

    if is_basketball:
        focus = "sakatlık listesi (injury report), rotasyon, son 5 maç formu, back-to-back durumu"
    elif is_football:
        focus = "sakatlık/ceza listesi, 11 tahmini, son form, H2H geçmişi, teknik direktör açıklaması"
    else:
        focus = "sakatlık, form, son haberler"

    return f"""Bugün {today}. {league} liginde {home} - {away} ({sport_name}) maçı var.
Aşağıdaki konularda GÜNCEL bilgi ver ({focus}):

1. 🏥 {home} kadro/sakatlık durumu
2. 🏥 {away} kadro/sakatlık durumu  
3. 📊 Son form (her takım son 3 maç)
4. 🔑 Maçı belirleyecek kritik faktör

Kısa ve net, Türkçe yaz. Sadece güncel ve doğrulanmış bilgi kullan."""

def fetch_gemini_local_predictions(sport_name, date_str, league_filter=""):
    """Gemini ile yerel bahis sitelerinden tahmin çek."""
    today_tr = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d %B %Y")
    league_txt = f"{league_filter} ligi" if league_filter else sport_name
    prompt = f"""{today_tr} tarihindeki {league_txt} maçları için Türkiye'deki bahis sitelerinin (Misli, Nesine, Bilyoner, İddaa) 
ve uluslararası tahmin sitelerinin öngörülerini ara ve özetle.

Her maç için şu formatta ver:
Ev Takımı - Deplasman Takımı:
🏆 Favori: [takım veya beraberlik]
📈 Popüler bahis: [1, X, 2 veya üst/alt]
💡 [1 cümle gerekçe]

Sadece bugünkü {league_txt} maçlarını listele. Türkçe yaz."""
    return prompt

# ── PARSE ─────────────────────────────────────────────────────────
def parse(m,sk):
    try: home=m["teams"]["home"]["name"]
    except: home="?"
    try: away=m["teams"]["away"]["name"]
    except: away="?"
    try: hid=m["teams"]["home"]["id"]
    except: hid=0
    try: aid=m["teams"]["away"]["id"]
    except: aid=0
    sh=get_sh(m,sk)
    if sk=="football":
        elapsed=m["fixture"]["status"].get("elapsed"); mid=m["fixture"]["id"]
        league=m["league"]["name"]; country=m["league"]["country"]
        lid=m["league"]["id"]; season=m["league"]["season"]
        h_g=m["goals"]["home"] if m["goals"]["home"] is not None else "-"
        a_g=m["goals"]["away"] if m["goals"]["away"] is not None else "-"
        h_logo=m["teams"]["home"].get("logo","")
        a_logo=m["teams"]["away"].get("logo","")
    else:
        elapsed=None; mid=m.get("id",0)
        try: league=m.get("league",{}).get("name","") or m.get("competition",{}).get("name","")
        except: league=""
        try: country=m.get("country",{}).get("name","") or m.get("league",{}).get("country","")
        except: country=""
        try: lid=m.get("league",{}).get("id",0)
        except: lid=0
        season=None; h_g="-"; a_g="-"
        try:
            sc=m.get("scores",{})
            if sc and isinstance(sc,dict):
                hr=sc.get("home",{}); ar=sc.get("away",{})
                hv=(hr.get("total") if isinstance(hr,dict) else hr)
                av=(ar.get("total") if isinstance(ar,dict) else ar)
                h_g=str(hv) if hv is not None else "-"
                a_g=str(av) if av is not None else "-"
        except: pass
    ko=kickoff_tr(m,sk)
    st_txt={"NS":"Başlamadı","FT":"Bitti","1H":"1.Yarı","2H":"2.Yarı","HT":"Devre Arası",
            "Q1":"Q1","Q2":"Q2","Q3":"Q3","Q4":"Q4","OT":"OT",
            "After Penalties":"Penaltı","Finished":"Bitti","Not Started":"Başlamadı",
            "In Play":"Canlı","Retired":"Çekildi","Walkover":"WO"}.get(sh,sh)
    # Tennis: get scores
    if sk=="tennis":
        try:
            sc=m.get("scores",{})
            if sc:
                h_g=sc.get("home","–") or "–"
                a_g=sc.get("away","–") or "–"
        except: pass
        # Tennis league/tournament
        try:
            league=m.get("tournament",{}).get("name","") or league
            country=m.get("country",{}).get("name","") or country
        except: pass
    h_logo = m.get("teams",{}).get("home",{}).get("logo","") if sk=="football" else ""
    a_logo = m.get("teams",{}).get("away",{}).get("logo","") if sk=="football" else ""
    return dict(home=home,away=away,hid=hid,aid=aid,h_score=h_g,a_score=a_g,
                sh=sh,elapsed=elapsed,kickoff=ko,league=league,country=country,
                lid=lid,season=season,mid=mid,is_major=lid in MAJOR_IDS,
                status_txt=st_txt,raw=m,h_logo=h_logo,a_logo=a_logo)

def badge(sh,elapsed=None,kickoff=None):
    if sh in LIVE_SH:
        m=f" {elapsed}'" if elapsed else ""
        lbl="CANLI" if sh!="HT" else "DEVRE ARASI"
        return f'<span class="status-live">🔴 {lbl}{m}</span>'
    if sh in DONE_SH: return '<span class="status-finished">✅ Bitti</span>'
    if sh=="NS": return f'<span class="status-upcoming">🕐 {kickoff or "Başlamadı"}</span>'
    return f'<span class="status-upcoming">{sh}</span>'

def render_bar(label,hv,av):
    try:
        h=int(str(hv).replace("%","")) if hv not in [None,"-"] else 0
        a=int(str(av).replace("%","")) if av not in [None,"-"] else 0
        tot=h+a or 1; hp=int(h/tot*100)
    except: return
    st.markdown(f"""<div style='margin-bottom:9px'>
  <div style='display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px'>
    <b>{hv}</b><span style='opacity:.55'>{label}</span><b>{av}</b></div>
  <div style='display:flex;height:7px;border-radius:5px;overflow:hidden;background:rgba(128,128,128,.15)'>
    <div style='width:{hp}%;background:#4e8cff'></div>
    <div style='width:{100-hp}%;background:#ff6b6b'></div></div></div>""",unsafe_allow_html=True)

def estimate_tokens(text):
    """Yaklaşık token sayısı (1 token ≈ 4 karakter)"""
    return len(text) // 4

def logo_html(url):
    """Takım logosu <img> döndürür; URL yoksa boş span."""
    if url:
        return f'<img src="{url}" style="width:20px;height:20px;object-fit:contain;vertical-align:middle;margin:0 3px;border-radius:3px" onerror="this.style.display=\'none\'">'
    return '<span style="display:inline-block;width:20px;height:20px;vertical-align:middle;margin:0 3px"></span>'

def show_ai(text,err,p,model_name,sname=None,show_tokens=True):
    if err: st.error(err); return
    if not text: return
    sname = sname or ""
    pred=extract_pred(text,sname)
    sub_pred = extract_sub_pred(text, sname)
    if pred:
        sub_items = "".join([f'<span style="font-size:12px;background:rgba(34,197,94,.15);padding:2px 8px;border-radius:8px;margin:2px">{k}: <b>{v}</b></span>' for k,v in sub_pred.items()]) if sub_pred else ""
        sub_div = f'<div style="margin-top:6px">{sub_items}</div>' if sub_items else ""
        st.markdown(f'<div class="pred-box"><div class="pred-label">🔮 TAHMİN EDİLEN SKOR</div><div class="pred-score">{pred}</div><div class="pred-label">{p["home"]} – {p["away"]}</div>{sub_div}</div>', unsafe_allow_html=True)
    tokens=estimate_tokens(text)
    token_info=f' <span style="font-size:11px;opacity:.5">~{tokens} token</span>' if show_tokens else ""
    st.markdown(f'<div class="ai-box">🤖 <b>{model_name}</b>{token_info}<br><br>{text}</div>',unsafe_allow_html=True)
    # Save to history

    st.session_state.analysis_history.append({
        "time": dt_module.datetime.now(TZ_TR).strftime("%H:%M"),
        "sport": sname,
        "home": p["home"], "away": p["away"],
        "league": p.get("league",""),
        "model": model_name,
        "pred": pred or "?",
        "sub_pred": sub_pred,
        "text": text,
        "tokens": tokens
    })

def compare_all_models(prompt,p,_sport_name=""):
    """Tüm modelleri paralel çalıştır ve yan yana göster"""
    models=list(AI_MODELS.keys())
    results={}
    progress=st.progress(0,text="Modeller analiz yapıyor...")
    for i,model_name in enumerate(models):
        progress.progress((i)/len(models),text=f"{model_name} analiz yapıyor...")
        text,err=run_ai(prompt,model_name)
        results[model_name]={"text":text,"err":err}
    progress.progress(1.0,text="Tamamlandı!")
    time.sleep(0.3); progress.empty()

    # Tahminleri üstte özet göster
    st.markdown("### 🔮 Model Tahminleri")
    pred_cols=st.columns(len(models))
    for i,(model_name,res) in enumerate(results.items()):
        with pred_cols[i]:
            pred=extract_pred(res["text"],_sport_name) if res["text"] else None
            sub=extract_sub_pred(res["text"],_sport_name) if res["text"] else {}
            color={"groq":"#EF9F27","gemini":"#22c55e","gpt":"#378ADD","deepseek":"#E24B4A"}.get(AI_MODELS[model_name]["id"],"#888")
            short_name=" ".join(model_name.split()[:2])
            sub_lines = "".join([
                f'<div style="font-size:11px;color:{color};font-weight:600;margin-top:4px;'
                f'background:rgba(128,128,128,.08);border-radius:6px;padding:2px 6px;'
                f'white-space:nowrap">{k}: {v}</div>'
                for k,v in sub.items() if k and v
            ]) if sub else ""
            if pred:
                st.markdown(
                    f'<div style="border:2px solid {color};border-radius:10px;padding:10px 8px;'
                    f'text-align:center;margin-bottom:8px">'
                    f'<div style="font-size:10px;opacity:.6;margin-bottom:4px">{short_name}</div>'
                    f'<div style="font-size:22px;font-weight:900;color:{color};white-space:nowrap;'
                    f'letter-spacing:.5px">{pred}</div>'
                    f'{sub_lines}'
                    f'</div>',
                    unsafe_allow_html=True
                )
            elif res["err"]:
                # Hatanın ilk 40 karakterini göster
                err_short = str(res["err"])[:40].replace("⚠️","").strip()
                st.markdown(f"""<div style="border:1px solid #f87171;border-radius:10px;padding:8px;text-align:center">
                    <div style="font-size:10px;opacity:.6">{short_name}</div>
                    <div style="font-size:10px;color:#f87171;margin-top:2px">{err_short}</div>
                </div>""",unsafe_allow_html=True)
            else:
                st.markdown(f"""<div style="border:1px solid {color};border-radius:10px;padding:10px;text-align:center">
                    <div style="font-size:10px;opacity:.6">{short_name}</div>
                    <div style="font-size:18px;font-weight:700;color:{color}">?</div>
                </div>""",unsafe_allow_html=True)

    # Konsensüs özeti
    consensus = extract_consensus(results, _sport_name)
    if consensus:
        st.markdown("### 🤝 Ortak Tahminler")
        cols = st.columns(len(consensus))
        for i, (key, (label, detail)) in enumerate(consensus.items()):
            with cols[i]:
                st.markdown(f'''<div style="background:var(--color-background-secondary);border-radius:10px;padding:10px;text-align:center">
                    <div style="font-size:13px;font-weight:500">{label}</div>
                    <div style="font-size:11px;opacity:.7;margin-top:4px">{detail}</div>
                </div>''', unsafe_allow_html=True)

    # Save to history (always)

    for model_name,res in results.items():
        if res.get("text") and not res.get("err"):
            pred=extract_pred(res["text"],_sport_name)
            tokens=estimate_tokens(res["text"])
            st.session_state.analysis_history.append({
                "time": dt_module.datetime.now(TZ_TR).strftime("%H:%M"),
                "sport": _sport_name,
                "home": p["home"], "away": p["away"],
                "league": p.get("league",""),
                "model": model_name,
                "pred": pred or "?",
                "text": res["text"],
                "tokens": tokens,
                "sub_pred": extract_sub_pred(res["text"],_sport_name)
            })

# ── SIDEBAR ───────────────────────────────────────────────────────
with st.sidebar:
    st.title("🏟️ Canlı Skor + AI")
    st.markdown("---")
    if "sport_name" not in st.session_state:
        st.session_state.sport_name = list(SPORT_CONFIG.keys())[0]
    sport_name = st.selectbox("Branş", list(SPORT_CONFIG.keys()), 
                              index=list(SPORT_CONFIG.keys()).index(st.session_state.sport_name))
    st.session_state.sport_name = sport_name
    cfg=SPORT_CONFIG[sport_name]
    sel_date=st.date_input("📅 Tarih",value=date.today())
    date_str=sel_date.strftime("%Y-%m-%d")

    st.markdown("---")
    st.subheader("🤖 AI Model")
    ai_model=st.radio("",list(AI_MODELS.keys()))
    cost=AI_MODELS[ai_model]["cost"]
    st.caption(f"Tahmini maliyet: {cost}")

    # Key durumu göster
    mid=AI_MODELS[ai_model]["id"]
    key_map={"groq":GROQ_KEY,"gemini":GEMINI_KEY,"gpt":OPENAI_KEY,"deepseek":DEEPSEEK_KEY}
    key_var={"groq":"GROQ_API_KEY","gemini":"GEMINI_API_KEY","gpt":"OPENAI_API_KEY","deepseek":"DEEPSEEK_API_KEY"}
    if key_map.get(mid,""):
        st.success(f"✓ Key mevcut")
    else:
        st.warning(f"⚠️ .env → {key_var.get(mid,'')}")

    st.markdown("---")
    search=st.text_input("🔍 Takım ara","")
    bulk_mode=st.checkbox("☑️ Toplu seçim modu")
    st.markdown("---")
    if st.button("🔃 Yenile",use_container_width=True):
        st.cache_data.clear()
        st.session_state.bulk_results={}
        st.session_state.selected=set()
        st.session_state.live_loaded=False
        st.session_state.live_data=[]
        st.rerun()
    st.caption("API-Sports ücretsiz\n100 istek/gün/branş")

# ── BRANŞ SEÇİCİ ─────────────────────────────────────────────────
sport_list = list(SPORT_CONFIG.keys())
sport_labels = [f"{SPORT_CONFIG[s]['emoji']} {s.split()[-1]}" for s in sport_list]
_sel_idx = sport_list.index(sport_name) if sport_name in sport_list else 0
_new_sport_label = st.selectbox("", sport_labels, index=_sel_idx,
                                label_visibility="collapsed", key="sport_dd")
_new_sport = sport_list[sport_labels.index(_new_sport_label)]
if _new_sport != sport_name:
    st.session_state.sport_name = _new_sport
    st.rerun()

if not API_KEY or "buraya" in API_KEY:
    st.error("⚠️ `.env` dosyasına `API_SPORTS_KEY` ekle."); st.stop()

# ── MAÇ DETAY EKRANI (aktifse tüm sayfayı kaplar) ────────────────
if st.session_state.get("detail_match"):
    dm = st.session_state.detail_match
    p  = dm["p"]
    mk = str(p["mid"])

    # Geri butonu
    if st.button("← Geri", key="detail_back"):
        st.session_state.detail_match = None
        st.rerun()

    # Başlık
    h_logo_d = logo_html(p.get("h_logo","")) if cfg["key"]=="football" else ""
    a_logo_d = logo_html(p.get("a_logo","")) if cfg["key"]=="football" else ""
    score_col_d = "#ff4444" if p["sh"] in LIVE_SH else "var(--color-text-primary)"
    st.markdown(f"""
    <div style="text-align:center;padding:16px 0 8px">
      <div style="font-size:12px;opacity:.5;margin-bottom:6px">{p.get('league','')} · {p.get('status_txt','')}</div>
      <div style="display:flex;align-items:center;justify-content:center;gap:12px">
        <div style="font-size:18px;font-weight:700;text-align:right;flex:1">{p['home']}{h_logo_d}</div>
        <div style="font-size:26px;font-weight:900;color:{score_col_d};white-space:nowrap;min-width:70px;text-align:center">{p['h_score']}–{p['a_score']}</div>
        <div style="font-size:18px;font-weight:700;text-align:left;flex:1">{a_logo_d}{p['away']}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Önceki tahminler varsa göster
    hist_for_match = [h for h in st.session_state.analysis_history
                      if h.get("home")==p["home"] and h.get("away")==p["away"]]
    if hist_for_match:
        st.markdown("#### 🔮 Önceki Tahminler")
        MODEL_COLORS_D = {"🟡 Groq – Llama 3.3":"#EF9F27","🟢 Gemini 2.5 Flash":"#22c55e","⚪ GPT-4o Mini":"#378ADD","🔴 DeepSeek V3":"#E24B4A"}
        MODEL_SHORT_D  = {"🟡 Groq – Llama 3.3":"Groq","🟢 Gemini 2.5 Flash":"Gemini","⚪ GPT-4o Mini":"GPT","🔴 DeepSeek V3":"DeepSeek"}
        pc = st.columns(len(hist_for_match))
        for i,h in enumerate(hist_for_match):
            c = MODEL_COLORS_D.get(h["model"],"#888")
            sn = MODEL_SHORT_D.get(h["model"], h["model"].split()[0])
            sub = h.get("sub_pred",{})
            sub_html = "".join([f'<div style="font-size:10px;color:{c};font-weight:600;white-space:nowrap">{k}: {v}</div>' for k,v in sub.items()])
            with pc[i]:
                st.markdown(f'<div style="border:2px solid {c};border-radius:10px;padding:8px;text-align:center"><div style="font-size:10px;opacity:.6">{sn}</div><div style="font-size:20px;font-weight:900;color:{c};white-space:nowrap">{h.get("pred","?")}</div>{sub_html}<div style="font-size:9px;opacity:.4;margin-top:2px">{h["time"]}</div></div>', unsafe_allow_html=True)
        st.markdown("---")

    # Analiz butonları
    st.markdown("#### 🤖 Yeni Analiz")
    da1, da2, da3 = st.columns(3)
    with da1:
        if st.button("🤖 Analiz", key=f"d_single_{mk}", use_container_width=True):
            st.session_state[f"d_run_{mk}"] = "single"
    with da2:
        if st.button("⚡ 4 Model", key=f"d_cmp_{mk}", use_container_width=True):
            st.session_state[f"d_run_{mk}"] = "compare"
    with da3:
        if st.button("🌐+⚡", key=f"d_ws_{mk}", use_container_width=True):
            st.session_state[f"d_run_{mk}"] = "web_compare"

    if st.session_state.get(f"d_run_{mk}"):
        run_t = st.session_state.pop(f"d_run_{mk}")
        with st.spinner("Analiz yapılıyor..."):
            if cfg["key"]=="football":
                sd  = fetch_stats(p["mid"]) if p["sh"]!="NS" else []
                ed  = fetch_events(p["mid"]) if p["sh"]!="NS" else []
                hf  = fetch_form(p["hid"],p["lid"],p["season"])
                af  = fetch_form(p["aid"],p["lid"],p["season"])
                hs  = fetch_tstat(p["hid"],p["lid"],p["season"])
                as_ = fetch_tstat(p["aid"],p["lid"],p["season"])
                inj_h = fetch_injuries(p["hid"],p["season"])
                inj_a = fetch_injuries(p["aid"],p["season"])
                h2hd  = fetch_h2h(p["hid"],p["aid"])
                stand = fetch_standings(p["lid"],p["season"])
                pred_api = fetch_predictions(p["mid"])
                # raw maçı bul
                _all_raw = pre_raw + st.session_state.live_data
                raw = next((m for m in _all_raw if m["fixture"]["id"]==p["mid"]), None)
                d_prompt = football_prompt(raw,sd,ed,hf,af,hs,as_,inj_h,inj_a,h2hd,stand,pred_api) if raw else generic_prompt(sport_name,p["home"],p["away"],p["status_txt"],p["league"])
            else:
                d_prompt = generic_prompt(sport_name,p["home"],p["away"],p["status_txt"],p["league"])

            if run_t in ["web_compare","web_single"] and GEMINI_KEY:
                nk = f"news_{mk}"
                if nk not in st.session_state:
                    nt,_ = call_gemini(build_news_prompt(p["home"],p["away"],sport_name,p.get("league","")), use_search=True)
                    st.session_state[nk] = nt or ""
                if st.session_state.get(nk):
                    st.markdown(f'<div class="news-box">🌐 <b>Güncel:</b><br>{st.session_state[nk]}</div>', unsafe_allow_html=True)
                    d_prompt += f"\n\nGÜNCEL:\n{st.session_state[nk]}"

        if run_t == "single":
            text,err = run_ai(d_prompt, ai_model)
            show_ai(text, err, p, ai_model, sname=sport_name)
        else:
            compare_all_models(d_prompt, p, _sport_name=sport_name)

    # Futbol istatistikleri
    if cfg["key"]=="football" and p["sh"] not in WAIT_SH:
        st.markdown("---")
        st.markdown("#### 📈 İstatistikler")
        with st.spinner("Yükleniyor..."):
            stats_d = fetch_stats(p["mid"])
        if stats_d and len(stats_d)>=2:
            h2s = {s["type"]:s["value"] for s in stats_d[0].get("statistics",[])}
            a2s = {s["type"]:s["value"] for s in stats_d[1].get("statistics",[])}
            for k in ["Ball Possession","Total Shots","Shots on Goal","Corner Kicks","Fouls","Yellow Cards"]:
                hv=h2s.get(k,"-"); av=a2s.get(k,"-")
                if hv not in [None,"-"] or av not in [None,"-"]: render_bar(k,hv or"-",av or"-")

    st.stop()  # Detay ekranı aktifken geri kalanı render etme

# Country filter (populated after data loads)
country_filter_key = f"country_filter_{sport_name}"
if country_filter_key not in st.session_state:
    st.session_state[country_filter_key] = "Hepsi"

# ── VERİ: MAÇ ÖNCESİ (günlük cache) ─────────────────────────────
with st.spinner("Maç öncesi liste yükleniyor..."):
    pre_raw, cache_ts = fetch_prematch_cached(cfg["key"],cfg["base"],date_str,API_KEY)

# Gemini fallback if no matches found
if not pre_raw and GEMINI_KEY:
    cache_key = f"{sport_name}_{date_str}"
    cached_matches = st.session_state.gemini_fallback.get(cache_key)

    if not cached_matches:
        st.warning(f"⚠️ API'den {sport_name} maçı gelmedi. Gemini ile çekebilirsiniz.")
        if st.button(f"🌐 Gemini ile Bugünkü {sport_name} Maçlarını Çek", key="gemini_fallback_btn"):
            with st.spinner("Gemini maç listesi arıyor..."):
                # Build sport-specific prompt
                is_tennis_fb = "tenis" in sport_name.lower() or "tennis" in sport_name.lower()
                if is_tennis_fb:
                    fallback_prompt = f"""{date_str} tarihindeki TÜM tenis maçlarını JSON formatında listele.
ATP, WTA, ITF, Challenger, Grand Slam tüm turnuvalar dahil.
Her oyuncu için tam isim yaz.
Yanıt SADECE JSON array, başka metin YOK:
[
  {{"home": "Oyuncu A", "away": "Oyuncu B", "league": "ATP Monte-Carlo", "country": "Monako", "time": "14:00"}},
  ...
]
En az 50 maç listele."""
                else:
                    fallback_prompt = f"""{date_str} tarihindeki TÜM {sport_name} maçlarını JSON formatında listele.
MUTLAKA şu ligleri dahil et (eksiksiz):
- Türkiye: Süper Lig, 1.Lig, 2.Lig
- İngiltere: Premier League, Championship, League One
- İspanya: La Liga, La Liga 2
- İtalya: Serie A, Serie B
- Almanya: Bundesliga, 2.Bundesliga
- Fransa: Ligue 1, Ligue 2
- Hollanda: Eredivisie
- Portekiz: Primeira Liga
- Belçika: Jupiler Pro League
- İskoçya: Scottish Premiership
- Yunanistan: Super League
- Çek Cumhuriyeti: Czech Liga
- Polonya: Ekstraklasa
- İsveç: Allsvenskan
- Norveç: Eliteserien
- Danimarka: Superliga
- UEFA: Champions League, Europa League, Conference League
- Diğer tüm ülkelerin ligleri

Yanıt SADECE JSON array, başka metin YOK:
[
  {{"home": "Takım A", "away": "Takım B", "league": "Lig", "country": "Ülke", "time": "20:00"}},
  ...
]
En az 80 maç listele."""
                fallback_text, fallback_err = call_gemini(fallback_prompt, use_search=True)
            if fallback_err:
                st.error(fallback_err)
            elif fallback_text:
                import json
                try:
                    import json as _json
                    clean = fallback_text.strip()
                    # Remove markdown code blocks
                    for tag in ["```json", "```JSON", "```"]:
                        clean = clean.replace(tag, "")
                    clean = clean.strip()
                    # Find [ ... ] 
                    start = clean.find("[")
                    end = clean.rfind("]") + 1
                    if start >= 0 and end > start:
                        clean = clean[start:end]
                    matches = _json.loads(clean)
                    st.session_state.gemini_fallback[cache_key] = matches
                    st.rerun()
                except Exception as _e:
                    st.error(f"Parse hatası: {_e}")
                    st.code(fallback_text[:800])
    else:
        st.info(f"🌐 Gemini ile çekildi — {len(cached_matches)} maç (cache'den)")
        if st.button("🔄 Yenile", key="gemini_refresh"):
            del st.session_state.gemini_fallback[cache_key]
            st.rerun()

        # Show as match cards
        if search:
            q = search.lower()
            cached_matches = [m for m in cached_matches if q in (m.get("home","")+" "+m.get("away","")).lower()]

        st.markdown(f'<div style="font-size:12px;opacity:.5;margin:4px 0">{cfg["emoji"]} {len(cached_matches)} maç</div>', unsafe_allow_html=True)
        
        # Group by league
        from collections import defaultdict as _dd
        _league_groups = _dd(list)
        for _gm in cached_matches:
            _league_groups[_gm.get("league","Diğer")].append(_gm)
        
        # Sort: major leagues first
        _major = ["Süper Lig","Premier League","La Liga","Serie A","Bundesliga","Ligue 1",
                  "Champions League","Europa League","Conference League","NBA","Euroleague",
                  "ATP","WTA","Grand Slam"]
        def _league_sort(l):
            for i,m in enumerate(_major):
                if m.lower() in l.lower(): return i
            return 99
        _sorted_leagues = sorted(_league_groups.keys(), key=_league_sort)
        
        _flat_matches = []
        for _lg in _sorted_leagues:
            _flat_matches.extend(_league_groups[_lg])
        
        i = 0
        for i, gm in enumerate(_flat_matches):
            mid_fake = f"gem_{i}"
            home = gm.get("home","?"); away = gm.get("away","?")
            league = gm.get("league",""); country = gm.get("country",""); kt = gm.get("time","")
            league_short = league[:20]+"…" if len(league)>20 else league

            # Compact one-line match row
            st.markdown(f'''<div style="display:flex;align-items:center;gap:6px;padding:8px 2px;border-bottom:0.5px solid rgba(128,128,128,.1)">
                <div style="font-size:10px;color:var(--color-text-tertiary);white-space:nowrap;min-width:45px;overflow:hidden">{league_short}</div>
                <div style="flex:1;text-align:right;font-size:14px;font-weight:600">{home}</div>
                <div style="min-width:40px;text-align:center;font-size:13px;opacity:.4;white-space:nowrap">– –</div>
                <div style="flex:1;font-size:14px;font-weight:600">{away}</div>
                <div style="font-size:11px;color:#3b82f6;white-space:nowrap">{kt}</div>
            </div>''', unsafe_allow_html=True)

            # Checkbox
            checked = st.checkbox("seç", key=f"chk_{mid_fake}", value=(mid_fake in st.session_state.selected), label_visibility="collapsed")
            if checked: st.session_state.selected.add(mid_fake)
            else: st.session_state.selected.discard(mid_fake)

            # Quick buttons compact
            _fb1, _fb2, _fb3 = st.columns([2,2,1])
            with _fb1:
                if st.button("🤖 Analiz", key=f"ai_{mid_fake}", use_container_width=True):
                    st.session_state[f"qr_{mid_fake}"] = "single"
            with _fb2:
                if st.button("⚡ 4 Model", key=f"cmp_{mid_fake}", use_container_width=True):
                    st.session_state[f"qr_{mid_fake}"] = "compare"
            with _fb3:
                if st.button("🌐", key=f"ws_{mid_fake}", use_container_width=True):
                    st.session_state[f"qr_{mid_fake}"] = "web_compare"

            if st.session_state.get(f"qr_{mid_fake}"):
                run_t = st.session_state.pop(f"qr_{mid_fake}")
                p_fake = {"home":home,"away":away,"league":league,"mid":mid_fake,"sh":"NS"}
                prompt = generic_prompt(sport_name, home, away, "Başlamadı", league)
                if run_t == "web_compare" and GEMINI_KEY:
                    nk = f"news_gem_{i}"
                    if nk not in st.session_state:
                        news_t, _ = call_gemini(build_news_prompt(home, away, sport_name, league), use_search=True)
                        st.session_state[nk] = news_t or ""
                    if st.session_state.get(nk):
                        prompt += f"\n\nGÜNCEL:\n{st.session_state[nk]}"
                    with st.spinner("Analiz..."):
                        if run_t in ["single","web_compare"] and run_t != "compare":
                            text, err = run_ai(prompt, ai_model)
                        else:
                            text, err = None, None
                    if run_t not in ["compare","web_compare"]:
                        if text and not err:
                            pred = extract_pred(text, sport_name)
                            sub = extract_sub_pred(text, sport_name)
                            sub_html = "".join([f'<div style="font-size:11px;opacity:.7">{k}: {v}</div>' for k,v in sub.items()]) if sub else ""
                            if pred:
                                st.markdown(f'<div class="pred-box"><div class="pred-label">🔮 TAHMİN</div><div class="pred-score">{pred}</div><div class="pred-label">{home} – {away}</div>{sub_html}</div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="ai-box">{text}</div>', unsafe_allow_html=True)
                        elif err: st.error(err)
                    else:
                        compare_all_models(prompt, p_fake, _sport_name=sport_name)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        i += 1

if cache_ts:
    st.markdown(f'<span class="cache-info">📦 Maç öncesi liste bugün {cache_ts}\'de çekildi — gün boyunca sabit kalır</span>', unsafe_allow_html=True)

pre_all=[parse(m,cfg["key"]) for m in pre_raw]

# Auto-supplement with Gemini if API has few matches
if len(pre_all) < 15 and GEMINI_KEY and cfg["key"] != "tennis":
    supp_key = f"supp_{sport_name}_{date_str}"
    if supp_key not in st.session_state:
        st.session_state[supp_key] = None
    if st.session_state[supp_key] is None:
        if st.button(f"🌐 Gemini ile {sport_name} maçlarını tamamla ({len(pre_all)} maç az geldi)", key="supp_btn"):
            with st.spinner("Gemini ek maçlar arıyor..."):
                existing = [(p["home"]+" "+p["away"]).lower() for p in pre_all]
                supp_prompt = f"""{date_str} tarihindeki {sport_name} maçlarını JSON listele. Sadece şu takımları ALMA (zaten var): {", ".join(existing[:10])}
TÜM ligleri dahil et, en az 60 maç. SADECE JSON array:
[{{"home":"A","away":"B","league":"L","country":"C","time":"20:00"}},...] """
                supp_text, supp_err = call_gemini(supp_prompt, use_search=True)
            if supp_text and not supp_err:
                import json as _j
                try:
                    clean = supp_text.strip()
                    for t in ["```json","```JSON","```"]: clean=clean.replace(t,"")
                    s = clean.find("["); e = clean.rfind("]")+1
                    if s>=0 and e>s: clean=clean[s:e]
                    st.session_state[supp_key] = _j.loads(clean)
                    st.rerun()
                except: st.session_state[supp_key] = []

if search:
    q=search.lower()
    pre_all=[p for p in pre_all if q in (p["home"]+" "+p["away"]).lower()]

# Country filter
all_countries = sorted(set(p.get("country","") for p in pre_all if p.get("country","")))
if all_countries:
    major_countries = ["Türkiye","England","Spain","Italy","Germany","France","Netherlands","Portugal","Belgium","Scotland","Greece","UEFA"]
    ordered = ["Hepsi"] + [c for c in major_countries if c in all_countries] + [c for c in all_countries if c not in major_countries and c not in ["Hepsi"]]
    
    # Horizontal scrollable country filter
    country_icons = {"Türkiye":"🇹🇷","England":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","Spain":"🇪🇸","Italy":"🇮🇹","Germany":"🇩🇪","France":"🇫🇷",
                     "Netherlands":"🇳🇱","Portugal":"🇵🇹","Belgium":"🇧🇪","Scotland":"🏴󠁧󠁢󠁳󠁣󠁴󠁿","Greece":"🇬🇷","UEFA":"🇪🇺",
                     "USA":"🇺🇸","Brazil":"🇧🇷","Argentina":"🇦🇷","Russia":"🇷🇺","Ukraine":"🇺🇦","Poland":"🇵🇱",
                     "Czech Republic":"🇨🇿","Sweden":"🇸🇪","Norway":"🇳🇴","Denmark":"🇩🇰","Switzerland":"🇨🇭"}
    
    sel_country = st.session_state.get(country_filter_key, "Hepsi")
    _c_idx = ordered.index(sel_country) if sel_country in ordered else 0
    _new_c = st.selectbox("Ülke", ordered, index=_c_idx,
                          label_visibility="collapsed", key=f"cdd_{sport_name}")
    if _new_c != sel_country:
        st.session_state[country_filter_key] = _new_c
        st.rerun()
    if sel_country != "Hepsi":
        pre_all = [p for p in pre_all if p.get("country","") == sel_country]

pre_major=[p for p in pre_all if p["is_major"]]
pre_minor=[p for p in pre_all if not p["is_major"]]

# ── ÖZET ─────────────────────────────────────────────────────────
live_parsed=[parse(m,cfg["key"]) for m in st.session_state.live_data]
live_now_count=len([p for p in live_parsed if p["sh"] in LIVE_SH])

done_count = len([p for p in live_parsed if p["sh"] in DONE_SH])
total = len(pre_all)+len(live_parsed)
st.markdown(f'<div style="font-size:12px;opacity:.6;margin:4px 0 8px">🕐 {len(pre_all)} maç öncesi &nbsp;·&nbsp; 🔴 {live_now_count} canlı &nbsp;·&nbsp; ✅ {done_count} bitti</div>', unsafe_allow_html=True)

# ── TOPLU ANALİZ BARI ─────────────────────────────────────────────
all_p=pre_all+live_parsed
sel_count=len(st.session_state.selected)
if sel_count:
    bar_cols=st.columns([4,3,2])
    with bar_cols[0]:
        st.markdown(f'<span style="font-size:13px">☑️ {sel_count} seçili</span>', unsafe_allow_html=True)
    with bar_cols[1]:
        if st.button("🤖 Toplu Analiz",type="primary",use_container_width=True):
            selected_p=[p for p in all_p if str(p["mid"]) in st.session_state.selected]
            mi=[{"home":p["home"],"away":p["away"],"h_score":p["h_score"],
                 "a_score":p["a_score"],"league":p["league"],"status":p["status_txt"]} for p in selected_p]
            prompt=bulk_prompt(mi,sport_name)
            with st.spinner(f"{len(selected_p)} maç analiz ediliyor..."):
                text,err=run_ai(prompt,ai_model)
            if err: st.error(err)
            elif text:
                st.success("✅ Tamamlandı!")
                blocks=re.split(r'\n(?=\d+\.)',text.strip())
                for i,p in enumerate(selected_p):
                    mk=str(p["mid"])
                    st.session_state.bulk_results[mk]=blocks[i].strip() if i<len(blocks) else text
                st.rerun()
    with bar_cols[2]:
        if st.button("🗑️",use_container_width=True):
            st.session_state.selected=set(); st.rerun()

st.markdown("---")

# ── MAÇ KARTI ────────────────────────────────────────────────────
is_football=cfg["key"]=="football"

def match_card(p,raw_list):
    mk=str(p["mid"])
    is_live_now=p["sh"] in LIVE_SH

    score_col = "#ff4444" if is_live_now else "var(--color-text-primary)"
    ko = p.get("kickoff","")
    elapsed = p.get("elapsed")
    sh = p.get("sh","")
    if sh in LIVE_SH and elapsed:
        time_badge = f'<span style="color:#ff4444;font-weight:700;font-size:12px">{elapsed}\'</span>'
    elif sh in DONE_SH:
        time_badge = '<span style="color:#888;font-size:11px">Bitti</span>'
    elif ko:
        time_badge = f'<span style="color:#3b82f6;font-size:13px;font-weight:600">{ko}</span>'
    else:
        time_badge = ""
    
    league_short = p["league"][:18] + ("…" if len(p["league"])>18 else "")

    # Takım logoları (sadece futbol)
    h_logo = logo_html(p.get("h_logo","")) if is_football else ""
    a_logo = logo_html(p.get("a_logo","")) if is_football else ""

    st.markdown(f"""<div style="display:flex;align-items:center;gap:4px;padding:10px 2px;border-bottom:0.5px solid rgba(128,128,128,.1)">
        <div style="font-size:10px;color:var(--color-text-tertiary);white-space:nowrap;min-width:50px;max-width:70px;overflow:hidden;text-overflow:ellipsis">{league_short}</div>
        <div style="flex:1;text-align:right;font-size:14px;font-weight:700;line-height:1.2">{p["home"]}{h_logo}</div>
        <div style="min-width:60px;text-align:center;font-size:15px;font-weight:700;color:{score_col};white-space:nowrap">{p["h_score"]}–{p["a_score"]}</div>
        <div style="flex:1;font-size:14px;font-weight:700;line-height:1.2">{a_logo}{p["away"]}</div>
        <div style="min-width:40px;text-align:right">{time_badge}</div>
    </div>""", unsafe_allow_html=True)

    # Detay butonu — maça gir
    if st.button("🔍", key=f"detail_{mk}", help="Maç detayına git"):
        st.session_state.detail_match = {"p": p, "raw_list_key": mk}
        st.rerun()
    
    checked=st.checkbox("seç",key=f"chk_{mk}",value=(mk in st.session_state.selected),label_visibility="collapsed")
    if checked: st.session_state.selected.add(mk)
    else: st.session_state.selected.discard(mk)

    if mk in st.session_state.bulk_results:
        res=st.session_state.bulk_results[mk]
        pred=extract_pred(res,sport_name)
        if pred:
            st.markdown(f"""<div class="pred-box">
                <div class="pred-label">🔮 TAHMİN (Toplu)</div>
                <div class="pred-score">{pred}</div>
                <div class="pred-label">{p['home']} – {p['away']}</div>
            </div>""",unsafe_allow_html=True)
        st.markdown(f'<div class="bulk-result">{res}</div>',unsafe_allow_html=True)

    # Hızlı aksiyon butonları — 3 eşit sütun, mobilde yan yana
    _qc1, _qc2, _qc3 = st.columns(3)
    with _qc1:
        if st.button("🤖 Analiz", key=f"quick_{mk}", use_container_width=True):
            st.session_state[f"quick_run_{mk}"] = "single"
    with _qc2:
        if st.button("⚡ 4 Model", key=f"quickcmp_{mk}", use_container_width=True):
            st.session_state[f"quick_run_{mk}"] = "compare"
    with _qc3:
        if st.button("🌐+⚡", key=f"quickws_{mk}", use_container_width=True):
            st.session_state[f"quick_run_{mk}"] = "web_compare"

    # Show stored quick analysis results
    qres_key = f"qres_{mk}"
    qtype_key = f"qtype_{mk}"
    if st.session_state.get(qres_key):
        qr = st.session_state[qres_key]
        qt = st.session_state.get(qtype_key, "single")
        if qt == "single":
            show_ai(qr.get("text"), qr.get("err"), p, qr.get("model", ai_model), sname=sport_name)
        # compare results shown inline already

    # Run quick analysis if triggered
    if st.session_state.get(f"quick_run_{mk}"):
        run_type = st.session_state.pop(f"quick_run_{mk}")
        with st.spinner("Analiz yapılıyor..."):
            if is_football:
                sd = fetch_stats(p["mid"]) if p["sh"]!="NS" else []
                ed = fetch_events(p["mid"]) if p["sh"]!="NS" else []
                hf = fetch_form(p["hid"],p["lid"],p["season"])
                af = fetch_form(p["aid"],p["lid"],p["season"])
                hs = fetch_tstat(p["hid"],p["lid"],p["season"])
                as_ = fetch_tstat(p["aid"],p["lid"],p["season"])
                inj_h = fetch_injuries(p["hid"],p["season"])
                inj_a = fetch_injuries(p["aid"],p["season"])
                h2h = fetch_h2h(p["hid"],p["aid"])
                stand = fetch_standings(p["lid"],p["season"])
                pred_api = fetch_predictions(p["mid"])
                raw = next((m for m in raw_list if m["fixture"]["id"]==p["mid"]),None)
                q_prompt = football_prompt(raw,sd,ed,hf,af,hs,as_,inj_h,inj_a,h2h,stand,pred_api) if raw else generic_prompt(sport_name,p["home"],p["away"],p["status_txt"],p["league"])
            else:
                q_prompt = generic_prompt(sport_name,p["home"],p["away"],p["status_txt"],p["league"])

            if run_type in ["web_compare","web_single"] and GEMINI_KEY:
                news_k = f"news_{mk}"
                if news_k not in st.session_state:
                    news_t, _ = call_gemini(build_news_prompt(p['home'], p['away'], sport_name, p.get('league','')), use_search=True)
                    st.session_state[news_k] = news_t or ""
                if st.session_state.get(news_k):
                    q_prompt += f"\n\nGÜNCEL:\n{st.session_state[news_k]}"

            if run_type == "single":
                text, err = run_ai(q_prompt, ai_model)
                st.session_state[qres_key] = {"text": text, "err": err, "model": ai_model}
                st.session_state[qtype_key] = "single"
                show_ai(text, err, p, ai_model, sname=sport_name)
            else:
                st.session_state[qtype_key] = "compare"
                compare_all_models(q_prompt, p, _sport_name=sport_name)

    # ── Detaylar (her zaman açık, toggle kaldırıldı) ──
    if is_football:
            t1,t2,t3=st.tabs(["📈 İstatistikler","⚡ Olaylar","🤖 AI Tahmini"])
            with t1:
                if p["sh"]=="NS": st.info("Maç başlamadı.")
                else:
                    with st.spinner("İstatistikler..."): stats=fetch_stats(p["mid"])
                    if stats and len(stats)>=2:
                        h2={s["type"]:s["value"] for s in stats[0].get("statistics",[])}
                        a2={s["type"]:s["value"] for s in stats[1].get("statistics",[])}
                        st.markdown(f"🔵 **{p['home']}** &nbsp;vs&nbsp; 🔴 **{p['away']}**"); st.markdown("---")
                        for k in ["Ball Possession","Total Shots","Shots on Goal","Shots off Goal",
                                  "Blocked Shots","Corner Kicks","Fouls","Yellow Cards","Red Cards","Goalkeeper Saves"]:
                            hv=h2.get(k,"-"); av=a2.get(k,"-")
                            if hv not in [None,"-"] or av not in [None,"-"]: render_bar(k,hv or"-",av or"-")
                    else: st.warning("İstatistik henüz yok.")
            with t2:
                if p["sh"]=="NS": st.info("Maç başlamadı.")
                else:
                    with st.spinner("Olaylar..."): events=fetch_events(p["mid"])
                    if events:
                        for e in events:
                            t=e.get("time",{}).get("elapsed","?")
                            team=e["team"]["name"]; pl=e.get("player",{}).get("name","")
                            det=e.get("detail",e["type"]); ast=e.get("assist",{}).get("name","")
                            if e["type"]=="Goal":
                                icon="🅿️" if "Penalty" in det else "⚽"
                                st.success(f"{icon} **{t}'** {team} — {pl}"+(f" *(asist: {ast})*" if ast else ""))
                            elif e["type"]=="Card":
                                st.warning(f"{'🟨' if 'Yellow' in det else '🟥'} **{t}'** {team} — {pl}")
                            elif e["type"]=="subst":
                                st.info(f"🔄 **{t}'** {team} — çıkan: {pl} / giren: {ast}")
                    else: st.info("Henüz olay yok.")
            with t3:
                btn1,btn2=st.columns(2)
                with btn1: do_single=st.button("🤖 Seçili Model",key=f"ai_{mk}")
                with btn2: do_compare=st.button("⚡ Tüm Modeller Karşılaştır",key=f"cmp_{mk}")
                use_ws = st.checkbox("🌐 Gemini ile güncel haber/sakat bilgisi çek (tüm modeller kullanır)", key=f"ws_{mk}", value=False)

                if do_single or do_compare:
                    with st.spinner("Veri toplanıyor..."):
                        sd   = fetch_stats(p["mid"])  if p["sh"]!="NS" else []
                        ed   = fetch_events(p["mid"]) if p["sh"]!="NS" else []
                        hf   = fetch_form(p["hid"],p["lid"],p["season"])
                        af   = fetch_form(p["aid"],p["lid"],p["season"])
                        hs   = fetch_tstat(p["hid"],p["lid"],p["season"])
                        as_  = fetch_tstat(p["aid"],p["lid"],p["season"])
                        inj_h= fetch_injuries(p["hid"],p["season"])
                        inj_a= fetch_injuries(p["aid"],p["season"])
                        h2h  = fetch_h2h(p["hid"],p["aid"])
                        stand= fetch_standings(p["lid"],p["season"])
                        pred = fetch_predictions(p["mid"])
                        raw  = next((m for m in raw_list if m["fixture"]["id"]==p["mid"]),None)
                        prompt = football_prompt(raw,sd,ed,hf,af,hs,as_,inj_h,inj_a,h2h,stand,pred) if raw else \
                                 generic_prompt(sport_name,p["home"],p["away"],p["status_txt"],p["league"])

                    if use_ws and GEMINI_KEY:
                        news_key = f"news_{p['mid']}"
                        if news_key not in st.session_state:
                            with st.spinner("🌐 Güncel haberler çekiliyor..."):
                                news_prompt = build_news_prompt(p['home'], p['away'], sport_name, p.get('league',''))
                                news_text, news_err = call_gemini(news_prompt, use_search=True)
                            st.session_state[news_key] = news_text or ""
                        news_text = st.session_state.get(news_key, "")
                        if news_text:
                            st.markdown(f'<div class="news-box">🌐 <b>Güncel Haberler:</b><br>{news_text}</div>', unsafe_allow_html=True)
                            prompt = prompt + f"\n\nGÜNCEL HABERLER:\n{news_text}"

                    if do_single:
                        text,err=run_ai(prompt,ai_model)
                        show_ai(text,err,p,ai_model,sname=sport_name)
                    else:
                        compare_all_models(prompt,p,_sport_name=sport_name)
    else:
            t1,t2=st.tabs(["📋 Bilgi","🤖 AI Tahmini"])
            with t1:
                raw=p.get("raw",{})
                ca,cb=st.columns(2)
                with ca:
                    st.markdown(f"**Lig:** {p['league']}")
                    st.markdown(f"**Durum:** {p['status_txt']}")
                    sc=raw.get("scores",{})
                    if sc and isinstance(sc,dict):
                        hs2=sc.get("home",{}); as2=sc.get("away",{})
                        if isinstance(hs2,dict):
                            for q in ["quarter_1","quarter_2","quarter_3","quarter_4","over_time"]:
                                hq=hs2.get(q); aq=as2.get(q)
                                if hq is not None or aq is not None:
                                    qn=q.replace("quarter_","Q").replace("over_time","OT")
                                    st.markdown(f"**{qn}:** {hq or'-'} – {aq or'-'}")
                with cb:
                    st.markdown(f"**Ev:** {p['home']}")
                    st.markdown(f"**Dep:** {p['away']}")
                    st.markdown(f"**Skor:** {p['h_score']} – {p['a_score']}")
            with t2:
                btn1,btn2=st.columns(2)
                with btn1: do_single2=st.button("🤖 Seçili Model",key=f"ai_{mk}")
                with btn2: do_compare2=st.button("⚡ Tüm Modeller",key=f"cmp_{mk}")
                use_ws2 = st.checkbox("🌐 Gemini ile güncel haber çek (tüm modeller kullanır)", key=f"ws_{mk}", value=False)
                if do_single2 or do_compare2:
                    prompt=generic_prompt(sport_name,p["home"],p["away"],p["status_txt"],p["league"])
                    if use_ws2 and GEMINI_KEY:
                        news_key2 = f"news_{mk}"
                        if news_key2 not in st.session_state:
                            with st.spinner("🌐 Güncel haberler çekiliyor..."):
                                news_prompt = build_news_prompt(p['home'], p['away'], sport_name, p.get('league',''))
                                news_text, news_err = call_gemini(news_prompt, use_search=True)
                            st.session_state[news_key2] = news_text or ""
                        news_text = st.session_state.get(news_key2, "")
                        if news_text:
                            st.markdown(f'<div class="news-box">🌐 <b>Güncel Haberler:</b><br>{news_text}</div>', unsafe_allow_html=True)
                            prompt = prompt + f"\n\nGÜNCEL HABERLER:\n{news_text}"
                    if do_single2:
                        with st.spinner("AI analiz yapıyor..."): text,err=run_ai(prompt,ai_model)
                        show_ai(text,err,p,ai_model,sname=sport_name)
                    else:
                        compare_all_models(prompt,p,_sport_name=sport_name)

    st.markdown('<div class="divider"></div>',unsafe_allow_html=True)

# ── SEKMELER ─────────────────────────────────────────────────────
hist_count = len(st.session_state.analysis_history)
tab_pre,tab_live,tab_hist,tab_local=st.tabs([
    f"🕐 Maç Öncesi ({len(pre_all)})",
    f"🔴 Canlı & Bitti ({len(live_parsed)})",
    f"📊 Tahmin Geçmişi ({hist_count})",
    "🌍 Yerel Tahminler"
])

with tab_pre:
    if not pre_all:
        st.info("Maç öncesi maç bulunamadı.")
    else:
        from collections import defaultdict as _dd2

        # ── Lig bazlı grupla ──
        _lig_grp = _dd2(list)
        for _p in pre_all:
            _lig_grp[_p["league"]].append(_p)

        _major_names = ["Premier League","La Liga","Serie A","Bundesliga","Ligue 1",
                        "Süper Lig","Champions League","Europa League","Conference League",
                        "Eredivisie","Primeira Liga","Super League","Ekstraklasa",
                        "NBA","Euroleague","ATP","WTA"]
        def _lig_sort_key(lg):
            for i,mn in enumerate(_major_names):
                if mn.lower() in lg.lower(): return i
            return 99

        _sorted_ligs = sorted(_lig_grp.keys(), key=_lig_sort_key)
        _lig_options = [f"{'⭐ ' if _lig_sort_key(l)<99 else ''}{l} ({len(_lig_grp[l])})" for l in _sorted_ligs]

        st.markdown(f'<div style="font-size:12px;opacity:.5;margin-bottom:6px">{len(_sorted_ligs)} lig · {len(pre_all)} maç</div>', unsafe_allow_html=True)

        # Lig seçici — tek selectbox, stabil
        _sel_lig_label = st.selectbox(
            "🏆 Lig seç",
            _lig_options,
            key=f"lig_sel_{sport_name}_{date_str}",
            label_visibility="collapsed"
        )
        # Seçili ligin maçlarını göster
        _sel_lig_idx = _lig_options.index(_sel_lig_label)
        _sel_lig = _sorted_ligs[_sel_lig_idx]
        _sel_matches = _lig_grp[_sel_lig]

        st.markdown(f'<div style="font-size:11px;opacity:.5;margin:4px 0 8px">📋 {_sel_lig} — {len(_sel_matches)} maç</div>', unsafe_allow_html=True)

        for _p in _sel_matches:
            match_card(_p, pre_raw)

with tab_live:
    # Manuel tetikleme
    col_btn,col_info=st.columns([2,5])
    with col_btn:
        if st.button("🔴 Canlı Maçları Yükle / Yenile",type="primary",use_container_width=True):
            with st.spinner("Canlı maçlar çekiliyor..."):
                st.session_state.live_data=fetch_live_now(cfg["key"],cfg["base"],date_str)
                st.session_state.live_ts=datetime.now(TZ_TR).strftime("%H:%M:%S")
                st.session_state.live_loaded=True
            st.rerun()
    with col_info:
        if st.session_state.live_ts:
            st.caption(f"Son güncelleme: {st.session_state.live_ts} — tekrar yüklemek için butona bas")
        else:
            st.caption("Canlı maçlar otomatik yüklenmez — istek kotasını korumak için manuel tetikleme")

    if not st.session_state.live_loaded:
        st.info("👆 Canlı maçları görmek için butona bas.")
    elif not live_parsed:
        st.info("Şu an canlı veya bitmiş maç yok.")
    else:
        if search:
            live_f=[p for p in live_parsed if search.lower() in (p["home"]+" "+p["away"]).lower()]
        else:
            live_f=live_parsed
        live_now_=[p for p in live_f if p["sh"] in LIVE_SH]
        done_=[p for p in live_f if p["sh"] in DONE_SH]
        live_sorted=live_now_+done_
        lmaj=[p for p in live_sorted if p["is_major"]]
        lmin=[p for p in live_sorted if not p["is_major"]]
        if lmaj:
            for p in lmaj: match_card(p,st.session_state.live_data)
        if lmin:
            if lmaj: st.markdown(f'<div style="font-size:11px;opacity:.5;margin:8px 0 4px">Diğer ({len(lmin)})</div>', unsafe_allow_html=True)
            for p in lmin: match_card(p,st.session_state.live_data)

with tab_hist:
    hist = st.session_state.analysis_history
    if not hist:
        st.info("Henüz analiz yapılmadı. Maç kartlarından AI tahmini al.")
    else:
        hc1, hc2 = st.columns([3,1])
        with hc1:
            hist_search = st.text_input("🔍 Takım ara", "", key="hist_search", placeholder="örn: Galatasaray")
        with hc2:
            if st.button("🗑️ Temizle", key="hist_clear"):
                st.session_state.analysis_history = []
                st.rerun()

        # Group by match
        from collections import defaultdict
        groups = defaultdict(list)
        for h in hist:
            key = f"{h['home']}_{h['away']}_{h['time'][:5]}"
            groups[key].append(h)

        # Arama filtresi
        if hist_search:
            q = hist_search.lower()
            groups = {k:v for k,v in groups.items()
                      if q in v[0].get("home","").lower() or q in v[0].get("away","").lower()
                      or q in v[0].get("league","").lower()}

        st.markdown(f'<div style="font-size:12px;opacity:.5;margin-bottom:8px">{len(groups)} maç · {len(hist)} analiz</div>', unsafe_allow_html=True)

        MODEL_COLORS = {
            "🟡 Groq – Llama 3.3": "#EF9F27",
            "🟢 Gemini 2.0 Flash": "#22c55e",
            "⚪ GPT-4o Mini": "#378ADD",
            "🔴 DeepSeek V3": "#E24B4A"
        }
        MODEL_SHORT = {
            "🟡 Groq – Llama 3.3": "Groq",
            "🟢 Gemini 2.0 Flash": "Gemini",
            "⚪ GPT-4o Mini": "GPT",
            "🔴 DeepSeek V3": "DeepSeek"
        }

        for key, items in reversed(list(groups.items())):
            h0 = items[0]
            # Header row
            hc1,hc2 = st.columns([3,7])
            with hc1:
                st.markdown(f"**{h0['time']}** · {h0['sport']}")
                st.caption(f"{h0['league']}")
            with hc2:
                st.markdown(f"### {h0['home']} – {h0['away']}")

            # Model predictions in one row
            pred_cols = st.columns(len(items))
            for i, h in enumerate(items):
                with pred_cols[i]:
                    color = MODEL_COLORS.get(h["model"],"#888")
                    short = MODEL_SHORT.get(h["model"], h["model"].split()[0])
                    pred = h.get("pred","?")
                    sub = h.get("sub_pred",{})
                    sub_html = ""
                    if sub:
                        sub_html = "".join([
                            f'<div style="font-size:10px;font-weight:600;color:{color};'
                            f'background:rgba(128,128,128,.08);border-radius:5px;'
                            f'padding:1px 5px;margin-top:3px;white-space:nowrap">{k}: {v}</div>'
                            for k,v in sub.items()
                        ])
                    st.markdown(f'''<div style="border:1.5px solid {color};border-radius:10px;padding:8px;text-align:center">
                        <div style="font-size:10px;color:{color};opacity:.8">{short}</div>
                        <div style="font-size:20px;font-weight:900;color:{color};white-space:nowrap">{pred}</div>
                        {sub_html}
                    </div>''', unsafe_allow_html=True)

            # Detailed analyses in expander
            with st.expander("Tam analizleri gör"):
                for h in items:
                    color = MODEL_COLORS.get(h["model"],"#888")
                    short = MODEL_SHORT.get(h["model"], h["model"])
                    st.markdown(f"**{short}** · ~{h['tokens']} token")
                    st.markdown(f'<div class="ai-box" style="border-color:{color}55;margin-bottom:8px">{h["text"]}</div>', unsafe_allow_html=True)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

with tab_local:
    st.markdown("### 🌍 Yerel & Uluslararası Tahminler")
    st.caption("Misli, Nesine, Bilyoner, İddaa ve uluslararası tahmin sitelerinin öngörüleri Gemini ile çekilir.")

    if not GEMINI_KEY:
        st.warning("⚠️ Bu özellik için Gemini API key gerekli.")
    else:
        # Lig filtresi
        local_league = st.text_input("🔍 Lig veya takım filtresi (boş = tüm branş)", "", key="local_league_filter")
        local_cache_key = f"local_preds_{sport_name}_{date_str}_{local_league}"

        col1, col2 = st.columns([2,1])
        with col1:
            fetch_btn = st.button("🌐 Yerel Tahminleri Çek", type="primary", use_container_width=True, key="fetch_local")
        with col2:
            if st.button("🗑️ Temizle", use_container_width=True, key="clear_local"):
                if local_cache_key in st.session_state:
                    del st.session_state[local_cache_key]
                st.rerun()

        if fetch_btn:
            with st.spinner("🌐 Tahmin siteleri taranıyor..."):
                local_prompt = fetch_gemini_local_predictions(sport_name, date_str, local_league)
                local_text, local_err = call_gemini(local_prompt, use_search=True)
            if local_err:
                st.error(local_err)
            elif local_text:
                st.session_state[local_cache_key] = local_text
                st.rerun()

        if st.session_state.get(local_cache_key):
            st.markdown(f'<div class="news-box" style="font-size:14px;line-height:1.8">{st.session_state[local_cache_key]}</div>', unsafe_allow_html=True)
            st.caption(f"📅 {date_str} | {sport_name} | Gemini web araması ile çekildi")
