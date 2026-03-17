"""
BLUE JEANS PICTURES — English-Translator
한국어 시나리오 → 영어 번역 (구조 보존)
Powered by Anthropic Claude API
"""

import streamlit as st
import anthropic
import re
import io
import time

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
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap');

/* Header */
.main-header {
    text-align: center;
    padding: 1.5rem 0 0.5rem 0;
}
.main-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    color: #191970;
    margin-bottom: 0.2rem;
    letter-spacing: 0.02em;
}
.main-header .subtitle {
    font-size: 0.95rem;
    color: #888;
    letter-spacing: 0.05em;
}
.brand-tag {
    text-align: center;
    font-size: 0.75rem;
    color: #bbb;
    margin-top: 0.2rem;
    letter-spacing: 0.1em;
}

/* Section headers */
.section-header {
    background: linear-gradient(90deg, #f5c842 0%, #f5c842 100%);
    color: #191970;
    padding: 0.45rem 1rem;
    border-radius: 6px;
    font-weight: 700;
    font-size: 0.95rem;
    margin: 1.2rem 0 0.8rem 0;
    letter-spacing: 0.03em;
}

/* Result box */
.result-box {
    background: #fafafa;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 1.2rem;
    font-family: 'Courier New', monospace;
    font-size: 0.88rem;
    line-height: 1.7;
    white-space: pre-wrap;
    max-height: 600px;
    overflow-y: auto;
}

/* Page chip */
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

/* Progress */
.progress-text {
    text-align: center;
    color: #666;
    font-size: 0.85rem;
    padding: 0.5rem 0;
}

/* Footer */
.footer {
    text-align: center;
    color: #ccc;
    font-size: 0.72rem;
    margin-top: 2rem;
    padding: 1rem 0;
    border-top: 1px solid #eee;
    letter-spacing: 0.05em;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
MAX_CHARS_PER_PAGE = 8000  # ~4000 Korean chars ≈ safe for one API call

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

SYSTEM_PROMPT = """You are an expert Korean-to-English screenplay translator for the international film market.

## RULES — ABSOLUTE
1. **Preserve ALL structural formatting exactly:**
   - Scene headers (S#, 씬, SCENE numbers) → keep numbering, translate location/time
   - Parenthetical directions: (O.L.), (E), (NA), CUT TO, FADE IN, etc. → keep as-is or use standard English equivalents
   - Character name lines → keep names in their original form (romanized if Korean)
   - Stage directions / 지문 → translate into professional English action lines
   - Dialogue → translate into natural, cinematic English dialogue
   - Line breaks, indentation patterns, blank lines → preserve exactly

2. **Translation quality:**
   - Produce **professional, production-grade English** suitable for international co-production packages
   - Dialogue must sound natural and spoken — not literary or stiff
   - Action lines must be vivid, present-tense, visual — standard screenplay style
   - Preserve the emotional tone, subtext, and rhythm of the original
   - Cultural references: adapt only when necessary for clarity; keep Korean proper nouns

3. **DO NOT:**
   - Add scene numbers or formatting that doesn't exist in the original
   - Remove any structural element
   - Add commentary, notes, or explanations
   - Merge or split scenes
   - Change character names unless they are purely descriptive Korean titles (translate those)

4. **Output ONLY the translated screenplay text.** No preamble, no closing remarks."""

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

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
        # Try to find a scene break (S#, 씬, SCENE, #.) near the end
        scene_pattern = r'\n\s*(?:S\s*#?\s*\d+|씬\s*#?\s*\d+|SCENE\s*\d+|#\s*\d+[\.\)])'
        matches = list(re.finditer(scene_pattern, chunk))

        if matches:
            # Cut at the last scene header found
            cut_point = matches[-1].start()
            if cut_point > max_chars * 0.3:  # Only if reasonably far in
                pages.append(remaining[:cut_point].rstrip())
                remaining = remaining[cut_point:].lstrip("\n")
                continue

        # Fallback: cut at last double newline
        last_break = chunk.rfind("\n\n")
        if last_break > max_chars * 0.3:
            pages.append(remaining[:last_break].rstrip())
            remaining = remaining[last_break:].lstrip("\n")
        else:
            # Hard cut
            pages.append(chunk)
            remaining = remaining[max_chars:]

    return pages


def translate_page(client, text: str, page_num: int, total_pages: int, model_id: str, max_tokens: int) -> str:
    """Translate a single page of screenplay text via Claude API."""
    context = ""
    if total_pages > 1:
        context = f"\n\n[Translator context: This is page {page_num} of {total_pages}. Maintain consistency with previous pages.]"

    message = client.messages.create(
        model=model_id,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
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
    <h1>🎬 English-Translator</h1>
    <div class="subtitle">KOREAN → ENGLISH — Structure-Preserving Translation</div>
</div>
<div class="brand-tag">BLUE JEANS PICTURES</div>
""", unsafe_allow_html=True)

st.markdown("---")

# API Key
api_key = st.text_input(
    "🔑 Anthropic API Key",
    type="password",
    help="Claude API 키를 입력하세요. (sk-ant-...)"
)

# Model Selection
st.markdown('<div class="section-header">🤖 MODEL — 번역 모델 선택</div>', unsafe_allow_html=True)

model_choice = st.radio(
    "번역 모델을 선택하세요:",
    list(MODEL_OPTIONS.keys()),
    index=1,  # default: Sonnet
    help="모델에 따라 번역 품질과 비용이 달라집니다."
)
selected_model = MODEL_OPTIONS[model_choice]
st.caption(f"📌 {selected_model['desc']}")

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
        help=".txt / .pdf / .docx 파일 지원"
    )
    if uploaded:
        with st.spinner("파일 읽는 중..."):
            source_text = read_uploaded_file(uploaded)
        if source_text:
            st.success(f"✅ 파일 로드 완료 — {len(source_text):,}자")
            with st.expander("📄 원문 미리보기", expanded=False):
                st.text(source_text[:3000] + ("..." if len(source_text) > 3000 else ""))

else:  # 텍스트 붙여넣기
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

if st.button("🚀 번역 시작", type="primary", disabled=not can_translate, use_container_width=True):

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
            result = translate_page(client, page, page_num, total, selected_model["id"], selected_model["max_tokens"])
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

        # Store in session state
        st.session_state["translation_result"] = full_translation

# ─── Output ───
if "translation_result" in st.session_state:
    st.markdown('<div class="section-header">📤 OUTPUT — 번역 결과</div>', unsafe_allow_html=True)

    result = st.session_state["translation_result"]

    # Display
    st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)

    # Download buttons
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
            from docx.shared import Pt, Inches
            from docx.enum.text import WD_ALIGN_PARAGRAPH

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
