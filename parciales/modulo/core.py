import logging
import re
class CoreAgent:
    """
    Clase para generar sugerencias de código basadas en patrones dados.
    """

    def __init__(self, suggestion_patterns: list[str] = None):
        self.suggestion_patterns = suggestion_patterns or []
        self.decision_log = []

    def _generate_suggestions(self, code: str) -> list[str]:
        suggestions = []

        for pattern in self.suggestion_patterns:
            # Usar set para evitar duplicados
            matches = {match.group() for match in re.finditer(pattern, code, re.MULTILINE)}
            
            # Convertir el set a una lista antes de agregarla a las sugerencias
            suggestions.extend(list(matches))

        return list(suggestions)
    
    def _log_decision(self, decision: str):
        self.decision_log.append({
            "code": decision,
            "suggestions": [str(match) for match in decision]
        })
        
    def generate_suggestions_with_logging(self, code: str):
        try:
            suggestions = self._generate_suggestions(code)
            self._log_decision(suggestions)
            return suggestions
        except Exception as e:
            logging.error(f"Error generating suggestions: {str(e)}")
            raise

# Ejemplo de uso:
core_agent = CoreAgent(suggestion_patterns=["def foo", "class Bar"])
suggestions = core_agent.generate_suggestions_with_logging("def foo() -> None:\n    print('Hello, world')")
print(suggestions)
print(core_agent.decision_log)



