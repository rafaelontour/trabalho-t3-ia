-- -- 


-- -- extensão para os acentos:
-- CREATE extension unaccent;

-- SELECT  to_tsvector(unaccent(livros.titulo)) ||
--         to_tsvector(livros.ano::text) ||
--         to_tsvector(unaccent(livros.autor)) ||
--         to_tsvector(unaccent(livros.genero)) ||
--         to_tsquery(unaccent(livros.descricao)) ||
--         to_tsquery((livros.numero_paginas))
     
--     AS document
-- FROM livros

-- -- É importante para o ordenamento dos resultados por relevância, ou seja, os documentos que estiverem
-- -- mais 'adequados' à nossa string de busca terão notas maiores, e estarão no topo da lista.
-- -- Vamos atribuir pesos aos diferentes campos do documento. Nesse caso, 

-- SELECT titulo, ano, autor, genero, descricao, numero_paginas
--        ts_rank(document, to_tsquery('dengue')) AS relevancia
-- FROM (
--  SELECT p.producoes_id as id_artigo,
--         p.nomeartigo AS titulo,
--         setweight(to_tsvector(p.nomeartigo), 'A') ||
--         setweight(to_tsvector(p.anoartigo::text), 'C') ||
--         setweight(to_tsvector(p.issn::text), 'D') ||
--         setweight(to_tsvector(pes.nome), 'B') AS document
--  FROM livros
-- ) busca_textual
-- WHERE busca_textual.document @@ to_tsquery('dengue')
-- ORDER BY relevancia DESC;