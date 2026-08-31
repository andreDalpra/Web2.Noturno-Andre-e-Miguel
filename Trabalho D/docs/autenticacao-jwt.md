# Autenticação JWT / Bearer

## Arquivos e responsabilidades

| Arquivo | Alteração | Responsabilidade |
| --- | --- | --- |
| `main.py` | JWT, `OAuth2PasswordBearer`, `/login`, `/auth/login`, `get_current_user` e proteção de rotas | Autentica credenciais, cria/valida tokens e aplica autorização. |
| `schemas.py` | `Token`, `TokenData` e schema de review compatível | Define os contratos de token e impede que o `user_id` enviado determine o dono da review. |
| `models.py` | Campo de senha com até 255 caracteres | Comporta hashes Argon2. |
| `frontend/src/main.jsx` | Armazena token e envia `Authorization: Bearer` | Mantém o frontend compatível com as rotas protegidas. |
| `requirements.txt` | PyJWT, pwdlib com Argon2 e python-multipart | Declara dependências da autenticação. |
| `.env` | `JWT_SECRET_KEY` | Guarda a chave que assina os JWTs fora do código-fonte. |
| `.env.example` | Variável de ambiente documentada | Modelo seguro para outra máquina. |

## Bibliotecas

- **PyJWT**: assina e decodifica tokens JWT usando HS256.
- **pwdlib[argon2]**: gera e verifica hashes seguros de senha com Argon2.
- **OAuth2PasswordBearer** (FastAPI): extrai `Authorization: Bearer <token>` e registra o esquema no OpenAPI/Swagger.
- **python-multipart**: permite o formulário OAuth2 usado por `POST /login` no Swagger.

## Fluxo

```text
Usuário → POST /login (usuário/e-mail + senha)
        → banco de dados
        → verificação do hash Argon2
        → JWT { sub: id do usuário, exp: expiração }
        → access_token
        → Authorization: Bearer <access_token>
        → get_current_user()
        → valida assinatura, expiração e usuário
        → endpoint protegido
```

`sub` contém o ID do usuário, e `exp` expira após 60 minutos. Um token ausente,
inválido, expirado ou associado a usuário removido retorna `401 Unauthorized`.

## Senhas existentes

Novos usuários recebem hash Argon2, nunca senha em texto puro. As contas já
existentes são compatíveis: no primeiro login válido, a senha antiga é conferida
uma única vez e substituída imediatamente pelo hash. Assim, não é necessário
recriar as contas existentes.

## Endpoints

| Método | Endpoint | Autenticação | Motivo |
| --- | --- | --- | --- |
| POST | `/users` | Não | Cadastro público. |
| GET | `/users` | Não | Consulta pública usada para exibir autores. |
| GET | `/users/me` | Sim | Retorna o perfil do token atual. |
| GET | `/users/{user_id}` | Não | Consulta pública de usuário. |
| PUT | `/users/{user_id}` | Sim, dono | Apenas a própria conta pode ser alterada. |
| DELETE | `/users/{user_id}` | Sim, dono | Apenas a própria conta pode ser excluída. |
| POST | `/login` | Não | Login OAuth2 para Swagger; recebe formulário. |
| POST | `/auth/login` | Não | Login JSON mantido para o React. |
| POST | `/ratings` | Sim | A review é associada ao ID do token. |
| GET | `/ratings` | Não | Consulta pública. |
| GET | `/feed` | Não | Feed público. |
| GET | `/ratings/{rating_id}` | Não | Consulta pública. |
| GET | `/ratings/user/id/{user_id}` | Não | Consulta pública. |
| GET | `/ratings/user/nickname/{nickname}` | Não | Consulta pública. |
| GET | `/ratings/music/{music_id}` | Não | Consulta pública. |
| PUT | `/ratings/{rating_id}` | Sim, dono | Apenas o autor pode editar. |
| DELETE | `/ratings/{rating_id}` | Sim, dono | Apenas o autor pode excluir. |
| GET | `/spotify/music/search` | Não | Busca pública via backend. |
| GET | `/spotify/music/id/{music_id}` | Não | Consulta pública via backend. |
| GET | `/spotify/music/artists/{music_id}` | Não | Consulta pública via backend. |

## Teste no Swagger

1. Execute `python -m pip install -r requirements.txt`.
2. Inicie: `python -m uvicorn main:app --reload`.
3. Abra `http://127.0.0.1:8000/docs`.
4. Crie uma conta com `POST /users`, se necessário.
5. Abra `POST /login`, clique em **Try it out** e informe `username` (apelido ou e-mail) e `password` no formulário.
6. Execute; a resposta terá `access_token`.
7. Clique em **Authorize**. O Swagger também pode solicitar as credenciais diretamente pelo fluxo OAuth2. Se for solicitado um token, informe somente o JWT, sem escrever `Bearer` duas vezes.
8. Execute `POST /ratings`. O cadeado indica que o token foi enviado.
9. Sem autorizar, a mesma requisição retorna `401`. Com texto aleatório no token, também retorna `401`.

## Exemplos

### Login JSON (usado pelo frontend)

```http
POST /auth/login
Content-Type: application/json

{
  "identifier": "miguel",
  "password": "123456"
}
```

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Login OAuth2 (Swagger)

```http
POST /login
Content-Type: application/x-www-form-urlencoded

username=miguel&password=123456
```

### Criar review protegida

```http
POST /ratings
Authorization: Bearer eyJ...
Content-Type: application/json

{
  "music_id": "3n3Ppam7vgaVa1iaRUc9Lp",
  "rating": 4.5,
  "description": "Ótima música"
}
```

O servidor ignora qualquer `user_id` enviado no JSON e usa o usuário obtido pelo
token. Por isso o frontend não é responsável pela segurança: ele apenas envia o
token; a API sempre verifica assinatura, validade e propriedade da review.

## Conceitos para apresentação

- **Autenticação** confirma quem é o usuário (login e senha).
- **Autorização** decide o que ele pode fazer (editar somente a própria review).
- **JWT** é um token assinado, com dados como `sub` e data de expiração.
- **Bearer Token** é o JWT enviado pelo cabeçalho `Authorization` com o prefixo `Bearer`.
- **OAuth2PasswordBearer** informa ao FastAPI como ler esse cabeçalho e faz o Swagger mostrar o botão **Authorize**.
- **Depends** injeta `get_current_user()` nas rotas; assim toda rota protegida executa a validação antes da lógica de negócio.
