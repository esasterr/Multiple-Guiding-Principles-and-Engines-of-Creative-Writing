from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class WorldState(BaseModel):
    metrics: Dict[str, Any] = {}
    active_laws: List[str] = []

class NarrativeNode(BaseModel):
    node_id: str
    title: str
    content: str
    world_state: Optional[WorldState] = None

class NarrativeDebt(BaseModel):
    debt_id: str
    category: str
    description: str
    is_resolved: bool = False
    created_at_node: str
    resolved_at_node: Optional[str] = None

# KRİTİK GÜNCELLEME: GlobalDebt uyuşmazlığını önlemek için takma isim (alias) tanımlıyoruz
GlobalDebt = NarrativeDebt

class Character(BaseModel):
    """Karakterlerin psikolojik profillerini, sırlarını ve bağlarını tutan Pydantic kart yapısı"""
    name: str = Field(description="Karakterin adı")
    traits: List[str] = Field(default=[], description="Karakterin kişilik özellikleri")
    secrets: List[str] = Field(default=[], description="Karakterin karanlık geçmişi ve sırları/günahları")
    relationships: Dict[str, Any] = Field(default={}, description="Diğer karakterlerle olan bağları ve güven seviyeleri")

class LoreRule(BaseModel):
    """Evrenin fantastik veya gerçekçi katı kuralları"""
    rule_id: str
    description: str