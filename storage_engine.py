import json
import os
# main.py içindeki nesne yapılarıyla eşitlemek için modelleri içe aktarıyoruz
from .models import NarrativeNode, GlobalDebt, Character, LoreRule


class StorageEngine:
    """Proje verilerini, Karakterleri, Lore kurallarını ve İlişkileri diskte saklayan esnek motor"""

    @staticmethod
    def save_project(filename: str, nodes: list, debts: list, characters: list, lore_rules: list):
        """Tüm evreni eksiksiz şekilde JSON olarak kaydeder"""

        formatted_chars = []
        for c in characters:
            if hasattr(c, 'name'):
                formatted_chars.append({
                    "name": c.name,
                    "traits": c.traits,
                    "secrets": c.secrets,
                    "relationships": getattr(c, 'relationships', {})
                })
            elif isinstance(c, dict):
                formatted_chars.append({
                    "name": c.get('name'),
                    "traits": c.get('traits'),
                    "secrets": c.get('secrets'),
                    "relationships": c.get('relationships', {})
                })

        formatted_lore = []
        for l in lore_rules:
            if hasattr(l, 'rule_id'):
                formatted_lore.append({"rule_id": l.rule_id, "description": l.description})
            elif isinstance(l, dict):
                formatted_lore.append({"rule_id": l.get('rule_id'), "description": l.get('description')})

        project_data = {
            "nodes": [{"node_id": n.node_id, "title": n.title, "content": n.content} for n in nodes],
            "debts": [
                {
                    "debt_id": d.debt_id, "category": d.category,
                    "description": d.description, "is_resolved": d.is_resolved,
                    "created_at_node": d.created_at_node
                } for d in debts
            ],
            "characters": formatted_chars,
            "lore_rules": formatted_lore
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=4)
        print(f"\n💾 [Sistem]: Projeniz, karakterler ve kurallarla birlikte '{filename}' dosyasına kaydedildi!")

    @staticmethod
    def load_project(filename: str) -> tuple:
        """Kayıtlı projeyi geri yükler ve ham verileri model nesnelerine dönüştürür"""
        if not os.path.exists(filename):
            print(f"\n⚠️ [Sistem]: Kayıt dosyası bulunamadı. Sıfır proje açılıyor.")
            return [], [], [], []

        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Ham sözlük verilerini main.py'ın beklediği nesne kalıplarına dönüştürüyoruz
        loaded_nodes = []
        for n in data.get("nodes", []):
            node = NarrativeNode(node_id=n.get("node_id"), title=n.get("title"), content=n.get("content"))
            loaded_nodes.append(node)

        loaded_debts = []
        for d in data.get("debts", []):
            debt = GlobalDebt(
                debt_id=d.get("debt_id"),
                category=d.get("category"),
                description=d.get("description"),
                is_resolved=d.get("is_resolved", False),
                created_at_node=d.get("created_at_node")
            )
            loaded_debts.append(debt)

        loaded_chars = []
        for c in data.get("characters", []):
            char = Character(
                name=c.get("name"),
                traits=c.get("traits", []),
                secrets=c.get("secrets", [])
            )
            if hasattr(char, 'relationships'):
                char.relationships = c.get("relationships", {})
            loaded_chars.append(char)

        loaded_lore = []
        for l in data.get("lore_rules", []):
            lore = LoreRule(rule_id=l.get("rule_id"), description=l.get("description"))
            loaded_lore.append(lore)

        print(f"\n📂 [Sistem]: '{filename}' başarıyla yüklendi! Bellek nesneleri ayağa kaldırıldı.")
        return loaded_nodes, loaded_debts, loaded_chars, loaded_lore