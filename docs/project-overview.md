VISÃO GERAL # GGReviews — Visão Geral do Projeto

## 1. Objetivo

O GGReviews é uma plataforma web de descoberta, organização e avaliação de jogos eletrônicos, inspirada em plataformas como Letterboxd e Metacritic.

O objetivo é permitir que usuários encontrem jogos, organizem suas bibliotecas pessoais, atribuam notas e compartilhem suas opiniões por meio de reviews.

## 2. Público-alvo

Pessoas que jogam videogames e desejam organizar os jogos que estão jogando, os que já jogaram e aqueles que pretendem jogar, além de consultar e publicar avaliações.

## 3. Funcionalidades principais

### 3.1. Busca de jogos
- Permitir que usuários pesquisem jogos.
- Apresentar informações disponíveis sobre cada jogo.
- Permitir acessar os detalhes de um jogo selecionado.

### 3.2. Biblioteca pessoal
- Permitir que usuários organizem jogos em sua biblioteca.
- Disponibilizar os seguintes status:
  - Jogando;
  - Jogados;
  - Lista de desejos.
- Permitir consultar os jogos organizados por status.

### 3.3. Avaliações
- Permitir que usuários atribuam notas aos jogos.
- Permitir que usuários escrevam reviews sobre os jogos.
- Associar as avaliações ao usuário e ao jogo correspondente.

### 3.4. Detalhes do jogo
- Apresentar as informações disponíveis sobre o jogo.
- Permitir consultar as avaliações e reviews relacionadas ao jogo, conforme as regras que forem definidas.

## 4. Diretrizes tecnológicas

- Linguagem principal: Python.
- Frontend: Streamlit.
- OpenSpec: gerenciamento de especificações e desenvolvimento incremental.
- Xano: integração com o backend, caso seja confirmado como a plataforma responsável pelos dados e pelas APIs.

## 5. Princípios de desenvolvimento

O desenvolvimento deverá ser incremental. Antes de implementar funcionalidades, o contexto do projeto deverá ser analisado para identificar módulos, dependências, dúvidas e decisões arquiteturais pendentes.

Cada mudança deverá ser planejada e revisada antes de sua implementação.

## 6. Decisões pendentes

- Definir a fonte dos dados dos jogos.
- Definir se haverá cadastro e login de usuários e como serão implementados.
- Definir a escala de notas.
- Definir se cada usuário poderá publicar uma única review por jogo ou várias.
- Definir se as notas e reviews serão públicas.
- Definir se haverá cálculo de nota média dos usuários.
- Definir se haverá integração com notas profissionais ou agregadores externos.
- Definir o modelo de permissões e a gestão dos dados.
- Confirmar o papel do Xano na arquitetura final.

## 7. Arquitetura Tecnológica (Stack)

*   **Frontend / Interface:** Streamlit (Python)
*   **Banco de Dados/BackEnd / APIs Base:** Xano
*   **Inteligência Artificial:** Google Gemini