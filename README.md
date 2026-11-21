# Quiz de la redacció integrada · Guia de publicació

Una web pública, sense registre, amb el quiz del kickoff. Els resultats i les aportacions es desen en un Google Sheet del teu Drive.

| Peça | Per a què serveix |
|---|---|
| **GitHub** | Guarda el codi |
| **Streamlit Community Cloud** | Publica el codi com a web gratuïta (`https://el-teu-nom.streamlit.app`) |
| **Google Sheet** | Guarda els resultats (pestanya `resultats`) i els dubtes i idees (pestanya `aportacions`) |
| **Google Cloud (compte de servei)** | Un "usuari robot" que permet a l'app escriure al Sheet |

Temps estimat: 30–45 minuts el primer cop.

---

## Pas 1 · Crea el Google Sheet

1. Al teu Drive: **Nou → Fulls de càlcul de Google**. Posa-li de nom, per exemple, `Quiz redacció integrada`.
2. Copia l'**ID** de la URL, és a dir, el tros entre `/d/` i `/edit`:
   `https://docs.google.com/spreadsheets/d/`**`1AbC...xyz`**`/edit`
3. Deixa'l buit. L'app crea sola les pestanyes `resultats` i `aportacions`.

## Pas 2 · Crea el compte de servei a Google Cloud

> Si fas servir el compte de la UOC i Google no et deixa crear projectes o claus, fes aquest pas amb un compte de Google personal. El Sheet pot estar al Drive que vulguis.

1. Entra a <https://console.cloud.google.com> i crea un **projecte nou**, per exemple `quiz-redaccio`.
2. Menú → **APIs i serveis → Biblioteca** → cerca **Google Sheets API** → **Habilita**.
3. Menú → **APIs i serveis → Credencials** → **Crea credencials → Compte de servei**. Posa-li un nom (`quiz-app`) i fes clic a **Fet**. No cal donar-li cap rol.
4. Obre el compte de servei creat → pestanya **Claus** → **Afegeix una clau → Crea una clau nova → JSON**. Es descarrega un fitxer `.json`.
   ⚠️ Aquest fitxer és una contrasenya: no el pugis mai a GitHub ni el comparteixis.
5. Copia el **correu del compte de servei**, que s'assembla a `quiz-app@quiz-redaccio.iam.gserviceaccount.com`.

## Pas 3 · Comparteix el Sheet amb el compte de servei

Al Google Sheet: **Comparteix** → enganxa el correu del compte de servei → permís **Editor** → desactiva "Notifica" → **Comparteix**.

## Pas 4 · Puja el codi a GitHub

1. A <https://github.com> → **New repository** → nom `quiz-redaccio-integrada`. Pot ser **públic**, perquè el codi no conté cap dada privada.
2. **Add file → Upload files** i puja aquests tres fitxers:
   - `app.py`
   - `requirements.txt`
   - `.gitignore` (opcional)
3. **Commit changes**.

**No** hi pugis `secrets_exemple.toml` amb dades reals ni el fitxer `.json`.

## Pas 5 · Publica amb Streamlit Community Cloud

1. Entra a <https://share.streamlit.io> amb el teu compte de GitHub.
2. **Create app → Deploy a public app from GitHub**.
3. Omple els camps:
   - **Repository:** `el-teu-usuari/quiz-redaccio-integrada`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** tria'n una de fàcil, per exemple `quiz-redaccio-uoc`
4. **Advanced settings → Secrets.** Obre `secrets_exemple.toml`, omple'l i enganxa'l:
   - `sheet_id` → l'ID del pas 1.
   - Bloc `[gcp_service_account]` → copia cada valor del fitxer `.json` del pas 2.
   - Ves amb compte amb `private_key`: copia-la sencera, entre cometes i amb els `\n` tal com surten al JSON.
5. **Deploy.** En un parell de minuts tindràs la web a `https://quiz-redaccio-uoc.streamlit.app`.

Si després has de canviar els secrets: la teva app → **⋮ → Settings → Secrets**.

## Pas 6 · Prova-ho

1. Fes una partida sencera i envia un dubte de prova.
2. Comprova que al Sheet apareixen les pestanyes `resultats` i `aportacions` amb les teves files.
3. Obre la vista per projectar: `https://quiz-redaccio-uoc.streamlit.app/?vista=resultats`. S'actualitza sola cada 10 segons.
4. Abans del kickoff, **esborra les files de prova** del Sheet. Deixa la primera fila, la de capçaleres.

## Pas 7 · El dia del kickoff

| Què | Com |
|---|---|
| **QR per a la presentació** | A Chrome, obre l'URL del quiz → icona de compartir de la barra d'adreces → **Crea un codi QR** → descarrega'l i posa'l a la diapositiva de la dinàmica |
| **Despertar l'app** | Si fa dies que ningú hi entra, Streamlit l'adorm. Obre-la mitja hora abans i, si cal, fes clic a "Yes, get this app back up" |
| **Projectar resultats** | `…/?vista=resultats`: percentatge de l'equip, missatge motivacional, rànquing i preguntes per reforçar |
| **Dubtes i idees** | Pestanya `aportacions` del Sheet, a punt per al primer consell mensual |

## Com funciona la puntuació

- Encert: entre 500 i 1.000 punts, segons la rapidesa (temps de referència: 30 s).
- Error: 0 punts.
- Si algú juga més d'un cop amb el mateix àlies, el rànquing i el percentatge de l'equip compten el seu millor intent.

## Canviar preguntes o textos

Tot és a `app.py`:

- **Preguntes:** a la llista `PREGUNTES`, cada pregunta té:
  - `q`: el text de la pregunta;
  - `o`: les 4 opcions;
  - `a`: la posició de la correcta, començant per 0;
  - `x`: l'explicació.
- **Missatges motivacionals:** a `missatge_equip()`.
- **Títols finals:** a `RANGS`.

Edita el fitxer a GitHub (icona del llapis → **Commit**) i Streamlit actualitza la web sola en un minut.
