import os
import sys
from config.settings import GEMINI_API_KEY
from core_engines.models import NarrativeNode, WorldState, NarrativeDebt, Character, LoreRule
from core_engines.storage_engine import StorageEngine
from core_engines.consistency_engine import ConsistencyEngine
from core_engines.branching_engine import BranchingEngine
from core_engines.stylometric_engine import StylometricEngine


def sahne_yonetim_menusu(mevcut_node, nodes, debts, characters, lore_rules, past_timeline, PROJE_DOSYASI):
    """Sahne yazıldıktan sonra yazarın seçim yapabileceği 8 seçenekli ana kontrol paneli"""
    while True:
        print("\n" + "=" * 50)
        print(f"🎬 MEVCUT SAHNE: {mevcut_node.title}")
        print("=" * 50)
        print("1. Tutarlılık ve Mantık Analizi")
        print("2. Üslup ve Edebi Analiz")
        print("3. Alternatif / Dallanma Motoru")
        print("4. Evrenin Kurallarını Gör")
        print("5. Karakterleri Gör")
        print("6. Sahneyi ve Projeyi Kaydet")
        print("7. Yeni Sahne Yaz")
        print("8. Çıkış")
        print("=" * 50)

        secim = input("Yapmak istediğiniz işlemi seçin (1-8): ").strip()

        if secim == "1":
            print("\n[Analiz] Keskin Gözlü Editör sahnede mantık hataları ve çelişkiler arıyor...")
            anomalies, _, new_debts, scene_time = ConsistencyEngine.analyze_scene(
                current_scene=mevcut_node,
                global_debts=debts,
                raw_chars=characters,
                raw_lore=lore_rules,
                past_timeline=past_timeline
            )
            print(f"\n⏱️  Tahmini Sahne Zamanı / Mekanı: {scene_time}")
            if anomalies:
                print("\n❌ TESPİT EDİLEN TUTARSIZLIKLAR:")
                for anomaly in anomalies:
                    print(f"   - {anomaly}")
            else:
                print("\n✅ Mantık Kontrolü Başarılı: Evren kuralları ve geçmişle bir çelişki bulunamadı.")

            if new_debts:
                print("\n📌 İLERİDE ÇÖZÜLMESİ GEREKEN YENİ GİZEMLER:")
                for debt in new_debts:
                    print(f"   - {debt}")
                    debts.append(
                        NarrativeDebt(
                            debt_id=f"debt_{len(debts) + 1}",
                            category="Gizem",
                            description=debt,
                            is_resolved=False,
                            created_at_node=mevcut_node.node_id
                        )
                    )

        elif secim == "2":
            print("\n[Analiz] Edebi Stil Analisti üslubunuzu inceliyor...")
            style_report = StylometricEngine.analyze_style(content=mevcut_node.content)
            print(f"\n📊 EDEBİ PUANLAMA:")
            print(f"    • Atmosfer ve Betimleme Derinliği : {style_report['atmosphere_score']}/100")
            print(f"    • Anlatıcı Dili ve Diyaloglar    : {style_report['dialogue_score']}/100")
            print(f"    • Sahne Akış Hızı (Tempo)        : {style_report['pacing_score']}/100")
            print(f"\n👁️  Dürüst Editör Eleştirisi:\n    \"{style_report['critique']}\"")
            print("\n💡 Somut Öneriler:")
            for suggestion in style_report['suggestions']:
                print(f"   - {suggestion}")

        elif secim == "3":
            print("\n🌲 DALLANMA MOTORU (Ya Şöyle Olsaydı?)")
            alternatif_secim = input("Karakterin verebileceği alternatif bir karar veya senaryo yazın: ").strip()
            if alternatif_secim:
                print("\n🔮 Alternatif Gelecek Simüle Ediliyor...")
                branch_result = BranchingEngine.simulate_branch(
                    current_node=mevcut_node,
                    alternative_choice=alternatif_secim,
                    raw_chars=characters,
                    raw_lore=lore_rules
                )
                print(f"\n💥 Alternatif Seçimin Evrene Etkisi:\n    \"{branch_result.get('impact_analysis')}\"")
                print("\n📈 Evren Metrik Değişimleri:")
                metrics = branch_result.get('metric_changes', {})
                for k, v in metrics.items():
                    print(f"   • {k}: {v}")
                print("\n🔮 Tetiklenebilecek Olası Gelecek Olaylar:")
                for event in branch_result.get('possible_future_events', []):
                    print(f"   - {event}")

        elif secim == "4":
            print("\n📜 EVRENİN KATI KURALLARI (LORE):")
            if lore_rules:
                for l in lore_rules:
                    desc = l.description if hasattr(l, 'description') else l.get('description', '')
                    print(f"   • {desc}")
            else:
                print("   Sisteme henüz bir evren kuralı tanımlanmamış.")

        elif secim == "5":
            print("\n👥 AKTİF KARAKTERLER VE KARANLIK GEÇMİŞLERİ:")
            if characters:
                for c in characters:
                    name = c.name if hasattr(c, 'name') else c.get('name', 'Bilinmeyen')
                    traits = c.traits if hasattr(c, 'traits') else c.get('traits', [])
                    secrets = c.secrets if hasattr(c, 'secrets') else c.get('secrets', [])
                    print(f"   • {name} | Kişilik: {', '.join(traits)} | Sırlar: {', '.join(secrets)}")
            else:
                print("   Sisteme henüz karakter kartı eklenmemiş.")

        elif secim == "6":
            # Mevcut sahneyi listeye ekleyip diske yazıyoruz (mükerrer kaydı önlemek için kontrol ederek)
            if mevcut_node not in nodes:
                nodes.append(mevcut_node)
            StorageEngine.save_project(
                filename=PROJE_DOSYASI,
                nodes=nodes,
                debts=debts,
                characters=characters,
                lore_rules=lore_rules
            )

        elif secim == "7":
            print("\n[Sistem]: Yeni sahne girişine yönlendiriliyorsunuz...")
            if mevcut_node not in nodes:
                nodes.append(mevcut_node)
            return "yeni_sahne"

        elif secim == "8":
            print("\n====================================================")
            print("         MGPE Sisteminden Güvenle Çıkılıyor.        ")
            print("====================================================")
            sys.exit()
        else:
            print("⚠️ Geçersiz seçim! Lütfen 1-8 arasında bir rakam girin.")


def yeni_sahne_yazma_dongusu(nodes, debts, characters, lore_rules, PROJE_DOSYASI):
    """Temizlenmiş arayüzle kullanıcıdan sahne alan fonksiyon"""
    past_timeline = [n.get("title", "İsimsiz Sahne") if isinstance(n, dict) else n.title for n in nodes]

    print("\n--- YENİ SAHNE GİRİŞİ ---")
    sahne_basligi = input("Sahne Başlığı: ").strip()
    if not sahne_basligi:
        sahne_basligi = f"Sahne #{len(nodes) + 1}"

    print("Sahne İçeriği:")
    sahne_icerigi = input("> ").strip()

    if not sahne_icerigi:
        print("❌ Boş sahne girişi yapılamaz!")
        return

    dunya_durumu = WorldState(metrics={"kaos_seviyesi": "Dinamik"}, active_laws=[])
    mevcut_node = NarrativeNode(
        node_id=f"node_{len(nodes) + 1}",
        title=sahne_basligi,
        content=sahne_icerigi,
        world_state=dunya_durumu
    )

    # Doğrudan 8 seçenekli yönetim menüsünü açıyoruz
    sahne_yonetim_menusu(mevcut_node, nodes, debts, characters, lore_rules, past_timeline, PROJE_DOSYASI)


def main():
    # API Kontrolü
    if not GEMINI_API_KEY or "BURAYA_" in GEMINI_API_KEY:
        print("⚠️ [Sistem Hatası]: config/settings.py içinde geçerli bir API anahtarı yok!")
        return

    PROJE_DOSYASI = "mgpe_proje.json"

    # Arka planda verileri sessizce yüklüyoruz (eski yükleme yazılarını temizledik)
    nodes, debts, characters, lore_rules = StorageEngine.load_project(PROJE_DOSYASI)

    while True:
        print("\n====================================================")
        print("        MGPE İnteraktif Kurgu & Analiz Motoru       ")
        print("====================================================")
        print("1. Yeni Sahne Yaz")
        print("2. Kaydedilen Sahneleri Gör")
        print("3. Çıkış")
        print("====================================================")

        ana_secim = input("Yapmak istediğiniz işlemi seçin (1-3): ").strip()

        if ana_secim == "1":
            yeni_sahne_yazma_dongusu(nodes, debts, characters, lore_rules, PROJE_DOSYASI)
        elif ana_secim == "2":
            print("\n📚 KAYDEDİLEN SAHNELER ZAMAN ÇİZELGESİ:")
            if nodes:
                for idx, n in enumerate(nodes, 1):
                    title = n.get("title", "İsimsiz") if isinstance(n, dict) else n.title
                    print(f"   {idx}. {title}")
            else:
                print("   Henüz kaydedilmiş bir sahne bulunmuyor.")
        elif ana_secim == "3":
            print("\n====================================================")
            print("         MGPE Sisteminden Güvenle Çıkılıyor.        ")
            print("====================================================")
            break
        else:
            print("⚠️ Geçersiz seçim! Lütfen 1-3 arasında bir rakam girin.")


if __name__ == "__main__":
    main()