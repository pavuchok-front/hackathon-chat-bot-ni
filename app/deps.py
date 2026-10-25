from app.services.dialog import DialogEngine
from app.services.kb import KnowledgeBase

kb = KnowledgeBase()
engine = DialogEngine(kb)
