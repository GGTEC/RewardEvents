# RewardEvents

Esse aplicativo permite usar as recompensas da twitch para executar eventos personalizados.

- Galeria de prints do programa
<a href="https://www.canva.com/design/DAFKks4wM3U/EP88RFgZN_BnwPm1zjFDdA/view#8">Galeria</a>

## Funções

Com o aplicativo é possivel = 

1. Reproduzir um audio;
2. Resgate com texto falado (voz do google);
3. Mudar de cena cena no OBS;
4. Exibir e/ou ocultar um filtro no obs;
5. Executar um atalho no seu teclado;
6. Exibir e/ou ocultar um filtro no obs;
7. Resposta no chat com recompensa;
8. Criar clipes com recompensa ou manualmente por meio de um botão na tela principal;
9. Criar comandos para cada evento opcionalmente;
10. Criar comandos simples para respostas no chat (Qualquer prefix é aceito ou nenhum se preferir);
11. Configurar mensagens automaticas para serem enviadas no chat em um intervalo personalizavél.


## Porque utlizar isso ?

- Facil configuração;
- Direto ao ponto;
- Melhora a interação dos espectadores com o streamer;
- 1001 utilidades 5 configurações
- Configurado uma vez não é necessário configurar novamente. (Entre em contato via [Discord] caso precise de ajuda)

## Requesitos

1. OBS WEBSOCKET COMPAT (PARA COMUNICAÇÃO COM O OBS EM RELAÇÃO ÁS FONTES PRESONALIZÁVEIS) [OBS-WEBSOCKET]

## Como utilizar ?

- Faça o Download do arquivo RewardEvents.Zip em [Releases] e use EXTRAIR AQUI para criar a pasta RewardEvents, o programa estará dentro desta pasta.

# Setup ou primeira configuração

- O setup precisa ser executado somente uma vez.
- !!!NÃO EDITE O ARQUIVO JSON (ERROS PODEM OCORRER)!!!

Siga o passo a passo abaixo para obter todas as informações necessárias para o funcionamento do aplicativo.

## Passo 1 Conta streamer (Princial)
- Depois de clicar em login o aplicativo deve ficar com a tela principal congelada e somente a tela de navegador funcionando.

1. Digite o nome da sua conta de streamer que você usa na url no campo requisitado.
2. Clique em login
3. Logue na sua conta e autorize o aplicativo para comunicar com a sua conta e coletar as informações necessárias para o funcionamento do aplicativo, as permissões coletadas são exibidas no momento em que é requisitada a autorização.

## Passo 2 Conta bot (opcional)
- Caso não queira usar a uma BOT marque a opção na janela.

1. Digite o nome de login da sua conta bot que você usa na url no campo requisitado.
2. Clique em login
3. Logue na sua conta e autorize o aplicativo para comunicar com a sua conta e coletar as informações necessárias para o funcionamento do aplicativo, as permissões coletadas são exibidas no momento em que é requisitada a autorização.


## Passo 4 OBS STUDIO 
_É obrigatório estar conectado com o OBS studio para configurar qualquer tipo de evento ou configuração com relação ao OBS studio_
- Para comunicarmos com o OBS e modificar as informações para isso precisamos instalar a ferramenta [OBS-WEBSOCKET]

1. Instale o [OBS-WEBSOCKET];
2. Abra o OBS studio, vá até a aba ferramentas e clique em WebSockets Server Settings
3. Marque a caixa Enable WebSockets server;
4. Em serve port teste alguma que funcionar ex. 444;
5. Marque a caixa enbale authentication;
6. Em password use a senha que preferir ex. 1234;
7. Utilize os mesmos valores no campo port e password no programa;
7. Clique em OK e a configuração inicial estará salva;


## Configurando os eventos de acordo com as recompensas

Na aba superior em Eventos é possível configurar cada evento para uma recompensa.
É possivel configurar apenas um evento por recompensa.
É necessário criar a recompensa no seu canal da twitch antes de criar um evento.
_Selecione no menu de opções qual evento deverá ser criado_


## Reproduzir Audio

- _Recompensa_ = Selecione a recompensa do canal na twitch;
- _Comando para o chat_ = Esse campo é opcional, use se quiser que seja possivel executar o evento com um comando;
- _Somente moderador pode usar o comando ?_ = Marcando essa opção faz com que somente moderador ou o próprio streamer utilize o comando;
- _Arquivo de audio_ = Selecione o arquivo de audio para ser reproduzido quando a recompensa for resgatada;
- _Tempo da notificação no OBS_ = Quanto tempo a notificação ficará visivel na tela;
- _Resposta no chat_ = Envia a mensagem no chat do canal quando a recompensa for resgatada;


## Texto falado Google

- _Titulo da recompensa_ = Selecione a recompensa do canal na twitch;
- _Comando para o chat_ = Esse campo é opcional, use se quiser que seja possivel executar o evento com um comando;
- _Somente moderador pode usar o comando ?_ = Marcando essa opção faz com que somente moderador ou o próprio streamer utilize o comando;
- _Limite de letras_ = Limite de letras para evitar flood;
- _Tempo da notificação no obs_ = Quanto tempo a notificação ficará visivel na tela;
- _Resposta no chat_ = Envia a mensagem no chat do canal quando a recompensa for resgatada;


## Mudar cena OBS

- _Recompensa_ = Selecione a recompensa do canal na twitch;
- _Comando para o chat_ = Esse campo é opcional, use se quiser que seja possivel executar o evento com um comando;
- _Somente moderador pode usar o comando ?_ = Marcando essa opção faz com que somente moderador ou o próprio streamer utilize o comando;
- _Cena Atual_ = Deve ser a cena que está ativa no OBS studio
- _Mudar para a cena_ = Deve ser a cena que será ativa no momento do resgate
- _Retornar para a cena anterior_ = Defina se o programa deve retornar para a _Cena Atual_ selecionada;
- _Tempo para voltar para a cena anterior_ = O tempo deve ser em segundos ex.:15;
- _Resposta no chat_ = Envia a mensagem no chat do canal quando a recompensa for resgatada;


## Exibit/ocultar Filtro OBS

- _Recompensa_ = Selecione a recompensa do canal na twitch;
- _Comando para o chat_ = Esse campo é opcional, use se quiser que seja possivel executar o evento com um comando;
- _Somente moderador pode usar o comando ?_ = Marcando essa opção faz com que somente moderador ou o próprio streamer utilize o comando;
- _Nome da fonte do OBS_ = Seleciona a fonte que deve ter o filtro alterado;
- _Nome do filtro presente na fonte_ = Selecione o nome do filtro que está configurado na fonte do OBS;
- _Tempo com o filtro ativo_ = Quanto tempo o filtro deverá ficar ativo no OBS;
- _Resposta no chat_ = Envia a mensagem no chat do canal quando a recompensa for resgatada;


## Exibir/ocultar fonte OBS

- _Recompensa_ = Selecione a recompensa do canal na twitch;
- _Comando para o chat_ = Esse campo é opcional, use se quiser que seja possivel executar o evento com um comando;
- _Somente moderador pode usar o comando ?_ = Marcando essa opção faz com que somente moderador ou o próprio streamer utilize o comando;
- _Nome da fonte no OBS_ = Selecione a fonte que deverá ser Exbida/Oculta;
- _Tempo exibindo_ = É o tempo que a fonte ficará visível na tela;
- _Resposta no chat_ = Envia a mensagem no chat do canal quando a recompensa for resgatada;


## Atalho no teclado

- _Recompensa_ = Selecione a recompensa do canal na twitch;
- _Comando para o chat_ = Esse campo é opcional, use se quiser que seja possivel executar o evento com um comando;
- _Somente moderador pode usar o comando ?_ = Marcando essa opção faz com que somente moderador ou o próprio streamer utilize o comando;
- _Pressionar a tecla novamente depois do tempo_ = Selecione se deseja que a tecla seja pressionada novamente, util com atalhos para ativar/desativar funções em programas;
- _Tempo para pressionar novamente_ = O tempo deve ser em segundos ex.:15;
- _Selecione as teclas_ = Selecione as teclas para serem pressionadas na ordem correta;
- _Resposta no chat_ = Envia a mensagem no chat do canal quando a recompensa for resgatada;


## Resposta no chat

- _Recompensa_ = Selecione a recompensa do canal na twitch;
- _Comando para o chat_ = Esse campo é opcional, use se quiser que seja possivel executar o evento com um comando;
- _Somente moderador pode usar o comando ?_ = Marcando essa opção faz com que somente moderador ou o próprio streamer utilize o comando;
- _Mensagem no Chat_ = Qual mensagem deverá ser enviada no resgate;


## Criar um Clip

- _Recompensa_ = Selecione a recompensa do canal na twitch;
- _Comando para o chat_ = Esse campo é opcional, use se quiser que seja possivel executar o evento com um comando;
- _Somente moderador pode usar o comando ?_ = Marcando essa opção faz com que somente moderador ou o próprio streamer utilize o comando;


## Excluir um evento
- Exclui um evento criado

## Na aba superior COMANDOS é possível gerenciar os comandos simples

### Criar um comando simples

- _Comando_ = Cria um comando simples (UTILIZE O PREFIXO QUE PREFERIR EX = !,?,@,#," OU ATÉ MESMO SEM PREFIXO E SOMENTE A PALAVRA);
- _Mensagem no chat_ = Qual mensagem no chat o comando irá enviar;
- _Somente moderador_ = Marcando essa opção faz que somente moderador ou o streamer possam utilizar o comando;

### Editar um comando simples

- _Comando_ = Qual comando deve ter o conteúdo editdado
- _Conteúdo da resposta_ = Insira a nova resposta
- _Somente moderador pode usar o comando ?_ = Marcando essa opção faz que somente moderador ou o streamer possam utilizar o comando;

### Editar delay para comandos

- _Editar delay para comandos gerais_ = Insira um valor em segundos para o delay entre os comandos.
- _Editar delay para !tts_ = Insira um valor em segundos para o delay de comandos !tts.

### Excluir um comando

- _Selecione o comando_ = Selecione qual comando deseja excluir.

## Timers
Na aba superior TIMERS é possível gerenciar as mensagens automáticas no chat

### Criar um timer
- _Mensagem_ = Insira qual mensagem deverá ser enviada.

### Editar timer
- _Selecione uma mensagem_ = Selecione uma mensagem para editar
- Insira a nova mensagem

### Excluir um timer
- _Excluir uma mensagem_ = Selecione a mensagem para excluir

### Alterar intervalo entre as mensagens
- ___Aplica um intervalo diferente para cada mensagem enviada escolhendo um valor aleátorio entre os tempos maximo e minimo
- _Minimo_ = ex.:100
- _Máximo_ = ex.:500
- Resultado = Primeira mensagem: 200, segunda mensagem:300, terceira mensagem: 50. etc....


## Configurações
## Na aba configurações é possivel configurar =

- conexão com o OBS studio;
- Notificações enviadas ao obs studio por meio de fontes de texto quando uma recompensa for resgatada;
- Quais tipos de mensagens o bot poderá enviar no chat e habilitar ou desabilitar comandos;

### Configurar conexão com o OBS studio

- _OBS HOST_ = Insira o mesmo valor que se encontra na configuração do OBS studio Websocket;
- _OBS PORT _ = Insira o mesmo valor que se encontra na configuração do OBS studio Websocket;
- _OBS PASSWORD_ = Insira o mesmo valor que se encontra na configuração do OBS studio Websocket;
- _Conectar automaticamente ao iniciar_ = Marcando essa caixa faz que o RewardEvents se conecte automaticamente ao OBS studio quando iniciar, sem essa opção marcada será necessário conectar manualmente;

### Configurar notificações no OBS studio

- _Nome do grupo_ = Selecione o nome do grupo no OBS studio que contem as fontes de texto, isso servirá para exbir e esconder os textos ao receber uma notificação;
- _Titulo da recompensa_ = Selecione o nome da fonte de texto do OBS que irá receber o nome da recompensa;
- _Usuário que resgatou_ = Selecione o nome da fotne de texto do OBS que irá receber o nome do usuário que resgatou a recompensa;

### Status de comandos e mensagens/respostas
- _Habilitar comando !tts ?_ = Marcando essa opção habilita o comando !tts;
- _Habilitar comandos ?_ = Marcando essa opção habilita todos os comandos menos o !tts;
- _Ativar respostas de comandos?_ =  Marcando essa opção habilita as respostas no chat de todos os comandos;
- _Exibir delay para comandos ?_ = Marcando essa opção habilita a resposta de delay caso um usuário tente enviar o comando antes do tempo;
- _Exibir confirmações/erros de clipes ?_ = Marcando essa opção habilita as respostas de clipes utilizando comandos, resgates de recompensa e/ou botão na interface;
- _Exbir erro de permissão para comandos ?_ = Marcando essa opção habilita a mensagem de erro quando um usuário tentar utilizar um comando que não tem permissão;
- _Ativar timer ?_ = Ativa as mensagens automaticas no chat;
- _Status de conexão no chat :_ = Envia uma mensagem quando o sistema de comandos for conectado ao chat;


<div align="left">
    <h2>Entre em contato via discord</h2>
    <a href="GGTEC#8307" target="_blank">
    <img src="https://raw.githubusercontent.com/maurodesouza/profile-readme-generator/master/src/assets/icons/social/discord/default.svg" width="52" height="40" alt="discord logo"/>
    </a>
    <h2>Donate</h2>
    <a href="https://livepix.gg/ggtec" target="_blank">
    <img src="https://dashboard.livepix.gg/images/logo-white.svg" width="52" height="40" />
    </a>
    <p> paypal = jheferson1gambet@gmail.com</p>
</div>

###

[OBS-WEBSOCKET]: <https://github.com/obsproject/obs-websocket/releases>
[Discord]: <https://youup.me/ggtec>
