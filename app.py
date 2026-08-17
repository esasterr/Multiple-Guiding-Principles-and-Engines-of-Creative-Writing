import streamlit as st
from config.settings import GEMINI_API_KEY
from core_engines.models import NarrativeNode, WorldState, NarrativeDebt, Character, LoreRule
from core_engines.storage_engine import StorageEngine
from core_engines.consistency_engine import ConsistencyEngine
from core_engines.branching_engine import BranchingEngine
from core_engines.stylometric_engine import StylometricEngine

# Sayfa Genişlik ve Tema Ayarları
st.set_page_config(page_title="MGPE Kreatif Yazarlık Masası", layout="wide", initial_sidebar_state="expanded")

# Proje Dosyası Tanımı
PROJE_DOSYASI = "mgpe_proje.json"

# API Kontrolü
if not GEMINI_API_KEY or "BURAYA_" in GEMINI_API_KEY:
    st.error("⚠️ [Sistem Hatası]: config/settings.py içinde geçerli bir API anahtarı yok!")
    st.stop()

# 1. Verileri Hafızaya Sessizce Yükleme
if 'nodes' not in st.session_state:
    nodes, debts, characters, lore_rules = StorageEngine.load_project(PROJE_DOSYASI)
    st.session_state.nodes = nodes
    st.session_state.debts = debts
    st.session_state.characters = characters
    st.session_state.lore_rules = lore_rules

# Geçmiş Zaman Çizelgesi Başlıklarını Toplama
past_timeline = [n.title for n in st.session_state.nodes]

# ==========================================
# 🌲 YAN PANEL (SIDEBAR) - EVREN BİLGİLERİ
# ==========================================
with st.sidebar:
    st.title("🌌 MGPE Evren Paneli")
    st.markdown("---")

    # Karakterler Bölümü
    st.subheader("👥 Aktif Karakter Kartları")
    if st.session_state.characters:
        for c in st.session_state.characters:
            with st.expander(f"📌 {c.name}"):
                st.caption(f"**Özellikler:** {', '.join(c.traits)}")
                st.caption(f"**Karanlık Sırlar:** {', '.join(c.secrets)}")
    else:
        st.info("Sisteme henüz karakter eklenmemiş.")

    st.markdown("---")

    # Lore Kuralları Bölümü
    st.subheader("📜 Evren Kuralları (Lore)")
    if st.session_state.lore_rules:
        for l in st.session_state.lore_rules:
            st.markdown(f"• {l.description}")
    else:
        st.info("Sisteme henüz kural eklenmemiş.")

    st.markdown("---")
    # Kaydedilen Sahneler Listesi
    st.subheader("📚 Kayıtlı Sahneler")
    if st.session_state.nodes:
        for idx, n in enumerate(st.session_state.nodes, 1):
            st.text(f"{idx}. {n.title}")
    else:
        st.text("Henüz kayıtlı sahne yok.")

# ==========================================
# 🎭 ANA PANEL - YAZIM VE ANALİZ ALANI
# ==========================================
st.title("✍️ MGPE İnteraktif Kurgu & Analiz Motoru")
st.caption("Yapay zeka metninizi yazmaz; kurgunuzun tutarlılığını korur ve edebi gücünü analiz eder.")

# Yeni Sahne Giriş Alanları
col1, col2 = st.columns([1, 3])
with col1:
    sahne_basligi = st.text_input("Sahne Başlığı", placeholder="Örn: 1. Bölüm - İlk Gece")
with col2:
    # Kullanıcı tetikleyene kadar durumu saklamak için session_state
    if 'scene_time_val' not in st.session_state:
        st.session_state.scene_time_val = "Hesaplanmadı"
    st.markdown(f"<br><p style='color:gray;'>⏱️ <b>Tahmini Zaman/Mekan:</b> {st.session_state.scene_time_val}</p>",
                unsafe_allow_html=True)

sahne_icerigi = st.text_area("Sahne İçeriği", height=250, placeholder="Hikayenizin bu sahnesini buraya yazın...")

# İşlem Butonları Girişi
st.markdown("### 🛠️ Analiz ve Operasyon Masası")
btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)

# Prototip veri sarmallama
dunya_durumu = WorldState(metrics={"kaos_seviyesi": "Dinamik"}, active_laws=[])
mevcut_node = NarrativeNode(
    node_id=f"node_{len(st.session_state.nodes) + 1}",
    title=sahne_basligi if sahne_basligi else f"Sahne #{len(st.session_state.nodes) + 1}",
    content=sahne_icerigi,
    world_state=dunya_durumu
)

# --- 1. MANTIK VE TUTARLILIK ANALİZİ ---
if btn_col1.button("🔍 Tutarlılık ve Mantık Analizi", use_container_width=True):
    if not sahne_icerigi.strip():
        st.warning("Lütfen önce sahne içeriğini yazın.")
    else:
        with st.spinner("Keskin Gözlü Editör çelişkileri arıyor..."):
            anomalies, _, new_debts, scene_time = ConsistencyEngine.analyze_scene(
                current_scene=mevcut_node,
                global_debts=st.session_state.debts,
                raw_chars=st.session_state.characters,
                raw_lore=st.session_state.lore_rules,
                past_timeline=past_timeline
            )
            st.session_state.scene_time_val = scene_time

            st.markdown("#### 🔬 Analiz Sonuçları")
            if anomalies:
                for anomaly in anomalies:
                    st.error(f"❌ {anomaly}")
            else:
                st.success("✅ Harika! Sahne, evren kuralları ve geçmiş kurguyla tamamen tutarlı.")

            if new_debts:
                st.info("📌 **Gelecekte Çözülmesi Gereken Yeni Gizemler:**")
                for debt in new_debts:
                    st.markdown(f"- {debt}")
                    # Hafızaya ekleme
                    st.session_state.debts.append(
                        NarrativeDebt(
                            debt_id=f"debt_{len(st.session_state.debts) + 1}",
                            category="Gizem", description=debt, is_resolved=False, created_at_node=mevcut_node.node_id
                        )
                    )

# --- 2. ÜSLUP VE EDEBİ ANALİZ ---
if btn_col2.button("📊 Üslup ve Edebi Analiz", use_container_width=True):
    if not sahne_icerigi.strip():
        st.warning("Lütfen önce sahne içeriğini yazın.")
    else:
        with st.spinner("Edebi Stil Analisti üslubunuzu inceliyor..."):
            style_report = StylometricEngine.analyze_style(content=mevcut_node.content)

            # Puan tablolarını görsel çubuklarla gösterme
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("Atmosfer ve Betimleme", f"{style_report['atmosphere_score']}/100")
            sc2.metric("Diyalog ve Anlatım Dili", f"{style_report['dialogue_score']}/100")
            sc3.metric("Sahne Akış Hızı (Tempo)", f"{style_report['pacing_score']}/100")

            st.markdown(f"**👁️ Editörün Dürüst Eleştirisi:**")
            st.info(f"\"{style_report['critique']}\"")

            st.markdown("**💡 Somut Öneriler:**")
            for sug in style_report['suggestions']:
                st.markdown(f"- {sug}")

# --- 3. SAHNEYİ KAYDET ---
if btn_col3.button("💾 Sahneyi ve Projeyi Kaydet", use_container_width=True):
    if not sahne_icerigi.strip():
        st.warning("Boş sahne kaydedilemez.")
    else:
        if mevcut_node.title not in [n.title for n in st.session_state.nodes]:
            st.session_state.nodes.append(mevcut_node)

        StorageEngine.save_project(
            filename=PROJE_DOSYASI,
            nodes=st.session_state.nodes,
            debts=st.session_state.debts,
            characters=st.session_state.characters,
            lore_rules=st.session_state.lore_rules
        )
        st.success("💾 Sahne başarıyla kaydedildi ve evren veri tabanına işlendi!")
        st.rerun()

# --- 4. YENİ TEMİZ SAYFA ---
if btn_col4.button("🧹 Ekranı Temizle / Yeni Sahne", use_container_width=True):
    st.rerun()

# ==========================================
# 🌲 DALLANMA MOTORU (YA ŞÖYLE OLSAYDI?)
# ==========================================
st.markdown("---")
st.subheader("🌲 Dallanma Motoru Matrisi")
alternatif_secim = st.text_input(
    "Karakterinizin bu sahnede verebileceği alternatif bir karar veya farklı bir olay kurgusu yazın:")

if st.button("🔮 Alternatif Geleceği Simüle Et", use_container_width=False):
    if not sahne_icerigi.strip() or not alternatif_secim.strip():
        st.warning("Lütfen hem sahne içeriğini hem de simüle edilecek alternatif yolu doldurun.")
    else:
        with st.spinner("Olasılık matrisleri hesaplanıyor..."):
            branch_result = BranchingEngine.simulate_branch(
                current_node=mevcut_node,
                alternative_choice=alternatif_secim,
                raw_chars=st.session_state.characters,
                raw_lore=st.session_state.lore_rules
            )

            st.markdown(f"**💥 Alternatif Seçimin Evrene Etkisi:**")
            st.warning(f"\"{branch_result.get('impact_analysis')}\"")

            mc1, mc2 = st.columns(2)
            metrics = branch_result.get('metric_changes', {})
            mc1.info(f"📈 **Karakter İlişkileri:** {metrics.get('karakter_ilişkileri', 'Değişim Yok')}")
            mc2.info(f"🔥 **Kaos Seviyesi:** {metrics.get('kaos_seviyesi', 'Değişim Yok')}")

            st.markdown("**🔮 Tetiklenebilecek Olası Gelecek Olay Düğümleri:**")
            for event in branch_result.get('possible_future_events', []):
                st.markdown(f"- {event}")