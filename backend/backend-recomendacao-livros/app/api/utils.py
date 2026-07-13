import logging
import sys

from dataclasses import dataclass

def get_logger(name: str = "app_logger") -> logging.Logger: 

    logger = logging.getLogger(name)

    logger.setLevel(logging.INFO)

    # Handler: Envia para o console (Terminal)
    stdout_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(stdout_handler)

    return logger

@dataclass
class Book:

    title: str
    author: str
    year: int
    number_of_pages: int
    book_description: str
    category: str

    def to_prompt_format(self) -> str:
        """Formata os dados do livro de um jeito que o LLM entenda perfeitamente."""
        return (
            f"Título: {self.title}\n"
            f"Autor: {self.author} ({self.year})\n"
            f"Categoria: {self.category}\n"
            f"Descrição: {self.book_description}"
        )
    
    def normalize_category(self) -> str:
        """Normaliza o nome da categoria para retorno da resposta final."""

        value = self.category.upper().strip()

        if value in ('ROMANCE', 'FANTASIA', 'TERROR', 'SUSPENSE', 'INFANTIL', 'POEMA','BIOGRAFIA',): 
            return value.lower()
        elif value ==  'FICCAO':
            return "ficção"
        elif value == 'CLASSICO':
            return "clássico"
        elif value ==  'CIENCIA': 
            return "ciência"
        else:
            return value.lower()
        
@dataclass
class BookRecommendationResult: 

    response: str
    retrieved_books: list[Book]