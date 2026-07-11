
from prompts.book_recomendation import BOOK_RECOMMENDATION

class BookRecommendationBuilder:
    """
    Classe responsável por gerir o fluxo de recomendação de livros.
    """

    def __init__(self):
        
        self.final_prompt = BOOK_RECOMMENDATION

    def stream_build(self, user_message: str): 
        """
        Função que executa a pipeline de geração da resposta de recomendação dos livros. 
        """

        # Etapa 1: processar a pergunta do usuário:
        # chamar um método que faz algum tratamento na pergunta. Ex: remover stopwords, pegar palavras-chave,
        # pedir pra o modelo melhorar a pergunta
        # retornar as palavras chaves da pergunta para montar a query.


        # Etapa 2: recuperar os documentos usando RAG
        

        # Etapa : fazer a injeção do contexto no prompt. 
        # substituir no prompt os placeholders:  catalogo_livros e pergunta_usuario

