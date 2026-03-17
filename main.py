"""
BLUE JEANS PICTURES — English-Translator
한국어 시나리오 → 영어 번역 (구조 보존)
Powered by Anthropic Claude API
"""

import streamlit as st
import anthropic
import re
import io
import csv

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="English-Translator | BLUE JEANS PICTURES",
    page_icon="🎬",
    layout="wide",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&display=swap');

/* ── Global background ── */
.stApp {
    background-color: #F7F7F5 !important;
}

/* ── Main Header (Creator Engine style) ── */
.main-header {
    text-align: center;
    padding: 2.5rem 0 1rem 0;
}
.main-header .brand-name {
    font-size: 0.85rem;
    color: #191970;
    letter-spacing: 0.35em;
    font-weight: 600;
    margin-bottom: 0.3rem;
}
.main-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem;
    font-weight: 900;
    color: #191970;
    margin: 0.2rem 0 0;
    letter-spacing: 0.02em;
    display: inline-block;
    border-bottom: 4px solid #f5c842;
    padding-bottom: 0.3rem;
}
.main-header .tagline {
    font-size: 0.78rem;
    color: #999;
    letter-spacing: 0.3em;
    margin-top: 0.7rem;
    font-weight: 400;
}

/* ── Section headers (yellow bar) ── */
.section-header {
    background: #f5c842;
    color: #191970;
    padding: 0.5rem 1.1rem;
    border-radius: 6px;
    font-weight: 700;
    font-size: 0.95rem;
    margin: 1.5rem 0 0.8rem 0;
    letter-spacing: 0.03em;
}

/* ── Result box ── */
.result-box {
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 1.2rem;
    font-family: 'Courier New', monospace;
    font-size: 0.88rem;
    line-height: 1.7;
    white-space: pre-wrap;
    max-height: 600px;
    overflow-y: auto;
}

/* ── Page chip ── */
.page-chip {
    display: inline-block;
    background: #191970;
    color: #f5c842;
    padding: 0.2rem 0.7rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

/* ── Character map table ── */
.char-table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.5rem 0;
    font-size: 0.85rem;
}
.char-table th {
    background: #191970;
    color: #f5c842;
    padding: 0.45rem 0.8rem;
    text-align: left;
    font-weight: 600;
}
.char-table td {
    padding: 0.4rem 0.8rem;
    border-bottom: 1px solid #e8e8e0;
}
.char-table tr:nth-child(even) td {
    background: #EEEEF6;
}

/* ── Progress ── */
.progress-text {
    text-align: center;
    color: #666;
    font-size: 0.85rem;
    padding: 0.5rem 0;
}

/* ── Footer ── */
.footer {
    text-align: center;
    color: #bbb;
    font-size: 0.72rem;
    margin-top: 2.5rem;
    padding: 1rem 0;
    border-top: 1px solid #ddd;
    letter-spacing: 0.08em;
}

/* ── Streamlit overrides for cream theme ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background-color: #fff !important;
    border-color: #ddd !important;
}
div[data-testid="stFileUploader"] {
    background-color: #fff !important;
    border-radius: 8px;
}
.stExpander {
    background-color: #fff !important;
    border-color: #ddd !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
MAX_CHARS_PER_PAGE = 8000

MODEL_OPTIONS = {
    "⚡ Haiku — 빠르고 저렴 (~$0.1/편)": {
        "id": "claude-haiku-4-5-20251001",
        "max_tokens": 8000,
        "desc": "기본 구조 보존 + 빠른 속도. 초벌 번역·확인용에 적합.",
    },
    "✦ Sonnet — 균형 잡힌 품질 (~$1/편)": {
        "id": "claude-sonnet-4-20250514",
        "max_tokens": 8000,
        "desc": "높은 번역 품질 + 합리적 비용. 대부분의 작업에 추천.",
    },
    "🏆 Opus — 최고 품질 (~$5/편)": {
        "id": "claude-opus-4-20250514",
        "max_tokens": 8000,
        "desc": "프리미엄 번역. 해외 공동제작 패키지·영화제 제출용.",
    },
}

# ─── Style Presets ───
STYLE_PRESETS = {
    "🎯 Standard — 할리우드 표준": {
        "desc": "미국 메이저 스튜디오 제출용 표준 포맷. 깔끔하고 읽기 쉬운 영어.",
        "prompt": """Style: Standard Hollywood submission format.
- Dialogue: Clean, natural American English. No slang unless character-appropriate.
- Action lines: Lean, visual, present-tense. Every word earns its place.
- Tone: Professional, neutral — let the story speak for itself.""",
    },
    "🔪 Thriller / Crime — 긴장감 중심": {
        "desc": "짧은 문장, 건조한 톤, 긴장감 있는 리듬.",
        "prompt": """Style: Thriller / Crime genre.
- Dialogue: Clipped, terse. Characters speak in short bursts. Subtext over exposition.
- Action lines: Staccato rhythm. Short sentences. Fragment OK. Create tension through pacing.
- Tone: Dry, hard-boiled. Minimal adjectives. Let silence and white space do the work.""",
    },
    "💕 Romance / Drama — 감성적": {
        "desc": "부드러운 톤, 감정의 결이 살아있는 번역.",
        "prompt": """Style: Romance / Drama genre.
- Dialogue: Warm, emotionally layered. Let vulnerability show through word choice.
- Action lines: Sensory details matter — light, texture, breath, gesture. Poetic but not purple.
- Tone: Intimate, human. Preserve the emotional rhythm and pauses of the original.""",
    },
    "😂 Comedy — 유머 살리기": {
        "desc": "타이밍과 리듬 중심, 웃긴 걸 웃기게.",
        "prompt": """Style: Comedy genre.
- Dialogue: Prioritize comedic timing and rhythm over literal accuracy. Punchlines must land in English.
- Action lines: Light, energetic. Physical comedy described with precise visual timing.
- Tone: Adapt humor culturally when needed — the joke matters more than the literal meaning.""",
    },
    "🎭 Art House / Festival — 영화제용": {
        "desc": "문학적 감각, A24/칸 영화제 스타일.",
        "prompt": """Style: Art House / Festival submission.
- Dialogue: Literary quality. Subtext-heavy. Silences and non-verbal beats are as important as words.
- Action lines: Evocative, almost novelistic. Sensory and atmospheric. Visual poetry on the page.
- Tone: Contemplative, layered. Preserve ambiguity and thematic depth. European sensibility.""",
    },
    "⚔️ Action / Blockbuster — 액션 블록버스터": {
        "desc": "빠른 템포, 강렬한 액션 묘사.",
        "prompt": """Style: Action / Blockbuster genre.
- Dialogue: Punchy, quotable. One-liners welcome. Characters speak with confidence.
- Action lines: Kinetic, visceral. Fast cuts on the page. Short paragraphs. Impact verbs.
- Tone: High energy, forward momentum. Every scene pushes harder than the last.""",
    },
    "👻 Horror / Supernatural — 공포·초자연": {
        "desc": "불안감 조성, 감각적 공포 묘사.",
        "prompt": """Style: Horror / Supernatural genre.
- Dialogue: Understated dread. What characters DON'T say matters. Whispers over screams.
- Action lines: Slow-burn tension. Sensory details that unsettle — sounds, shadows, wrong silences.
- Tone: Creeping unease. Build atmosphere through restraint. The unseen is scarier than the seen.""",
    },
    "📺 K-Drama Adaptation — K드라마 각색": {
        "desc": "K드라마 특유의 감성을 살리면서 영어권에 맞게 각색.",
        "prompt": """Style: K-Drama adaptation for English-speaking audience.
- Dialogue: Preserve the emotional directness of Korean drama. Honorifics adapted naturally.
- Action lines: Keep the visual grammar of K-drama — close-ups implied, reaction beats preserved.
- Tone: Emotionally generous. The heightened sincerity that defines K-drama should translate, not flatten.""",
    },
}

BASE_SYSTEM_PROMPT = """You are an expert Korean-to-English screenplay translator for the international film market.

## RULES — ABSOLUTE
1. **Preserve ALL structural formatting exactly:**
   - Scene headers (S#, 씬, SCENE numbers) → keep numbering, translate location/time
   - Parenthetical directions: (O.L.), (E), (NA), CUT TO, FADE IN, etc. → keep as-is or use standard English equivalents
   - Stage directions / 지문 → translate into professional English action lines
   - Dialogue → translate into natural, cinematic English dialogue
   - Line breaks, indentation patterns, blank lines → preserve exactly

2. **Translation quality:**
   - Produce **professional, production-grade English** suitable for international co-production packages
   - Dialogue must sound natural and spoken — not literary or stiff
   - Action lines must be vivid, present-tense, visual — standard screenplay style
   - Preserve the emotional tone, subtext, and rhythm of the original

3. **DO NOT:**
   - Add scene numbers or formatting that doesn't exist in the original
   - Remove any structural element
   - Add commentary, notes, or explanations
   - Merge or split scenes

4. **Output ONLY the translated screenplay text.** No preamble, no closing remarks."""


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def parse_character_map(uploaded_file) -> dict:
    """Parse character name mapping from CSV or TXT file.

    Supported formats:
      CSV: 한국이름,영어이름  (with or without header)
      TXT: 한국이름 → 영어이름  or  한국이름 = 영어이름  or  한국이름, 영어이름
    """
    name = uploaded_file.name.lower()
    content = uploaded_file.read().decode("utf-8", errors="replace")
    uploaded_file.seek(0)

    char_map = {}
    skip_headers = {"한국이름", "한국명", "korean", "name", "이름"}

    if name.endswith(".csv"):
        reader = csv.reader(io.StringIO(content))
        for row in reader:
            if len(row) >= 2:
                ko = row[0].strip()
                en = row[1].strip()
                if ko and en and ko.lower() not in skip_headers:
                    char_map[ko] = en
    else:
        for line in content.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            for sep in ["→", "->", "=>", "=", ",", ":", "\t"]:
                if sep in line:
                    parts = line.split(sep, 1)
                    ko = parts[0].strip()
                    en = parts[1].strip()
                    if ko and en and ko.lower() not in skip_headers:
                        char_map[ko] = en
                    break

    return char_map


def build_system_prompt(char_map: dict, style_prompt: str, custom_instructions: str) -> str:
    """Assemble full system prompt from base + character map + style + custom instructions."""
    prompt_parts = [BASE_SYSTEM_PROMPT]

    if char_map:
        char_lines = "\n".join([f"  - {ko} → {en}" for ko, en in char_map.items()])
        prompt_parts.append(f"""
## CHARACTER NAME MAPPING — MANDATORY
Replace ALL Korean character names with their English equivalents below.
This applies to: dialogue headers, stage directions, parentheticals, and any mention in the text.
Also adapt natural Korean name usage (e.g., honorifics like "수현아", "서연이 언니") into natural English equivalents.

{char_lines}

Any Korean character name NOT in this list should be romanized using standard romanization.""")

    if style_prompt:
        prompt_parts.append(f"\n## TRANSLATION STYLE\n{style_prompt}")

    if custom_instructions.strip():
        prompt_parts.append(f"\n## ADDITIONAL INSTRUCTIONS\n{custom_instructions.strip()}")

    return "\n".join(prompt_parts)


def read_uploaded_file(uploaded_file) -> str:
    """Read text from uploaded .txt, .pdf, or .docx file."""
    name = uploaded_file.name.lower()

    if name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="replace")

    elif name.endswith(".pdf"):
        try:
            import pymupdf
            pdf_bytes = uploaded_file.read()
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            text_parts = []
            for page in doc:
                text_parts.append(page.get_text())
            doc.close()
            return "\n".join(text_parts)
        except ImportError:
            st.error("PDF 처리를 위해 pymupdf가 필요합니다. requirements.txt를 확인하세요.")
            return ""

    elif name.endswith(".docx"):
        try:
            from docx import Document
            docx_bytes = io.BytesIO(uploaded_file.read())
            doc = Document(docx_bytes)
            return "\n".join([p.text for p in doc.paragraphs])
        except ImportError:
            st.error("DOCX 처리를 위해 python-docx가 필요합니다. requirements.txt를 확인하세요.")
            return ""

    else:
        st.error("지원하지 않는 파일 형식입니다. (.txt / .pdf / .docx)")
        return ""


def split_into_pages(text: str, max_chars: int = MAX_CHARS_PER_PAGE) -> list[str]:
    """Split text into pages, trying to break at scene boundaries."""
    if len(text) <= max_chars:
        return [text]

    pages = []
    remaining = text

    while remaining:
        if len(remaining) <= max_chars:
            pages.append(remaining)
            break

        chunk = remaining[:max_chars]
        scene_pattern = r'\n\s*(?:S\s*#?\s*\d+|씬\s*#?\s*\d+|SCENE\s*\d+|#\s*\d+[\.\)])'
        matches = list(re.finditer(scene_pattern, chunk))

        if matches:
            cut_point = matches[-1].start()
            if cut_point > max_chars * 0.3:
                pages.append(remaining[:cut_point].rstrip())
                remaining = remaining[cut_point:].lstrip("\n")
                continue

        last_break = chunk.rfind("\n\n")
        if last_break > max_chars * 0.3:
            pages.append(remaining[:last_break].rstrip())
            remaining = remaining[last_break:].lstrip("\n")
        else:
            pages.append(chunk)
            remaining = remaining[max_chars:]

    return pages


def translate_page(client, text: str, page_num: int, total_pages: int,
                   model_id: str, max_tokens: int, system_prompt: str) -> str:
    """Translate a single page of screenplay text via Claude API."""
    context = ""
    if total_pages > 1:
        context = f"\n\n[Translator context: This is page {page_num} of {total_pages}. Maintain consistency with previous pages.]"

    message = client.messages.create(
        model=model_id,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": f"Translate the following Korean screenplay into English:{context}\n\n---\n\n{text}"
            }
        ]
    )
    return message.content[0].text


# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────

# Header
st.markdown("""
<div class="main-header">
    <div class="brand-name">B L U E &nbsp; J E A N S &nbsp; P I C T U R E S</div>
    <h1>ENGLISH-TRANSLATOR</h1>
    <div class="tagline">Y O U N G &nbsp; · &nbsp; V I N T A G E &nbsp; · &nbsp; F R E E &nbsp; · &nbsp; I N N O V A T I V E</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# API Key — Streamlit Secrets 우선, 없으면 직접 입력
api_key = st.secrets.get("ANTHROPIC_API_KEY", "")

if api_key:
    st.success("🔑 API Key 연결됨 (Secrets)")
else:
    api_key = st.text_input(
        "🔑 Anthropic API Key",
        type="password",
        help="Claude API 키를 입력하세요. (sk-ant-...) 또는 Streamlit Secrets에 ANTHROPIC_API_KEY를 설정하세요."
    )

# ─── Model Selection ───
st.markdown('<div class="section-header">🤖 MODEL — 번역 모델 선택</div>', unsafe_allow_html=True)

model_choice = st.radio(
    "번역 모델을 선택하세요:",
    list(MODEL_OPTIONS.keys()),
    index=1,
    help="모델에 따라 번역 품질과 비용이 달라집니다."
)
selected_model = MODEL_OPTIONS[model_choice]
st.caption(f"📌 {selected_model['desc']}")

# ─── Character Map ───
st.markdown('<div class="section-header">👤 CHARACTER MAP — 인물표 (한국이름 → 영어이름)</div>', unsafe_allow_html=True)

st.info("💡 CSV 또는 TXT 파일을 업로드하세요. 형식: `한국이름,영어이름` 또는 `한국이름 → 영어이름`")

char_map_file = st.file_uploader(
    "인물표 파일 업로드",
    type=["csv", "txt"],
    help="CSV: 한국이름,영어이름 | TXT: 한국이름 → 영어이름",
    key="char_map_upload"
)

char_map = {}
if char_map_file:
    char_map = parse_character_map(char_map_file)
    if char_map:
        st.success(f"✅ {len(char_map)}명의 인물 매핑 로드 완료")
        table_rows = "".join([
            f"<tr><td>{ko}</td><td>→</td><td><strong>{en}</strong></td></tr>"
            for ko, en in char_map.items()
        ])
        st.markdown(f"""
        <table class="char-table">
            <tr><th>한국이름</th><th></th><th>English Name</th></tr>
            {table_rows}
        </table>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ 인물 매핑을 읽을 수 없습니다. 파일 형식을 확인하세요.")

with st.expander("📋 인물표 파일 예시 보기"):
    st.code("""# CSV 형식 (characters.csv)
한국이름,영어이름
정수현,DANIEL JUNG
김서연,SARAH KIM
박민호,MICHAEL PARK
이지은,GRACE LEE

# TXT 형식 (characters.txt)
정수현 → DANIEL JUNG
김서연 → SARAH KIM
박민호 → MICHAEL PARK
이지은 → GRACE LEE""", language="text")

# ─── Style Selection ───
st.markdown('<div class="section-header">🎨 STYLE — 번역 스타일</div>', unsafe_allow_html=True)

style_choice = st.selectbox(
    "장르/스타일 프리셋을 선택하세요:",
    list(STYLE_PRESETS.keys()),
    index=0,
    help="시나리오 장르에 맞는 번역 톤을 선택합니다."
)
selected_style = STYLE_PRESETS[style_choice]
st.caption(f"📌 {selected_style['desc']}")

custom_instructions = st.text_area(
    "✏️ 추가 번역 지시사항 (선택)",
    height=100,
    placeholder="예: 대사에서 존댓말/반말 구분을 sir/ma'am으로 표현해줘 / 지명은 모두 영어로 바꿔줘 / 특정 용어는 이렇게 번역해줘...",
    help="프리셋 위에 추가로 적용할 지시사항을 자유롭게 입력하세요."
)

# ─── Input Method ───
st.markdown('<div class="section-header">📥 INPUT — 시나리오 입력</div>', unsafe_allow_html=True)

input_method = st.radio(
    "입력 방식을 선택하세요:",
    ["📎 파일 업로드", "📝 텍스트 붙여넣기"],
    horizontal=True,
    label_visibility="visible"
)

source_text = ""

if input_method == "📎 파일 업로드":
    uploaded = st.file_uploader(
        "시나리오 파일을 업로드하세요",
        type=["txt", "pdf", "docx"],
        help=".txt / .pdf / .docx 파일 지원",
        key="screenplay_upload"
    )
    if uploaded:
        with st.spinner("파일 읽는 중..."):
            source_text = read_uploaded_file(uploaded)
        if source_text:
            st.success(f"✅ 파일 로드 완료 — {len(source_text):,}자")
            with st.expander("📄 원문 미리보기", expanded=False):
                st.text(source_text[:3000] + ("..." if len(source_text) > 3000 else ""))

else:
    st.info("💡 시나리오가 길면 여러 페이지로 나눠 붙여넣으세요. '페이지 추가' 버튼을 누르면 입력칸이 추가됩니다.")

    if "paste_pages" not in st.session_state:
        st.session_state.paste_pages = 1

    col_add, col_remove = st.columns([1, 1])
    with col_add:
        if st.button("➕ 페이지 추가", use_container_width=True):
            st.session_state.paste_pages += 1
            st.rerun()
    with col_remove:
        if st.session_state.paste_pages > 1:
            if st.button("➖ 페이지 제거", use_container_width=True):
                st.session_state.paste_pages -= 1
                st.rerun()

    page_texts = []
    for i in range(st.session_state.paste_pages):
        st.markdown(f'<span class="page-chip">Page {i+1}</span>', unsafe_allow_html=True)
        txt = st.text_area(
            f"시나리오 텍스트 (페이지 {i+1})",
            height=250,
            key=f"paste_page_{i}",
            placeholder=f"페이지 {i+1}의 시나리오 텍스트를 붙여넣으세요...",
            label_visibility="collapsed"
        )
        page_texts.append(txt)

    source_text = "\n\n".join([t for t in page_texts if t.strip()])
    if source_text:
        st.caption(f"총 {len(source_text):,}자 입력됨")


# ─── Translate Button ───
st.markdown('<div class="section-header">🔄 TRANSLATE — 번역 실행</div>', unsafe_allow_html=True)

can_translate = bool(api_key and source_text.strip())

if not api_key:
    st.warning("⬆️ API Key를 먼저 입력하세요.")
elif not source_text.strip():
    st.warning("⬆️ 시나리오 텍스트를 입력하세요.")

if can_translate:
    summary_parts = [f"**모델**: {model_choice.split('—')[0].strip()}"]
    if char_map:
        summary_parts.append(f"**인물표**: {len(char_map)}명 매핑")
    summary_parts.append(f"**스타일**: {style_choice.split('—')[0].strip()}")
    if custom_instructions.strip():
        summary_parts.append("**커스텀 지시**: 있음")
    st.caption(" · ".join(summary_parts))

if st.button("🚀 번역 시작", type="primary", disabled=not can_translate, use_container_width=True):

    system_prompt = build_system_prompt(
        char_map=char_map,
        style_prompt=selected_style["prompt"],
        custom_instructions=custom_instructions,
    )

    client = anthropic.Anthropic(api_key=api_key)
    pages = split_into_pages(source_text)
    total = len(pages)

    st.markdown(f'<div class="progress-text">총 {total}페이지로 분할하여 번역합니다...</div>', unsafe_allow_html=True)

    progress_bar = st.progress(0)
    translated_pages = []
    status_area = st.empty()

    for idx, page in enumerate(pages):
        page_num = idx + 1
        status_area.markdown(f'<div class="progress-text">🔄 페이지 {page_num}/{total} 번역 중...</div>', unsafe_allow_html=True)

        try:
            result = translate_page(
                client, page, page_num, total,
                selected_model["id"], selected_model["max_tokens"],
                system_prompt
            )
            translated_pages.append(result)
        except anthropic.APIError as e:
            st.error(f"❌ API 오류 (페이지 {page_num}): {e}")
            break
        except Exception as e:
            st.error(f"❌ 오류 (페이지 {page_num}): {e}")
            break

        progress_bar.progress(page_num / total)

    if len(translated_pages) == total:
        status_area.markdown('<div class="progress-text">✅ 번역 완료!</div>', unsafe_allow_html=True)
        full_translation = "\n\n".join(translated_pages)
        st.session_state["translation_result"] = full_translation

# ─── Output ───
if "translation_result" in st.session_state:
    st.markdown('<div class="section-header">📤 OUTPUT — 번역 결과</div>', unsafe_allow_html=True)

    result = st.session_state["translation_result"]

    st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)

    st.markdown("")
    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "📥 TXT 다운로드",
            data=result.encode("utf-8"),
            file_name="screenplay_translated.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with col2:
        try:
            from docx import Document
            from docx.shared import Pt

            doc = Document()
            style = doc.styles['Normal']
            font = style.font
            font.name = 'Courier New'
            font.size = Pt(12)

            for line in result.split("\n"):
                doc.add_paragraph(line)

            buf = io.BytesIO()
            doc.save(buf)
            buf.seek(0)

            st.download_button(
                "📥 DOCX 다운로드",
                data=buf.getvalue(),
                file_name="screenplay_translated.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        except ImportError:
            st.info("DOCX 출력을 위해 python-docx가 필요합니다.")

# Footer
st.markdown("""
<div class="footer">
    BLUE JEANS PICTURES — English-Translator v1.0<br>
    Powered by Anthropic Claude API
</div>
""", unsafe_allow_html=True)
