-- -- Por questões de simplificação, tudo foi realizado no mesmo script. Basta descomentar a parte que deseja executar.


-- -- PARTE 1: CONSTRUINDO O DOCUMENTO:

-- -- Estamos selecionando os campos das tabelas que desejamos, e fazendo uma concatenação de strings. 
-- -- O documento final será uma string com as informações concatenadas.

-- -- SELECT producoes.nomeartigo || ' ' || producoes.anoartigo || ' ' ||
-- -- producoes.issn || ' ' || pesquisadores.nome AS document
-- -- FROM producoes 
-- -- INNER JOIN pesquisadores ON producoes.pesquisadores_id=pesquisadores.pesquisadores_id


-- -- PARTE 2: CRIANDO DOCUMENTO COMO TS_VECTOR:

-- -- Precisamos transformar o documento em um ts_vector, que é um vetor contendo os campos que selecionamos, para que possamos 
-- -- recuperar as informações que desejamos do documento final. Para isso, utilizamos a função to_tsvector(). OBS: essa função só funciona com strings, então
-- -- é preciso converter campos que não são de string, como o anoartigo, que é um inteiro, usando '::text'. 
-- -- A saída desse SQL para cada documento, é um conjunto de lexemas e suas posições no documento.

-- -- SELECT to_tsvector(producoes.nomeartigo ) || to_tsvector(producoes.anoartigo::TEXT) ||
-- -- to_tsvector(producoes.issn) || to_tsvector(pesquisadores.nome) AS document
-- -- FROM producoes
-- -- INNER JOIN pesquisadores ON producoes.pesquisadores_id=pesquisadores.pesquisadores_id


-- -- PARTE 3: REALIZANDO CONSULTAS:

-- -- Agora que sabemos como o documento é montado, agora queremos encontrar o documento que contém aquele 'searh_text' que desejamos.
-- -- Utilizamos a função tsquery() para procurar o lexema que desejamos em um determinado texto. 
-- -- Ex: 
-- -- SELECT to_tsvector('It''s kind of fun to do the impossible') @@ to_tsquery('impossible');
-- -- A função vai retornar 'true' se o lexema esxistir no texto, ou 'false' se o lexema não estiver presente no texto
-- -- É possível usar operadores booleanos dentro da tsquery(), como AND (&), OR (|), NOT(!). Ex: tsquery('! fact');
-- -- Também dá para utilizar ':*' para buscar textos com prefixo específico. Ex: to_tsquery('theo:*');

-- -- Agora vamos usar esses conhecimentos para fazer a consulta nos documentos, como na parte 2:

-- -- SELECT id_artigo, titulo -- recuperamos a coluna peloas aliases
-- -- FROM (
-- --	SELECT producoes.producoes_id AS id_artigo, producoes.nomeartigo AS titulo, -- definimos aliases para as colunas que queremos recuperar
-- --	to_tsvector(producoes.nomeartigo ) || to_tsvector(producoes.anoartigo::text) ||
-- --	to_tsvector(producoes.issn) || to_tsvector(pesquisadores.nome) AS document
-- --	FROM producoes
-- --	INNER JOIN pesquisadores ON producoes.pesquisadores_id=pesquisadores.pesquisadores_id
-- -- ) busca_textual -- alias para o documento select
-- -- WHERE busca_textual.document @@ TO_TSQUERY('Critical & Analysis');


-- -- PARTE 4: SUPORTE A IDIOMAS
-- -- A função to_tsvector() suporta idiomas diferentes, e cada idioma tem as suas regras para montagem dos lexemas: stemming (redução de palavras) e stopwords (palavras ignoradas, como conectivos).
-- -- Vamos adicionar uma coluna de idioma para os artigos, com o default 'english'.

-- -- ALTER TABLE producoes ADD COLUMN idioma TEXT NOT NULL DEFAULT 'english' -- OBS: você pode mudar manualmente a lingua dos artigos depois se quiser. Eu mudei alguns que estão em português para 'portuguese'.

-- -- Vamos reconstruir o documento usando o idioma:

-- -- SELECT TO_TSVECTOR(producoes.idioma::regconfig, producoes.nomeartigo) || to_tsvector(producoes.anoartigo::TEXT) ||
-- -- to_tsvector(producoes.issn) || to_tsvector(pesquisadores.nome) AS document
-- -- FROM producoes
-- -- INNER JOIN pesquisadores ON producoes.pesquisadores_id=pesquisadores.pesquisadores_id

-- -- PARTE 5: ACENTUAÇÃO NOS DOCUMENTOS:
-- -- Podemos usar uma extensão de nome unaccent para remover a acentuação de textos.
-- -- Ex:
-- -- CREATE extension unaccent;
-- -- SELECT unaccent('èéêë');

-- -- Nas buscas nem sempre escrevemos com acento, por isso é importante colocarmos essa regra de recuperação
-- -- do nome do artigo sem acento: 

-- -- SELECT to_tsvector(producoes.idioma::regconfig, unaccent(producoes.nomeartigo)) ||
-- --       to_tsvector(producoes.anoartigo::text) ||
-- --       to_tsvector(producoes.issn::text) ||
-- --      to_tsvector('simple', unaccent(pesquisadores.nome)) AS document
-- -- FROM producoes
-- -- INNER JOIN pesquisadores 
-- --  ON producoes.pesquisadores_id = pesquisadores.pesquisadores_id;


-- -- PARTE 6: CLASSIFICAÇÃO DOS DOCUMENTOS:
-- -- É importante para o ordenamento dos resultados por relevância, ou seja, os documentos que estiverem
-- -- mais 'adequados' à nossa string de busca terão notas maiores, e estarão no topo da lista.
-- -- Vamos atribuir pesos aos diferentes campos do documento. Nesse caso, o nome do artigo terá um peso maior,
-- -- em seguida o nome do pesquisador, o ano do artigo e por último o issn.

-- -- SELECT id_artigo, titulo,
-- --        ts_rank(document, to_tsquery('dengue')) AS relevancia
-- -- FROM (
-- --  SELECT p.producoes_id as id_artigo,
-- --         p.nomeartigo AS titulo,
-- --         setweight(to_tsvector(p.nomeartigo), 'A') ||
-- --         setweight(to_tsvector(p.anoartigo::text), 'C') ||
-- --         setweight(to_tsvector(p.issn::text), 'D') ||
-- --         setweight(to_tsvector(pes.nome), 'B') AS document
-- --  FROM producoes p
-- --  INNER JOIN pesquisadores pes
-- --    ON p.pesquisadores_id = pes.pesquisadores_id
-- -- ) busca_textual
-- -- WHERE busca_textual.document @@ to_tsquery('dengue')
-- -- ORDER BY relevancia DESC;

-- -- PARTE 7: INDEXAÇÃO:
-- -- Por questões de otimização devemos utilizar índices ao fazer a consulta.

-- -- para facilitar as consultas, vamos adicionar uma coluna nova na tabela producoes: 'document' que vai armazenar
-- -- titulo do artigo, issn, ano do artigo e nome do pesquisador:

-- -- ALTER TABLE producoes ADD COLUMN document tsvector;

-- -- UPDATE producoes
-- -- SET document =
-- --    setweight(to_tsvector(nomeartigo), 'A') ||
-- --    setweight(to_tsvector(anoartigo::text), 'C') ||
-- --    setweight(to_tsvector(issn::text), 'D') ||
-- --    setweight(to_tsvector('simple', (SELECT nome FROM pesquisadores WHERE pesquisadores_id = producoes.pesquisadores_id)), 'B');

-- -- agora criamos um índice GIN na coluna 'document' para otimizar as consultas
-- -- CREATE INDEX idx_fts_producoes ON producoes USING gin(document);

-- -- usando trigger para rodar automaticamente a atualização de 'document' quando um artigo for inserido ou atualizado
-- -- CREATE TRIGGER producoes_fts_update
-- -- BEFORE INSERT OR UPDATE ON producoes
-- -- FOR EACH ROW EXECUTE FUNCTION
-- -- tsvector_update_trigger(
-- --    document,
-- --    'pg_catalog.portuguese',
-- --    nomeartigo, anoartigo, issn
-- -- );

-- -- rodando a consulta do document ja com indice:
-- -- SELECT producoes_id, nomeartigo,
-- --       ts_rank(document, to_tsquery('dengue')) AS relevancia
-- -- FROM producoes
-- -- WHERE document @@ to_tsquery('dengue')
-- -- ORDER BY relevancia DESC;

-- -- PARTE 8: ERROS DE ORTOGRAFIA
-- -- às vezes a search_text pode vir com algum erro de ortografia, e a palavra não está exatamente igual ao que aparece no documento. 
-- -- então, usamos uma extensão pg_tgrm
-- -- serve para encontrar uma palavra que é parecida, mas não exatamente igual: 

-- -- CREATE EXTENSION pg_trgm;

-- -- criar uma lista de lexemas únicos:

-- -- DROP MATERIALIZED VIEW IF EXISTS unique_lexeme;

-- -- CREATE MATERIALIZED VIEW unique_lexeme AS
-- -- SELECT word
-- -- FROM ts_stat(
-- --  $$SELECT document FROM public.producoes$$
-- -- );

-- -- criando indice para essa consulta:
-- -- CREATE INDEX words_idx ON unique_lexeme USING gin(word gin_trgm_ops);

-- -- fazendo a consulta usando a similaridade:
-- SELECT word
-- FROM unique_lexeme
-- WHERE similarity(word, 'denge') > 0.5
-- ORDER BY word <-> 'denge'
-- LIMIT 1;

-- -- exemplo sem usar similaridade
-- SELECT producoes_id, nomeartigo
-- FROM producoes
-- WHERE document @@ to_tsquery('dengue');