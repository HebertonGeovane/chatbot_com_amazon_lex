## 🦷 DentistBot – Chatbot com Amazon Lex V2

### O DentistBot é um chatbot construído com Amazon Lex V2 para auxiliar no agendamento de consultas odontológicas. Ele combina processamento de linguagem natural (PLN), Lambda, Cognito e S3 para criar uma aplicação completa de chatbot acessível pela web.

## Arquitetura 

![image - 2025-09-14T092256 456](https://github.com/user-attachments/assets/805886f9-f0bc-404c-b7cb-a860030c78c5)

| Serviço | Preço | Exemplo de Custo |
|---|---|---|
| Amazon Lex | Cobrado por solicitação de texto ou voz. Texto: `$0.004` por solicitação. Voz: `$0.0065` por solicitação. | `10.000` requisições de texto/mês = `$40/mês` |
| AWS Lambda | Baseado em invocações e tempo de execução. `1 milhão` de invocações grátis/mês. | `10.000` chamadas de 1s (128MB) = `≈ $0.02/mês` |
| Amazon S3 | Armazenamento (`$0.023`/GB/mês) + requisições (`$0.0004`/1k GET) + transferência. | Site de `100MB` e `10.000` acessos/mês = `≈ $0.01/mês` |
| Amazon Cognito | Grátis para os primeiros `50.000` usuários ativos mensais. Depois, `$0.0055` por usuário. | `1.000` usuários logados/mês = `$0.00` (dentro da cota) |

## ⚠️ Verifique suas Permissões ⚠️

 ## 1️⃣ **IAM**
- Criar Role LexRole
  - Roles → Create role
  - AWS service → Use case `Lambda` → Next

<img width="1118" height="746" alt="image" src="https://github.com/user-attachments/assets/3a999363-376d-4d76-9cc9-b24ff4290144" />

  - Add permissions → Next
  - Name, review, and create →  Role name `LexRole`
  - Create role
  - Permissions →  create inline policy

<img width="1498" height="375" alt="image" src="https://github.com/user-attachments/assets/4763d332-87f6-4347-8f81-998a1e9b46de" />
  
   - json
 
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:<Seu-AWS-Region>:<Seu-Account-ID>:log-group:/aws/lambda/MakeAppointmentCodeHook:*", 
            "Effect": "Allow"
        },
        {
            "Action": [
                "lambda:InvokeFunction",
                "lambda:GetFunction"
            ],
            "Resource": "arn:aws:lambda:<Seu-AWS-Region>:<Seu-Account-ID>:function:MakeAppointmentCodeHook",
            "Effect": "Allow"
        }
    ]
}
```
   - Policy name  → `LexCustomPolicy` → Create policy

## 2️⃣ **Lambda**

- Criar uma função do AWS Lambda
  - no painel do lambda `Create function`
  - Use a blueprint → Blueprint name `Make an appointment with Lex`
  - Function name `MakeAppointmentCodeHook`
  - Use an existing role `LexRole`
  - Create function
<img width="1284" height="742" alt="image" src="https://github.com/user-attachments/assets/4b4157cb-e246-46ff-9bd4-80937f1b528a" />
<img width="836" height="400" alt="image" src="https://github.com/user-attachments/assets/edc1ada5-c7d4-461c-8961-c2d6c57cc16e" />

 
   - Copie o código lambda_function.py e cole-o no editor de código para substituir o código existente e escolha Implantar
<img width="1862" height="781" alt="image" src="https://github.com/user-attachments/assets/74e30a7d-353c-489e-b8cf-c57a74db8ec3" />

## 3️⃣ criar e configurar o bot com o **Amazon Lex**

   - Acesse o Amazon Lex → Create bot
     - Creation method → Start with an example
     - Example bot → MakeAppointment
     - Bot name → DentistBot
     - IAM permissions → Create a role with basic Amazon Lex permissions. ou Use an existing role
     - Children’s Online Privacy Protection Act (COPPA) → No → Next
     - Language: English (US) → Done
     - Na próxima tela no final da sessão
     - Code hooks - optional → Marque Use a Lambda function for initialization and validation
     - Save intent

<img width="998" height="639" alt="image" src="https://github.com/user-attachments/assets/294217ac-7447-49f5-abc8-bb823c049558" />

<img width="656" height="553" alt="image" src="https://github.com/user-attachments/assets/c803db0e-1b03-4158-a93e-f3839c977c4b" />

<img width="995" height="495" alt="image" src="https://github.com/user-attachments/assets/4256d2e6-aa5f-4dab-9353-f5e5281e2f2c" />

<img width="1001" height="255" alt="image" src="https://github.com/user-attachments/assets/876befef-fe68-400a-a8eb-6b74841cb2b2" />

<img width="984" height="204" alt="image" src="https://github.com/user-attachments/assets/4582107b-4007-4ff6-9cfb-f5abd1654931" />

<img width="1005" height="242" alt="image" src="https://github.com/user-attachments/assets/2f32e11f-de38-4e21-8f67-6a85dfe6f241" />

<img width="999" height="221" alt="image" src="https://github.com/user-attachments/assets/8da76c2b-176e-4afa-8839-127e7995b2f4" />



 associar a função **Lambda** ao **bot**
 
  - No console Amazon Lex, escolha Bots
     - DentistBot
     - Create versions and aliases for deployment → View aliases
     - TestBotAlias → Language Status English (US) → Alias language support: English (US) → MakeAppointmentCodeHook → $LATEST
     - Save
   
<img width="997" height="616" alt="image" src="https://github.com/user-attachments/assets/3d4a7fef-1452-47cc-87d3-08010007c8bd" />

<img width="1396" height="318" alt="image" src="https://github.com/user-attachments/assets/49ad9e33-c1b0-46bf-8099-d4561f25969c" />

<img width="983" height="286" alt="image" src="https://github.com/user-attachments/assets/abfb5b00-aea7-4319-b442-14310d6f4e99" />

<img width="991" height="353" alt="image" src="https://github.com/user-attachments/assets/f4453f60-9367-441f-bff7-a4040af58025" />




##  criar e testar o bot

Na mesma página, escolha Intenções `Intents` no painel à esquerda. Em seguida, escolha Construir `Build`, quando a criação do bot estiver concluída, selecione Testar

<img width="1410" height="505" alt="image" src="https://github.com/user-attachments/assets/d1bd41ee-492a-4bb4-b3a2-b1c353e8bd93" />

Na janela de teste, insira os seguintes valores:

`I would like to make an appointment`

`A root canal`

`tomorrow` (Se o dia seguinte for fim de semana ou feriado, escolha o próximo dia útil, use o exemplo de datas no calendário dos EUA 09/15/2025)

`10:00 a.m.`

`Yes`

A confirmação a seguir será exibida.

<img width="426" height="657" alt="image" src="https://github.com/user-attachments/assets/0df6e5f7-739b-464e-9cd1-76827f64f787" />

<img width="425" height="655" alt="image" src="https://github.com/user-attachments/assets/57294fc9-b85f-438a-90a8-60384d1b2495" />


## 4️⃣ **Cognito**

- No painel de navegação do Amazon Cognito à esquerda, Identity pools.
  - Configure identity pool trust  → Authentication → Marque Authenticated access e Guest access
  - Marque Authenticated identity sources → Next
<img width="1138" height="651" alt="image" src="https://github.com/user-attachments/assets/57411157-9cc5-4901-b366-e65f49b1adea" />

  - Configure permissions → Authenticated → role Create a new IAM role `Cognito_DentistBot_Auth_Role`
  - Guest role Create a new IAM role `Cognito_DentistBot_Guest_Role`

<img width="1148" height="380" alt="image" src="https://github.com/user-attachments/assets/cb7a912f-00f7-436c-b403-441fb4d78a98" />

<img width="1128" height="386" alt="image" src="https://github.com/user-attachments/assets/fa19af56-3a44-447d-8f07-9d8323d6c3a6" />

- Next → Grupo de usuários do Amazon Cognito
- Pular por enquanto

- Configurar propriedades →  Nome do pool de identidades → `DentistBotIdentityPool` Next

<img width="1162" height="297" alt="image" src="https://github.com/user-attachments/assets/3df1a74b-8cce-4f59-b626-cbc38afab07f" />

Review and create 

<img width="1554" height="233" alt="image" src="https://github.com/user-attachments/assets/75cce36e-87f9-4faa-8f4d-49e6a20d3008" />

- Anote o ID do  pool de identidades.

- Verificar seu DentistBot ID e seu Alias ID , Mudar Cognito_DentistBot_Auth_Role Customer inline e Cognito_DentistBot_Guest_Role
Customer inline no Painel do IAM 

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lex:RecognizeText",
                "lex:RecognizeUtterance"
            ],
            "Resource": "arn:aws:lex:<Seu-AWS-Region :<Seu-Account-ID>:bot-alias/<Seu-DentistBot-ID/Alias-ID"
        }
    ]
}

```
- verificar suas  Cognito_DentistBot_Auth_Role e Cognito_DentistBot_Guest_Role Trust relationships

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "cognito-identity.amazonaws.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "cognito-identity.amazonaws.com:aud": "<Seu-Identity-pool-ID"
                },
                "ForAnyValue:StringLike": {
                    "cognito-identity.amazonaws.com:amr": "authenticated"
                }
            }
        }
    ]
}
```
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "cognito-identity.amazonaws.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "cognito-identity.amazonaws.com:aud": "<Seu-Identity-pool-ID"
                },
                "ForAnyValue:StringLike": {
                    "cognito-identity.amazonaws.com:amr": "unauthenticated"
                }
            }
        }
    ]
}
```

## 5️⃣ criar um **bucket do S3**

- Agora que você configurou as permissões de segurança, crie um bucket do S3 para hospedar sua página Web

  - Acesse os dois arquivos da página web a seguir e extraia-os para um diretório de arquivos local

  - index.html

  - error.html

O arquivo `index.html` inclui o script que carregará seu bot

Acesse **S3**
- Create bucket → Bucket name <Seu-Bucket-Nome> 
- Block all public access desmarque 
    - Marque a caixa de seleção de aviso Confirmar
- Create bucket

<img width="1835" height="520" alt="image" src="https://github.com/user-attachments/assets/9f5ac320-fb75-4551-a47f-9c0032f4784f" />

<img width="1844" height="612" alt="image" src="https://github.com/user-attachments/assets/d19734ae-ca6b-4edd-a649-449f7bc4dda9" />

- Selcione seu Bucket , em Visão geral do bucket selecione carregar `Upload`
- Na página Carregar, selecione Adicionar arquivos. Navegue até o local dos arquivos index.html e error.html

<img width="1846" height="753" alt="image" src="https://github.com/user-attachments/assets/3eb59d38-005b-4f8e-a1c7-0742e3487d5d" />

- Na guia Propriedades, role a tela para baixo até a seção Hospedagem de site estático e selecione Editar
- Selecione Ativar
- Em Documento de índice, insira: index.html . Para a página de erro, insira: error.html. Clique em Salvar alterações

<img width="1481" height="730" alt="image" src="https://github.com/user-attachments/assets/74358acc-186e-4015-98cc-5f39d24db82a" />

- Atualizar e testar o arquivo de demonstração

*Agora você deve atualizar o arquivo HTML de demonstração para que ele use o Amazon Cognito*

*Use o VsCode ou um editor de texto para fazer as alterações a seguir na página index.HTML*

  - Adicione o IdentityPoolId que você criou anteriormente

  - Adicione seu botId (encontrado nas configurações do seu bot)

  - Adicione seu botAliasId (encontrado na seção Versões e aliases)

  - Atualize a região para corresponder à região do seu bot

<img width="875" height="282" alt="image" src="https://github.com/user-attachments/assets/68c44fc0-916e-4e0a-b4db-adec4c526f7d" />

 - Salve a Atualização
 - Faça Upload novamente do arquivo index.html
 - Selecione Permissões Bucket policy Editar

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::<Seu-Bucket-Nome>/*"
        },
        {
            "Sid": "AllowLexV2Runtime",
            "Effect": "Allow",
            "Principal": {
                "Service": "lexv2.amazonaws.com"
            },
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::<Seu-Bucket-Nome>/*"
        }
    ]
}

```

- Save
- Vá para a seção Hospedagem de site estático
- Na parte inferior da seção Hospedagem de site estático, escolha o URL
- A página web é aberta e você pode interagir com o bot da mesma forma que fez no console de gerenciamento da AWS 

<img width="1905" height="956" alt="image" src="https://github.com/user-attachments/assets/c52907b8-0a09-40a9-b597-8536ba98f6ad" />

error page 

<img width="1911" height="956" alt="image" src="https://github.com/user-attachments/assets/ffa40813-7555-4889-a79e-9037e6eb0576" />



## ✅ Conclusão

  - Com este projeto, os alunos aprenderam a:

  - Criar e configurar roles e permissões no IAM.

  - Usar Lambda como code hook para lógica personalizada.

  - Construir e treinar um chatbot com Amazon Lex V2.

  - Gerenciar autenticação com Cognito Identity Pools.

  - Publicar uma aplicação web no Amazon S3 para acesso público.

Esse fluxo mostra na prática como os serviços da AWS podem ser integrados para criar uma solução completa de chatbot inteligente e escalável.


## Licença
Este projeto é **livre para fins educacionais**.  
Não utilize para fins comerciais sem autorização.

---

## Autor
🧑‍🏫 **Heberton Geovane**  
[![LinkedIn](https://img.shields.io/badge/-LinkedIn-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/heberton-geovane/)

   
