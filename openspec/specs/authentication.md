# Autenticação do GGReviews

## Arquitetura

O Xano é a fonte de verdade das contas e emite tokens de autenticação. A interface Streamlit chama o grupo de APIs **Authentication** no servidor e mantém o token somente em `st.session_state`. Senhas e tokens não devem ser incluídos em respostas visíveis, logs ou arquivos versionados.

A senha deve ter pelo menos 8 caracteres, incluindo uma letra e um número. O Xano normaliza e-mails para minúsculas e rejeita e-mails duplicados. O logout remove o token da sessão Streamlit; não revoga tokens já emitidos no Xano, que continuam válidos até expirarem (atualmente, 24 horas).

## APIs Xano

Configure `XANO_API_BASE_URL` com a URL base do grupo de APIs **Authentication**, incluindo o identificador do grupo (`canonical` em `xano/api/authentication/authentication.xs`). Exemplo de formato:

```text
https://<instancia-xano>.n7.xano.io/api:ZnpRG7wg
```

Os caminhos abaixo são relativos a essa URL base:

| Método e caminho | Autenticação | Uso |
|---|---|---|
| `POST /auth/signup` | Pública | Recebe `name`, `email` e `password`; cria a conta e retorna `authToken` e `user_id`. |
| `POST /auth/login` | Pública | Recebe `email` e `password`; retorna `authToken` e `user_id` para credenciais válidas. |
| `GET /auth/me` | Bearer token | Retorna os dados permitidos da conta autenticada. |
| `POST /reset/request-reset-link` | Pública | Recebe `email`; retorna a mesma confirmação genérica para e-mails cadastrados ou não cadastrados. |
| `POST /reset/complete` | Pública, com link | Recebe `magic_token`, `email`, `password` e `confirm_password`; valida o link de uso único e atualiza a senha. |

O token retornado por cadastro/login deve ser enviado como `Authorization: Bearer <authToken>` nas chamadas protegidas. O Streamlit não persiste esse token entre sessões.

O endpoint legado `POST /reset/magic-link-login` e `POST /reset/update_password` permanecem disponíveis para a demonstração Xano existente. A aplicação Streamlit usa `/reset/complete`, que valida o link e altera a senha em uma só chamada.

## Configuração local do Streamlit

Instale as dependências e inicie a aplicação:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Defina `XANO_API_BASE_URL` no ambiente do processo ou em `.streamlit/secrets.toml` local:

```toml
XANO_API_BASE_URL = "https://<instancia-xano>.n7.xano.io/api:ZnpRG7wg"
```

Não versione `secrets.toml`; a configuração local está excluída pelo `.gitignore`. Em produção, configure `XANO_API_BASE_URL` no gerenciador de segredos da hospedagem Streamlit.

## Recuperação por e-mail

O Xano envia o link por SendGrid. Configure estas variáveis de ambiente no Xano, sem colocar os respectivos valores no repositório:

| Variável Xano | Valor |
|---|---|
| `sendgrid_api_key` | Chave SendGrid com permissão de envio de e-mail. |
| `sendgrid_from_email` | Endereço remetente verificado no SendGrid. |
| `ggreviews_frontend_url` | URL HTTPS pública da aplicação Streamlit, sem barra final; o Xano acrescenta os parâmetros do link de redefinição. |

O link expira após uma hora e pode ser usado uma única vez. A solicitação de recuperação usa `POST`, para não incluir o e-mail em uma URL. Sem uma conta SendGrid válida, um remetente verificado e a URL pública da interface, o envio de recuperação não funcionará em produção.

## Testes

Execute os testes locais:

```powershell
python -m unittest discover -s tests -v
```

Os testes locais simulam respostas da API. Valide também os endpoints Xano em um ambiente de teste com as variáveis de ambiente configuradas antes de disponibilizar a aplicação.
