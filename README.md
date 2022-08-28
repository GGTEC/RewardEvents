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
10. Configurar mensagens automaticas para serem enviadas no chat em um intervalo personalizavél.


## Porque utlizar isso ?

- Facil configuração;
- Direto ao ponto;
- Melhora a interação dos espectadores com o streamer;
- 1001 utilidades 5 configurações
- Configurado uma vez não é necessário configurar novamente. (Entre em contato via [Discord] caso precise de ajuda)

## Requesitos

1. OBS WEBSOCKET (PARA COMUNICAÇÃO COM O OBS EM RELAÇÃO ÁS FONTES PRESONALIZÁVEIS)

## Como utilizar ?

- Faça o Download do arquivo RewardEvents.Zip em [Releases] e use EXTRAIR AQUI para criar a pasta RewardEvents, o programa estará dentro desta pasta.

# Ativação

- Para conseguir a sua Key entre em contato comigo via [Discord]
- Para ativar insira a chave de ativação sem espaços e o programa estará ativo.

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
- Para comunicarmos com o OBS e modificar as informações precisamos instalar a ferramenta [OBS-WEBSOCKET]

1. Instale o [OBS-WEBSOCKET];
2. Abra o OBS studio, vá até a aba ferramentas e clique em WebSockets Server Settings
3. Marque a caixa Enable WebSockets server
4. Em serve port use = 4444
5. Marque a caixa enbale authentication
6. Em password use = 1234
7. Clique em OK e a configuração inicial estará salva


## Configurando os eventos de acordo com as recompensas

Na aba superior em Eventos é possível configurar cada evento para uma recompensa.
É possivel configurar apenas um evento por recompensa.
É necessário criar a recompensa no seu canal da twitch antes de criar um evento.


## Reproduzir Audio
- _Titulo da recompensa_ = O titulo deve ser o idêntico ao da recompensa do canal da twitch
- _Comando para o chat_ = Esse campo é opcional, use se quiser que seja possivel executar o evento com um comando, não é necesssário utilizar o '!' antes do nome do comando
- _Arquivo de audio_ = Selecione por meio do botão qual será o arquivo de audio para ser reproduzido quando a recompensa for resgatada.
- _Tempo da notificação no OBS_ = Quanto tempo a notificação ficará visivel na tela.

## Texto falado Google

- _Titulo da recompensa_ = O titulo deve ser o idêntico ao da recompensa do canal da twitch
- _Comando para o chat_ = Esse campo é opcional, use se quiser que seja possivel executar o evento com um comando, não é necesssário utilizar o '!' antes do nome do - comando

## Mudar cena OBS
## Exibit/ocultar Filtro OBS
- _Titulo da recompensa_ = O titulo deve ser o idêntico ao da recompensa do canal da twitch
- _Comando para o chat_ = Esse campo é opcional, use se quiser que seja possivel executar o evento com um comando, não é necesssário utilizar o '!' antes do nome do comando
- _Cena Atual_ = Deve ser a cena que está ativa no OBS studio
- _Mudar para a cena_ = Deve ser a cena que será ativa no momento do resgate
- _Tempo para voltar para a cena anterior_ = O tempo deve ser em segundos ex.:15


## Atalho no teclado
- _Titulo da recompensa_ = O titulo deve ser o idêntico ao da recompensa do canal da twitch
- _Comando para o chat_ = Esse campo é opcional, use se quiser que seja possivel executar o evento com um comando, não é necesssário utilizar o '!' antes do nome do comando
- _Tempo para pressionar novamente_ = O tempo deve ser em segundos ex.:15
- _Selecione as teclas_ = Selecione as teclas para serem pressionadas na ordem correta


## Exibir/ocultar fonte OBS
- _Titulo da recompensa_ = O titulo deve ser o idêntico ao da recompensa do canal da twitch
- _Comando para o chat_ = Esse campo é opcional, use se quiser que seja possivel executar o evento com um comando, não é necesssário utilizar o '!' antes do nome do comando
- _Nome da fonte no OBS_ = É o nome da fonte/source que será exibido/ocultado
- _Tempo exibindo_ = É o tempo que a fonte ficará visível na tela


## Resposta no chat
- _Titulo da recompensa_ = O titulo deve ser o idêntico ao da recompensa do canal da twitch
- _Comando para o chat_ = Esse campo é opcional, use se quiser que seja possivel executar o evento com um comando, não é necesssário utilizar o '!' antes do nome do comando
- _Mensagem no Chat_ = Qual mensagem deverá ser exibida no resgate


## Criar um Clip
- _Titulo da recompensa_ = O titulo deve ser o idêntico ao da recompensa do canal da twitch
- _Comando para o chat_ = Esse campo é opcional, use se quiser que seja possivel executar o evento com um comando, não é necesssário utilizar o '!' antes do nome do comando


## Excluir um evento
- Exclui um evento criado


## Gerenciar timer
- Adicionar uma mensagem
_Mensagem_ = Qual mensagem deverá ser enviada (comandos com '/' da twitch estão habilitados ex.= /me,/announce)

### Intervalo entre mensagens
- ___Cria um intervalo diferente para cada mensagem enviada escolhendo um valor aleátorio entre os tempos maximo e minimo
- _Minimo_ = ex.:100
- _Máximo_ = ex.:500
- Resultado = Primeira mensagem: 200, segunda mensagem:300, terceira mensagem: 50.

### Excluir uma mensagem
- Selecione uma mensagem para excluir.




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

[OBS-WEBSOCKET]: <https://obsproject.com/forum/resources/obs-websocket-remote-control-obs-studio-using-websockets.466/>
[Discord]: <https://youup.me/ggtec>
