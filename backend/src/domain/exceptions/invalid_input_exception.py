from backend.src.domain.exceptions.app_exception import AppException

class InvalidInputException(AppException):
    """
    Exception levée lorsqu'une entrée de requête est invalide.
    Hérite de AppException pour un traitement unifié des erreurs de domaine.
    
    Attributes:
        message: Message lisible pour l'utilisateur.
        code: Code d'erreur spécifique.
        http_status: Code HTTP à retourner.
        details: Détails supplémentaires sur l'erreur (par ex. champs manquants ou invalides).
    """

    def __init__(self, message: str = "Invalid input", details: dict = None):
        super().__init__(message=message, code="INVALID_INPUT", http_status=422)
        self.details = details or {}