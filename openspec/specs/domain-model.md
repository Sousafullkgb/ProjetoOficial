Modelo de domínio # GGReviews - Modelo do Domínio (Xano)

Este documento define a estrutura de dados base de dados no Xano para a plataforma Impacta.

## 1. Entidades (Tabelas no Xano)

### 1.1. User (Utilizadores)
Armazena os dados das pessoas que utilizam a plataforma.
*   **id** (integer): Identificador único do utilizador.
*   **name** (text): Nome de exibição do utilizador.
*   **email** (text): E-mail para login.
*   **password** (password): Palavra-passe armazenada como hash pelo Xano; nunca deve ser exposta em respostas ou logs. Requer pelo menos 8 caracteres, uma letra e um número.
*   **created_at** (timestamp): Data de registo.
*   **password_reset** (object, opcional): Token de redefinição armazenado como hash, prazo de expiração e indicador de uso único.

### 1.2. Game (Jogos)
Armazena o cache/registo dos jogos na nossa base de dados. (Nota: muitos dados virão da API externa, mas guardamos o essencial aqui para relacionar com avaliações).
*   **id** (integer): ID interno no Xano.
*   **external_api_id** (text/integer): O ID do jogo na API externa (ex: IGDB ou RAWG).
*   **title** (text): Nome do jogo.
*   **cover_url** (text): Link para a imagem da capa.

### 1.3. Library (Biblioteca Pessoal)
Relaciona o utilizador com os jogos que ele guardou e o estado atual.
*   **id** (integer): Identificador único.
*   **user_id** (table reference -> User): O utilizador dono do registo.
*   **game_id** (table reference -> Game): O jogo guardado.
*   **status** (text): O estado atual. Valores permitidos: `Jogando`, `Jogados`, `Quero Jogar`.
*   **updated_at** (timestamp): Última vez que o status foi alterado.

### 1.4. Review (Avaliações)
Guarda as notas e os textos que os utilizadores escrevem sobre os jogos.
*   **id** (integer): Identificador único.
*   **user_id** (table reference -> User): O autor da avaliação.
*   **game_id** (table reference -> Game): O jogo avaliado.
*   **rating** (integer/decimal): A nota atribuída (ex: 1 a 5 ou 1 a 10).
*   **review_text** (text): A opinião escrita pelo utilizador (opcional).
*   **created_at** (timestamp): Data em que a avaliação foi publicada.

## 2. Relacionamentos
*   Um **User** pode ter muitos itens na **Library** e muitas **Reviews**.
*   Um **Game** pode estar em várias **Library** e ter muitas **Reviews**.
*   A **Library** e a **Review** funcionam como tabelas intermédias que ligam o *User* ao *Game*.