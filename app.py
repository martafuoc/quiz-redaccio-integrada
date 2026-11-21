"""
Quiz de la redacció integrada (UOC) · Kickoff
Streamlit + Google Sheets

Vistes:
  - Quiz (per defecte):            https://<la-teva-app>.streamlit.app
  - Resultats d'equip (projector): https://<la-teva-app>.streamlit.app/?vista=resultats
"""

import time
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

# ------------------------------------------------------------------
# Configuració
# ------------------------------------------------------------------
st.set_page_config(page_title="Quiz de la redacció integrada", page_icon="🎯", layout="centered")

TEMPS = 30            # segons de referència per pregunta
PUNTS_MAX = 1000      # punts si s'encerta a l'instant
PUNTS_MIN = 500       # punts mínims per encert
FULL_RESULTATS = "resultats"
FULL_APORTACIONS = "aportacions"
ZONA = ZoneInfo("Europe/Madrid")

PREGUNTES = [
    {"q": "Tenim una previsió TOP. Què ha de decidir, abans que res, com la difonem?",
     "o": ["El canal on tenim més seguidors", "El públic al qual ens adrecem", "El format que ja tenim fet", "L'ordre en què ha entrat a Monday"], "a": 1,
     "x": "El públic és el criteri principal. Els nivells de prioritat orienten la difusió, però no predeterminen canals ni productes."},
    {"q": "El 12 de març es publica l'informe d'inserció laboral dels titulats. Aquest fet, al Monday, és...",
     "o": ["Una previsió", "Un producte editorial", "Una campanya", "Un capítol"], "a": 0,
     "x": "És el fet datat: una previsió. La nota, el vídeo i el post que en fem són productes editorials, i poden formar un capítol d'Ocupabilitat 2027."},
    {"q": "Què fa que una cosa sigui una campanya?",
     "o": ["Que hi hagi pressupost per a globus", "Concepte únic, capítols, tots els canals alhora, públic prioritari, fitxa i mesura", "Que duri més d'una setmana", "Que hi surti la rectora"], "a": 1,
     "x": "Una campanya és un relat amb un concepte únic, desplegat en capítols, que activa tots els canals alhora i es mesura."},
    {"q": "Una nota de premsa sobre un estudi de la UOC, tota sola, és una campanya?",
     "o": ["Sí, si surt a molts mitjans", "No: és un producte editorial, que pot ser el capítol d'una campanya si encaixa en el seu relat", "Sí, si la publiquem en tres idiomes", "Només si la retuiteja la rectora"], "a": 1,
     "x": "Una peça sola no fa campanya. Ho és quan forma part d'un relat amb concepte, capítols, fitxa i mesura."},
    {"q": "On es decideix si una previsió entra en una campanya?",
     "o": ["A la màquina de cafè", "Al consell de redacció mensual", "Al xat d'actualitat", "A la Taula de relats"], "a": 1,
     "x": "La decisió editorial es pren al consell de redacció; el seguiment de les campanyes, a la Taula de relats."},
    {"q": "Què es fa a la Taula de relats?",
     "o": ["Es reparteixen els torrons de Nadal", "Es revisen les previsions d'actualitat que no són campanya", "Seguiment de cada campanya: capítols, KPIs, ajustos i propers passos", "Es corregeixen faltes d'ortografia"], "a": 2,
     "x": "És l'espai mensual de seguiment de campanyes i grans relats. L'actualitat que no és campanya no s'hi tracta."},
    {"q": "Quin d'aquests NO és un dels quatre territoris de la redacció?",
     "o": ["Educació al llarg de la vida", "Innovació educativa", "Salut digital", "Comunitat"], "a": 2,
     "x": "Salut digital és un subàmbit de Recerca i coneixement. Els quatre territoris són Educació al llarg de la vida, Innovació educativa, Recerca i coneixement, i Comunitat."},
    {"q": "Quin territori té, a més, una mirada transversal a tots els altres?",
     "o": ["Recerca i coneixement", "Innovació educativa", "Comunitat", "Educació al llarg de la vida"], "a": 2,
     "x": "La cap d'eix de Comunitat té doble rol: lidera campanyes pròpies i vetlla pels criteris de comunitat a tots els territoris."},
    {"q": "Estàs a punt de publicar una peça. Què et fa revisar el community check?",
     "o": ["Que hi surti el logo ben gran", "Si hi ha veus de la comunitat, un benefici per a ella i una crida a l'acció relacional", "Que tingui més de mil paraules", "Que l'hagi votat tota la comunitat"], "a": 1,
     "x": "Persones al centre: veus, benefici i crida a l'acció. Ho comprova cada autor abans de publicar."},
    {"q": "Ocupabilitat 2027 és la campanya pilot de...",
     "o": ["Educació al llarg de la vida", "Recerca i coneixement", "Innovació educativa", "Recursos Humans"], "a": 0,
     "x": "Primer capítol: la inserció laboral dels titulats, amb la Fira d'ocupació com a acció 360."},
    {"q": "La docusèrie «Com vivim», en quin territori encaixa més?",
     "o": ["Educació al llarg de la vida", "Innovació educativa", "Recerca i coneixement", "Comunitat"], "a": 2,
     "x": "Forma part del capítol 1 de «Recerca per entendre i actuar»: la recerca que respon als reptes globals."},
    {"q": "Un vídeo amb testimonis d'alumnis que han canviat de feina gràcies a la UOC, on el posaries?",
     "o": ["Educació al llarg de la vida, a Ocupabilitat 2027", "Recerca i coneixement", "Innovació educativa", "A la carpeta «Ja ho mirarem»"], "a": 0,
     "x": "És la peça «Sentir» d'Ocupabilitat 2027: les dades d'inserció, explicades per les persones."},
    {"q": "Un vídeo que explica com es fa servir la IA a les aules, amb veus de l'eLinC, el professorat i l'estudiantat, encaixa a...",
     "o": ["Comunitat", "Innovació educativa", "Educació al llarg de la vida", "Cap territori: és un tutorial"], "a": 1,
     "x": "És la peça forta de «IA per transformar el model educatiu», la campanya pilot d'Innovació educativa."},
    {"q": "«Recerca per entendre i actuar»: quin capítol inclou el Doctoral Day?",
     "o": ["Reptes globals", "Talent jove investigador", "Transferència", "Cinc missions de recerca"], "a": 1,
     "x": "El capítol 2 explica qui són les ments joves que canvien el panorama científic a la UOC."},
    {"q": "Quina d'aquestes NO és una capa d'etiquetatge?",
     "o": ["Territori", "Subtag amb propòsit", "Nom de campanya", "Estat d'ànim del redactor"], "a": 3,
     "x": "Tres capes: territori, subtag amb propòsit i nom de campanya. L'estat d'ànim, de moment, no el mesurem."},
    {"q": "Per a què ens serveix l'Índex de Repercussió Mediàtica (IRM)?",
     "o": ["Per comptar quants periodistes tenim a l'agenda", "Per mesurar la presència i el valor de la UOC als mitjans, i veure si som veu de referència", "Per saber quantes notes de premsa enviem", "Per calcular el pressupost de publicitat"], "a": 1,
     "x": "És un dels indicadors qualitatius de referència, juntament amb el sentiment de la conversa i l'índex de reputació."},
    {"q": "Un reel de la UOC té moltes visualitzacions, però gairebé ningú el comenta, el comparteix ni el desa. Quin indicador et diu si ha connectat de debò?",
     "o": ["Les visualitzacions", "La taxa d'interacció", "Els seguidors que tenim", "El nombre de hashtags"], "a": 1,
     "x": "Les visualitzacions diuen quanta gent l'ha vist. La taxa d'interacció (comentaris, compartits i desats sobre l'abast) diu si ha connectat, i desats i compartits són els senyals més valuosos."},
    {"q": "Qui fa el community check d'una peça?",
     "o": ["La cap d'eix de Comunitat, peça per peça", "Cada autor, abans de publicar", "L'equip de Xarxes, quan la difon", "Ningú: és opcional"], "a": 1,
     "x": "No és un filtre extern: la cap de Comunitat dona criteri, però la revisió la fa cada autor abans de publicar."},
    {"q": "Vols provar un format interactiu nou en una campanya. Amb qui en parles primer?",
     "o": ["Amb la figura de nous formats", "Amb l'Oficina de Mitjans", "Amb Dades i Audiències", "Amb ningú: ho fas tot sol"], "a": 0,
     "x": "Nous formats promou la innovació en formats de la redacció i articula els interactius amb Audiovisuals, Xarxes i editores."},
    {"q": "El nou model comunicatiu ens porta «de l'emissor únic a...»",
     "o": ["...l'emissor doble", "...la cocreació", "...el silenci estratègic", "...l'emissor amb GIFs"], "a": 1,
     "x": "La comunitat participa en el relat i en els continguts: estudiantat, alumnis, PDI i aliances com a veus."},
]
N = len(PREGUNTES)
CAP_RESULTATS = ["data", "sessio", "alias", "punts", "encerts"] + [f"p{i + 1}" for i in range(N)]
CAP_APORTACIONS = ["data", "alias", "tipus", "text"]

RANGS = [
    (18700, "Llegenda de la redacció", "Puntuació de rècord. Algú hauria d'etiquetar-te amb subtag propi."),
    (16700, "Cap de territori", "Tens visió de conjunt i reflexos. Ja pots presidir la Taula de relats."),
    (12700, "Redactor/a integrat/da", "Domines el model: previsions, productes i campanyes no tenen secrets per a tu."),
    (8000, "Redactor/a amb potencial", "Tens la base. Una mica més de Monday i seràs imparable."),
    (0, "Becari/ària en pràctiques", "Has vingut, i això ja compta. Repassa la presentació i torna-hi!"),
]


def missatge_equip(p: int) -> str:
    if p >= 85:
        return f"Estem preparats al {p}%! La redacció integrada ja és una realitat."
    if p >= 70:
        return f"Estem preparats al {p}%! Ja hi som gairebé: ara toca fer-ho cada dia."
    if p >= 50:
        return f"Estem preparats al {p}%. Bona base: el primer consell mensual i la Taula de relats faran la resta."
    return f"Estem preparats al {p}%. Tot just comencem, i per això fem aquest kickoff!"


# ------------------------------------------------------------------
# Estil UOC
# ------------------------------------------------------------------
st.markdown("""
<style>
:root{--navy:#000078;--cyan:#73EDFF;--sand:#DDD5C2}
.stApp{background:#000078;color:#fff}
.stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label,.stApp li,.stApp span{color:#fff}
.brand{color:#73EDFF;font-weight:800;letter-spacing:.04em;text-transform:uppercase;font-size:13px}
.big{color:#73EDFF;font-weight:800;font-size:clamp(64px,16vw,140px);line-height:1}
.score{color:#73EDFF;font-weight:800;font-size:64px;line-height:1}
.motto{font-weight:800;font-size:clamp(24px,5vw,40px);line-height:1.15}
.box{background:#14148f;border-radius:16px;padding:18px 20px;margin:8px 0}
.ok{color:#3fd68b!important;font-weight:800;font-size:20px}
.ko{color:#ff7a7a!important;font-weight:800;font-size:20px}
div.stButton>button{width:100%;min-height:64px;border-radius:14px;background:#fff;color:#000078;
  font-weight:700;font-size:16px;border:0;white-space:normal;text-align:left}
div.stButton>button:hover{background:#73EDFF;color:#000078}
div.stButton>button p{color:#000078!important}
.stTextInput input,.stTextArea textarea{background:#fff;color:#000078}
[data-testid="stTable"] *, [data-testid="stDataFrame"] *{color:#000078}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------
# Google Sheets
# ------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def llibre():
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    return gspread.authorize(creds).open_by_key(st.secrets["sheet_id"])


def full(nom: str, capcalera: list[str]):
    b = llibre()
    try:
        return b.worksheet(nom)
    except gspread.WorksheetNotFound:
        try:
            w = b.add_worksheet(title=nom, rows=1000, cols=len(capcalera))
            w.append_row(capcalera)
            return w
        except gspread.exceptions.APIError:
            # Una altra persona l'ha creat alhora: el tornem a llegir
            return b.worksheet(nom)


def ara() -> str:
    return datetime.now(ZONA).strftime("%Y-%m-%d %H:%M:%S")


def desa_resultat(alias, punts, encerts, respostes) -> bool:
    try:
        full(FULL_RESULTATS, CAP_RESULTATS).append_row(
            [ara(), st.session_state.sessio, alias, punts, encerts] + respostes,
            value_input_option="USER_ENTERED")
        llegeix_resultats.clear()
        return True
    except Exception:
        return False


def desa_aportacio(alias, tipus, text) -> bool:
    try:
        full(FULL_APORTACIONS, CAP_APORTACIONS).append_row([ara(), alias, tipus, text[:1200]])
        return True
    except Exception:
        return False


@st.cache_data(ttl=8, show_spinner=False)
def llegeix_resultats() -> list[dict]:
    try:
        files = full(FULL_RESULTATS, CAP_RESULTATS).get_all_records()
    except Exception:
        return []
    # Millor intent de cada persona (per àlies)
    millors = {}
    for f in files:
        clau = str(f.get("alias", "")).strip().lower()
        if not clau:
            continue
        if clau not in millors or int(f.get("punts") or 0) > int(millors[clau].get("punts") or 0):
            millors[clau] = f
    return sorted(millors.values(), key=lambda f: int(f.get("punts") or 0), reverse=True)


# ------------------------------------------------------------------
# Vista de resultats d'equip (per projectar)
# ------------------------------------------------------------------
def vista_resultats():
    st.markdown('<div class="brand">UOC · Redacció integrada · Resultats de l\'equip</div>', unsafe_allow_html=True)

    @st.fragment(run_every=10)
    def panell():
        files = llegeix_resultats()
        if not files:
            st.markdown('<div class="motto">Esperant els primers resultats…</div>', unsafe_allow_html=True)
            return
        n = len(files)
        total = sum(int(f.get("encerts") or 0) for f in files)
        p = round(total / (n * N) * 100)
        st.markdown(f'<div class="big">{p}%</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="motto">{missatge_equip(p)}</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Persones que han jugat", n)
        c2.metric("Encerts de mitjana", f"{total / n:.1f}/{N}".replace(".", ","))
        c3.metric("Millor puntuació", f"{int(files[0].get('punts') or 0):,}".replace(",", "."))

        st.subheader("Rànquing")
        st.table([{"#": i + 1, "Nom": f.get("alias"), "Encerts": f"{f.get('encerts')}/{N}",
                   "Punts": f"{int(f.get('punts') or 0):,}".replace(",", ".")} for i, f in enumerate(files[:15])])

        st.subheader("Pregunta a pregunta")
        st.caption("De menys a més encerts: les primeres són els conceptes per reforçar al primer consell mensual.")
        per = []
        for i, q in enumerate(PREGUNTES):
            vals = [int(f.get(f"p{i + 1}") or 0) for f in files]
            per.append((round(sum(vals) / len(vals) * 100), q["q"]))
        for pc, txt in sorted(per):
            st.markdown(f"**{pc}%** · {txt}")
            st.progress(pc / 100)

    panell()


# ------------------------------------------------------------------
# Quiz
# ------------------------------------------------------------------
def init():
    ss = st.session_state
    ss.setdefault("sessio", uuid.uuid4().hex[:10])
    ss.setdefault("fase", "inici")
    ss.setdefault("alias", "")
    ss.setdefault("i", 0)
    ss.setdefault("punts", 0)
    ss.setdefault("encerts", 0)
    ss.setdefault("respostes", [])
    ss.setdefault("t0", 0.0)
    ss.setdefault("ultima", None)
    ss.setdefault("desat", False)


def comenca():
    ss = st.session_state
    ss.fase, ss.i, ss.punts, ss.encerts, ss.respostes = "pregunta", 0, 0, 0, []
    ss.desat, ss.sessio = False, uuid.uuid4().hex[:10]
    ss.t0 = time.time()


def respon(k: int):
    ss = st.session_state
    if ss.fase != "pregunta":
        return
    q = PREGUNTES[ss.i]
    t = time.time() - ss.t0
    ok = k == q["a"]
    pts = 0
    if ok:
        pts = round(PUNTS_MIN + (PUNTS_MAX - PUNTS_MIN) * max(0.0, TEMPS - t) / TEMPS)
        ss.punts += pts
        ss.encerts += 1
    ss.respostes.append(1 if ok else 0)
    ss.ultima = {"k": k, "ok": ok, "pts": pts, "t": t}
    ss.fase = "feedback"


def seguent():
    ss = st.session_state
    ss.i += 1
    if ss.i >= N:
        ss.fase = "final"
    else:
        ss.fase = "pregunta"
        ss.t0 = time.time()


def vista_quiz():
    ss = st.session_state
    st.markdown('<div class="brand">UOC · Redacció integrada · Kickoff</div>', unsafe_allow_html=True)

    if ss.fase == "inici":
        st.title("Quant saps de la nova redacció?")
        st.write(f"{N} preguntes per repassar territoris, campanyes, prioritats i mesura. "
                 f"Com més ràpid encertis, més punts: fins a {PUNTS_MAX:,} per pregunta.".replace(",", "."))
        alias = st.text_input("El teu nom o àlies de redacció", max_chars=24, placeholder="Ex.: La reina del Monday")
        if st.button("Comença", disabled=not alias.strip()):
            ss.alias = alias.strip()
            comenca()
            st.rerun()
        return

    if ss.fase in ("pregunta", "feedback"):
        q = PREGUNTES[ss.i]
        c1, c2 = st.columns(2)
        c1.caption(f"Pregunta {ss.i + 1} de {N}")
        c2.caption(f"{ss.punts:,} punts".replace(",", "."))
        st.progress(ss.i / N)
        st.subheader(q["q"])

        if ss.fase == "pregunta":
            st.caption(f"Respon ràpid: els punts baixen durant els primers {TEMPS} segons.")
            for k, opcio in enumerate(q["o"]):
                st.button(f"{'ABCD'[k]}.  {opcio}", key=f"o{ss.i}_{k}", on_click=respon, args=(k,))
        else:
            u = ss.ultima
            for k, opcio in enumerate(q["o"]):
                marca = "✅" if k == q["a"] else ("❌" if k == u["k"] else "▫️")
                st.markdown(f"{marca} {'ABCD'[k]}. {opcio}")
            if u["ok"]:
                st.markdown(f'<div class="ok">Ben vist! +{u["pts"]} punts</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="ko">Aquesta no... +0 punts</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="box">{q["x"]}</div>', unsafe_allow_html=True)
            st.button("Veure el resultat" if ss.i == N - 1 else "Següent", key=f"seg{ss.i}", on_click=seguent)
        return

    if ss.fase == "final":
        if not ss.desat:
            ss.desat = desa_resultat(ss.alias, ss.punts, ss.encerts, ss.respostes) or "error"
        rang = next(r for r in RANGS if ss.punts >= r[0])
        st.caption(f"{ss.alias} · {ss.encerts} de {N} encerts")
        st.markdown(f'<div class="score">{ss.punts:,}</div>'.replace(",", "."), unsafe_allow_html=True)
        st.markdown(f"### {rang[1]}")
        st.write(rang[2])
        if ss.desat == "error":
            st.warning("No s'ha pogut desar el resultat al rànquing.")

        st.divider()
        st.header("Un projecte viu")
        st.write("La redacció integrada la construïm entre tots. Deixa'ns dubtes, idees o comentaris: "
                 "els tractarem al primer consell mensual.")
        with st.form("aportacio", clear_on_submit=True):
            tipus = st.radio("Què ens vols deixar?", ["Dubte", "Idea", "Comentari"], horizontal=True)
            text = st.text_area("Escriu-lo aquí", max_chars=1200,
                                placeholder="Ex.: Com sabré si la meva previsió forma part d'una campanya?")
            if st.form_submit_button("Envia"):
                if not text.strip():
                    st.warning("Escriu alguna cosa abans d'enviar.")
                elif desa_aportacio(ss.alias, tipus, text.strip()):
                    st.success("Gràcies! Ho portarem al primer consell mensual. Pots afegir-ne més.")
                else:
                    st.error("No s'ha pogut enviar. Torna-ho a provar d'aquí a una estona.")

        st.divider()
        st.subheader("Rànquing")
        files = llegeix_resultats()
        if files:
            st.table([{"#": i + 1, "Nom": f.get("alias"), "Encerts": f"{f.get('encerts')}/{N}",
                       "Punts": f"{int(f.get('punts') or 0):,}".replace(",", ".")} for i, f in enumerate(files[:15])])
        else:
            st.caption("Encara no hi ha resultats.")
        if st.button("Torna-hi"):
            ss.fase = "inici"
            st.rerun()


# ------------------------------------------------------------------
init()
if st.query_params.get("vista") == "resultats":
    vista_resultats()
else:
    vista_quiz()
