# RewardEvents

Esse aplicativo permite controlar o seu OBS ou computador com as recompensas da loja do canal da twitch..

## Caracteristicas

Com o aplicativo é possivel = 

1. Mudar de cena cena no OBS
2. Reproduzir um audio
3. Exibir e/ou ocultar um filtro no obs
4. Enviar uma mensagem no chat como resposta (Igual comandos)
5. Até executar um atalho no seu teclado aplicando assim a funcionalidade que quiser ao programa.



## Porque utlizar isso ?

- Facil configuração,
- Direto ao ponto,
- Melhora a interação dos espectadores com o streamer.

## Requesitos

1. OBS WEBSOCKET (PARA COMUNICAÇÃO COM O OBS EM RELAÇÃO ÁS FONTES PRESONALIZÁVEIS)

## Como utilizar ?

Faça o Download do arquivo RewardEvents.Zip em [Releases] e use EXTRAIR AQUI para criar a pasta SRBR, o programa estará dentro desta pasta.

# Ativação

O programa é pago com um valor de 10 reais( valor simbolico para ajudar também novos streamers e apoiar o meu trabalho ), porém é possivel obter uma chave de licença de testes de 3 dias, para comprar ou testar o programa entre em contato comigo via [Discord]

Para ativar insira a chave de ativação sem espaços e o programa estará ativo.

# Setup ou primeira configuração

### O setup precisa ser executado somente uma vez antes de executar o SRBR.exe.
### !!!NÃO EDITE O ARQUIVO JSON (ERROS PODEM OCORRER)!!!

Siga o passo a passo abaixo para obter todas as informações necessárias para o funcionamento do aplicativo.
(O client ID E client secret são necessários para comunicação com a sua conta e canal da twitch, a partir deles utilizaremos o TOKEN para autenticar a sua conta com o aplicativo)

## Passo 1 Client ID, e Client Secret ( É NECESSARIO ATIVAR A AUTENTICAÇÃO DE 2 FATORES NA TWITCH PARA OBTER O CLIENT ID E CLIENT SECRET )

0. Consiga ID do Canal em (clique) >> [streamweasels.com];
1. Acesse = [Twitch-devs];
2. Logue com a sua conta da twitch;
3. Navegue até 'Your console' no topo da página;
4. Vá até a aba 'Aplicativos';
5. Clique em Registre seu aplicativo;
6. No campo nome use o nome que preferir, isso não irá interferir no funcionamento do programa;
7. Em 'URLs de redirecionamento OAuth' cole a url a seguir = `https://twitchapps.com/tokengen/`
8. Em 'Categoria' use  Application integration
9. Salve e copie o Client-ID ,depois cole no progama no campo especificado
10. Gere um novo Client-Secret e copie ,depois cole no progama no campo especificado


## Passo 2 Token

1. Accesse = [tokengen]
2. Cole o CLIENT ID que pegamos no passo anterior
3. Copie e cole em scopes o conteudo a seguir, não deve conter espaços no final e no inicio somente entre cada scopo = chat:edit chat:read channel:read:redemptions channel:manage:redemptions

## Passo 3 Token BOT

### Opcionalmente podemos configurar uma conta bot para responder os pedidos de musica no chat com o nome da musica e artista e o nome de quem pediu, caso não tenha ou não queira utilizar a conta bot, use o mesmo nome de usuário da sua conta de streamer e o Token obtido no passo 2 (Não é possivel desabilitar esta função)

1. Agora logado na twitch com a conta de bot, Repita todo o processo do passo 1 menos para o ID do CANAL.
2. Repita o processo do passo 2 porem com o CLIENT ID da sua conta bot.
(se quiser alterar a conta bot posteriormente execute todo o processo novamente.)
3. SALVE e seguiremos para o passo 4.


(em caso de erro verifique o passo a passo novamente)
## Passo 4 OBS STUDIO
### Para comunicarmos com o OBS e modificar as informações precisamos instalar a ferramenta [OBS-WEBSOCKET]
1. Instale o [OBS-WEBSOCKET];
2. Abra o OBS studio, vá até a aba ferramentas e clique em WebSockets Server Settings
3. Marque a caixa Enable WebSockets server
4. Em serve port use = 4444
5. Marque a caixa enbale authentication
6. Em password use = 1234
7. Clique em OK

## Passo 5 Recompensas

As abas superiores no aplicativo controlam cada tipo de função conforme o titulo da recompensa, é expressamente necessário que o titulo da recompensa seja o mesmo da sua loja da twitch.
1. Preencha os campos com as informações necessárias.
2. a localização do arquivo de audio que quiser utilizar na aba audio deve estar localizada em src/files/,
3. Para configurar uma notificação no seu OBS quando uma recompensa de audio for resgatada, crie um grupo de notificação com o nome REQUESTGROUP,adicione uma imagem e use a imagem que está localizada em src/Request.png, crie uma fonte de texto com o nome REQUEST_USER_NAME e uma com o nome REQUEST_NAME, adicione o fundo de sua preferência no mesmo grupo.
4. As outras abas são configuradas adicionando o nome correto de cada item.
5. Somente as recompensas de audio tem notificalções.



<div align="left">
    <a href="GGTEC#8307" target="_blank">
    <img src="https://raw.githubusercontent.com/maurodesouza/profile-readme-generator/master/src/assets/icons/social/discord/default.svg" width="52" height="40" alt="discord logo"  />
    </a>
    <p>Donate</p>
    <a href="https://livepix.gg/ggtec" target="_blank">
    <img src="https://dashboard.livepix.gg/images/logo-white.svg" width="52" height="40" />
    </a>
    <p> paypal = jheferson1gambet@gmail.com</p>
</div>

###

[OBS-WEBSOCKET]: <https://obsproject.com/forum/resources/obs-websocket-remote-control-obs-studio-using-websockets.466/>
[Discord]: <https://youup.me/ggtec>
[Twitch-devs]: <https://dev.twitch.tv>
[streamweasels.com]: <https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/>
[tokengen]: <https://twitchapps.com/tokengen/>
