//COMANDOS

function show_commands_div(div_id) {

    if (div_id == "del-commands-div") {
        commands_fun('event','get_list');
    } else if (div_id == "edit-commands-div") {
        commands_fun('event','get_list');
    } else if (div_id == "duel-commands-div"){
        commands_fun('event','get_duel');
    }
    document.getElementById("commands-div").hidden = true;
    document.getElementById(div_id).hidden = false;
}

function hide_commands_div(div_id, modal) {

    $("#" + modal).modal("hide");
    document.getElementById("commands-div").hidden = false;
    document.getElementById(div_id).hidden = true;

}

async function commands_fun(event,type_id){

    if (type_id == 'create'){
        event.preventDefault();

        var form = document.querySelector("#command-create-form");
        var mod_value = form.querySelector('select[id="user-level-command"]').value;
    
        data = {
            new_command: form.querySelector('input[id="new-command"]').value,
            new_message: form.querySelector('input[id="new-message"]').value,
            new_delay: form.querySelector('input[id="new-delay"]').value,
            new_user_level: mod_value,
        };
    
        var formData = JSON.stringify(data);

        window.pywebview.api.commands_py('create',formData);

        form.reset();

    
    } else if (type_id == 'edit'){
        event.preventDefault();

        var form = document.querySelector("#command-edit-form");
        var mod_value = form.querySelector('select[id="user-level-command-edit"]').value;
        var status_command = form.querySelector('#command-simple-status');

        if (status_command.checked == true) {
            status_command = 1
        } else if (status_command.checked == false) {
            status_command = 0
        }


        data = {
            old_command: form.querySelector('select[id="command-select-edit"]').value,
            edit_command: form.querySelector('input[id="edit-command"]').value,
            status_command: status_command,
            edit_message: form.querySelector('input[id="edit-message"]').value,
            edit_delay:form.querySelector('input[id="edit-delay"]').value,
            edit_user_level: mod_value,
        };

        var formData = JSON.stringify(data);

        window.pywebview.api.commands_py(type_id,formData);
        form.reset();


    } else if (type_id == 'delete'){

        event.preventDefault();

        var form = document.querySelector("#command-del-form");
        var command = form.querySelector('select[id="command-select-del"]').value;

        window.pywebview.api.commands_py(type_id,command);
        form.reset();
        $("#command-select-del option:selected").remove();
        $("#command-select-del").selectpicker("refresh");

    } else if (type_id == 'get_list'){

        var list_command_parse = await window.pywebview.api.commands_py(type_id,'null');

        if (list_command_parse) {
            list_command_parse = JSON.parse(list_command_parse)

            $("#command-select-del").empty();
            $("#command-select-del").selectpicker("refresh");
            $("#command-select-edit").empty();
            $("#command-select-edit").selectpicker("refresh");
    
    
            for (var i = 0; i < list_command_parse.length; i++) {
                var optn = list_command_parse[i];
    
                $("#command-select-del").append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
                $("#command-select-del").selectpicker("refresh");
                $("#command-select-edit").append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
                $("#command-select-edit").selectpicker("refresh");
            }
        }

    } else if (type_id == 'get_info'){

        var command = document.querySelector("#command-select-edit").value;
        var command_info_parse = await window.pywebview.api.commands_py(type_id,command);

        if (command_info_parse) {
            
            command_info_parse = JSON.parse(command_info_parse)
            var status_command = command_info_parse.status;
            var command_edit = command_info_parse.edit_command;
            var message_edit = command_info_parse.edit_message;
            var delay_edit = command_info_parse.edit_delay;

            if (status_command == 1){
                document.getElementById("command-simple-status").checked = true;
            } else if (status_command == 0){
                document.getElementById("command-simple-status").checked = false;
            }

            document.getElementById("edit-command").value = command_edit;
            document.getElementById("edit-message").value = message_edit;
            document.getElementById("edit-delay").value = delay_edit;

        }
    } else if (type_id == 'get_duel'){

        var form_duel = document.getElementById('duel-form');
        var command_duel = form_duel.querySelector('#command-duel');
        var command_accept = form_duel.querySelector('#command-duel-accept');
        var user_level_duel = form_duel.querySelector('#user-level-duel');
        var delay_duel = form_duel.querySelector('#command-duel-delay');
        var time_to_accept = form_duel.querySelector('#time-duel-accept');
        var time_to_message = form_duel.querySelector('#time-duel-message');
        var time_to_start = form_duel.querySelector('#time-duel-start');
        var create_pred = form_duel.querySelector('#pred-enable');
        var select_batle = form_duel.querySelector('#select-message-duel');

        var duel_info_parse = await window.pywebview.api.commands_py(type_id,'null');

        if (duel_info_parse){
            duel_info_parse = JSON.parse(duel_info_parse)

            command_duel.value = duel_info_parse.command_duel;
            command_accept.value = duel_info_parse.command_accept;
            user_level_duel.value = duel_info_parse.user_level;
            delay_duel.value = duel_info_parse.delay;
            time_to_accept.value = duel_info_parse.time_to_accept;
            time_to_message.value = duel_info_parse.time_to_message;
            time_to_start.value = duel_info_parse.time_to_start;
            
            if (duel_info_parse.create_pred == 1){
                create_pred.checked = true;
            } else {
                create_pred.checked = false;
            }

            var count_ba = 0
            for (item in duel_info_parse.duel_battle_list){
                
                count_ba = count_ba + 1

                $("#select-message-duel").append('<option style="background: #000; color: #fff;" value="'+ item +'">Duelo'+count_ba +'</option>');
                $("#select-message-duel").selectpicker("refresh");
            }

        }

    } else if (type_id == 'get_battles'){

        var select_battle = document.getElementById('select-message-duel');
        var div_duel_message = document.getElementById('message-duel-edit');
        div_duel_message.hidden = true;

        var message_0 = document.getElementById('duel-message-0');
        var message_1 = document.getElementById('duel-message-1');
        var message_2 = document.getElementById('duel-message-2');
        var message_3 = document.getElementById('duel-message-3');
        var message_4 = document.getElementById('duel-message-4');
        var message_5 = document.getElementById('duel-message-5');


        if (select_battle.value == 'None'){
            toast_notifc('Selecione uma mensagem')
        } else {
            var duel_battle_parse = await window.pywebview.api.commands_py(type_id,select_battle.value);

            if (duel_battle_parse){
                duel_battle_parse = JSON.parse(duel_battle_parse)
                message_0.value = duel_battle_parse.message_0;
                message_1.value = duel_battle_parse.message_1;
                message_2.value = duel_battle_parse.message_2;
                message_3.value = duel_battle_parse.message_3;
                message_4.value = duel_battle_parse.message_4;
                message_5.value = duel_battle_parse.message_5;
    
                div_duel_message.hidden = false;
    
    
            }
        }
        
    } else if (type_id == 'save_duel'){
        event.preventDefault();

        var form_duel = document.getElementById('duel-form');
        var command_duel = form_duel.querySelector('#command-duel');
        var command_accept = form_duel.querySelector('#command-duel-accept');
        var delay_duel = form_duel.querySelector('#command-duel-delay');
        var user_level_duel = form_duel.querySelector('#user-level-duel');
        var time_to_accept = form_duel.querySelector('#time-duel-accept');
        var time_to_message = form_duel.querySelector('#time-duel-message');
        var time_to_start = form_duel.querySelector('#time-duel-start');
        var create_pred = form_duel.querySelector('#pred-enable');
        var select_batle = form_duel.querySelector('#select-message-duel');

        var div_duel_message = document.getElementById('message-duel-edit');
        div_duel_message.hidden = true;

        var message_0 = document.getElementById('duel-message-0');
        var message_1 = document.getElementById('duel-message-1');
        var message_2 = document.getElementById('duel-message-2');
        var message_3 = document.getElementById('duel-message-3');
        var message_4 = document.getElementById('duel-message-4');
        var message_5 = document.getElementById('duel-message-5');

        if(create_pred.checked == true) {
            create_pred = 1
        } else {
            create_pred = 0
        }

        data = {
            command_duel : command_duel.value,
            command_accept : command_accept.value,
            user_level_duel : user_level_duel.value,
            delay : delay_duel.value,
            time_to_accept : time_to_accept.value,
            time_to_message : time_to_message.value,
            time_to_start : time_to_start.value,
            create_pred : create_pred,
            new_user_level: mod_value,
            select_batle : select_batle.value,
            message_0 : message_0.value,
            message_1 : message_1.value,
            message_2 : message_2.value,
            message_3 : message_3.value,
            message_4 : message_4.value,
            message_5 : message_5.value,
        };
    
        var formData = JSON.stringify(data);
        window.pywebview.api.commands_py(type_id,formData);

    
    } else if (type_id == 'get_default'){

        var cmd_val = document.getElementById('command-default-command');
        var cmd_status = document.getElementById('command-default-status');
        var cmd_delay = document.getElementById('command-default-delay');
        var cmd_respo = document.getElementById('command-default-respo');
        var cmd_perm = document.getElementById('command-default-perm');
        var cmd_type = document.getElementById('command-default-type');

        var cmd_aliases = document.getElementById('command-default-aliases');

        var fomr_command_default = document.getElementById('form-command-default');

        var select_editor = document.querySelector('#command-default-edit');

        cmd_type.value = select_editor.value

        var resp_default_parse = await window.pywebview.api.commands_py(type_id,select_editor.value);

        if (resp_default_parse) {
            resp_default_parse = JSON.parse(resp_default_parse)
            fomr_command_default.hidden = false;

            if (cmd_type.value == 'cmd'){
                cmd_respo.setAttribute('readonly', 'true')
            } else {
                cmd_respo.removeAttribute('readonly')
            }

            if (cmd_type.value == 'emote'){
                cmd_delay.setAttribute('min', '10')
            } else {
                cmd_respo.setAttribute('min','0')
            }

            if (resp_default_parse.status == 1){
                cmd_status.checked = true;
            } else if (resp_default_parse.status = 0){
                cmd_status.checked = false;
            }

            cmd_val.value = resp_default_parse.command;
            cmd_delay.value = resp_default_parse.delay;
            cmd_respo.value = resp_default_parse.response;


            if (cmd_type.value == "cmd"){
                cmd_aliases.value = ""
            } else if (cmd_type.value == "dice"){
                cmd_aliases.value = "{username}[value]";
            } else if (cmd_type.value == "random"){
                cmd_aliases.value = "{username}[value]";
            } else if (cmd_type.value == "uptime"){
                cmd_aliases.value = "{username}{h}{m}";
            } else if (cmd_type.value == "game"){
                cmd_aliases.value = "{username}{game}";
            } else if (cmd_type.value == "followage"){
                cmd_aliases.value = "{username}{streamer}{d}{h}{m}";
            } else if (cmd_type.value == "msgcount"){
                cmd_aliases.value = "{username}{count}";
            } else if (cmd_type.value == "watchtime"){
                cmd_aliases.value = "{username}{streamer}{d}{h}{m}";
            } else if (cmd_type.value == "accountage"){
                cmd_aliases.value = "{username}{year}{month}{day}{hour}{minute}";
            } else if (cmd_type.value == "interaction_1"){
                cmd_aliases.value = "{user_1}{user_2}";
            } else if (cmd_type.value == "interaction_2"){
                cmd_aliases.value = "{user_1}{user_2}";
            } else if (cmd_type.value == "interaction_3"){
                cmd_aliases.value = "{user_1}{user_2}";
            } else if (cmd_type.value == "interaction_4"){
                cmd_aliases.value = "{user_1}{user_2}";
            } else if (cmd_type.value == "interaction_5"){
                cmd_aliases.value = "{user_1}{user_2}";
            } else if (cmd_type.value == "setgame"){
                cmd_aliases.value = "{username}{game_name}";
            } else if (cmd_type.value == "title"){
                cmd_aliases.value = "{username}{sufix}";
            } else if (cmd_type.value == "emote"){
                cmd_aliases.value = "";
            }

            $("#command-default-perm").selectpicker('val', resp_default_parse.user_level)

        }


    } else if (type_id == 'save_default'){

        var cmd_val = document.getElementById('command-default-command');
        var cmd_status = document.getElementById('command-default-status');
        var cmd_delay = document.getElementById('command-default-delay');
        var cmd_respo = document.getElementById('command-default-respo');
        var cmd_perm = document.getElementById('command-default-perm');
        var cmd_type = document.getElementById('command-default-type');

        cmd_status = cmd_status.checked ? 1 : 0

        data = {
            default_type : cmd_type.value,
            command : cmd_val.value,
            status: cmd_status,
            delay: cmd_delay.value,
            response : cmd_respo.value,
            perm : cmd_perm.value,
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.commands_py(type_id,formData);

    } else if (type_id == 'command-list'){

        $("#list-comands-modal").modal("show");

        var command_list_parse = await window.pywebview.api.get_command_list()

        if (command_list_parse){


            var command_list_redeem = command_list_parse.commands_redeem[0]
            var command_list_simple = command_list_parse.commands_simple[0]
            var command_list_default = command_list_parse.commands_default[0]
            var command_list_counter = command_list_parse.commands_counter[0]
            var command_list_giveaway = command_list_parse.commands_giveaway[0]
            var command_list_player = command_list_parse.commands_player[0]

            var dataTableData = [];

            for (var key in command_list_redeem) {
                if (command_list_redeem.hasOwnProperty(key)) {
                  var rewardItem = command_list_redeem[key];
                  dataTableData.push([
                    key,
                    "Recompensa",
                    rewardItem.last_use == 0 ? "Nunca" : new Date(rewardItem.last_use * 1000).toLocaleString(),
                    rewardItem.status == 1 ? "Sim" : "Não",
                    rewardItem.delay,
                    rewardItem.redeem,
                    '',
                    rewardItem.user_level
                  ]);
                }
            }

            for (var key in command_list_simple) {
                if (command_list_simple.hasOwnProperty(key)) {
                  var commandItem = command_list_simple[key];
                  dataTableData.push([
                    key,
                    "Simples",
                    commandItem.last_use == 0 ? "Nunca" : new Date(commandItem.last_use * 1000).toLocaleString(),
                    commandItem.status == 1 ? "Sim" : "Não",
                    commandItem.delay,
                    '',
                    commandItem.response,
                    commandItem.user_level
                  ]);
                }
              }

            for (var key in command_list_default) {
                if (command_list_default.hasOwnProperty(key)) {
                    var defaultItem = command_list_default[key];
                    dataTableData.push([
                    defaultItem.command,
                    `Padrão / ${key}`,
                    defaultItem.last_use == 0 ? "Nunca" : new Date(defaultItem.last_use * 1000).toLocaleString(),
                    defaultItem.status == 1 ? "Sim" : "Não",
                    defaultItem.delay,
                    '',
                    defaultItem.response,
                    defaultItem.user_level
                    ]);
                }
            }

            for (var key in command_list_counter) {
                if (command_list_counter.hasOwnProperty(key)) {
                    var counterItem = command_list_counter[key];
                    dataTableData.push([
                    counterItem.command,
                    `Counter / ${key}`,
                    counterItem.last_use == 0 ? "Nunca" : new Date(counterItem.last_use * 1000).toLocaleString(),
                    counterItem.status == 1 ? "Sim" : "Não",
                    counterItem.delay,
                    '',
                    '',
                    'Mod'
                    ]);
                }
            }

            for (var key in command_list_giveaway) {
                if (command_list_giveaway.hasOwnProperty(key)) {
                    var giveawayItem = command_list_giveaway[key];
                    dataTableData.push([
                    giveawayItem.command,
                    `Sorteio / ${key}`,
                    giveawayItem.last_use == 0 ? "Nunca" : new Date(giveawayItem.last_use * 1000).toLocaleString(),
                    giveawayItem.status == 1 ? "Sim" : "Não",
                    giveawayItem.delay,
                    '',
                    '',
                    'Mod'
                    ]);
                }
            }

            for (var key in command_list_player) {
                if (key != "redeem"){
                    if (command_list_player.hasOwnProperty(key)) {
                        var playerItem = command_list_player[key];
                        dataTableData.push([
                        playerItem.command,
                        `Player / ${key}`,
                        playerItem.last_use == 0 ? "Nunca" : new Date(playerItem.last_use * 1000).toLocaleString(),
                        playerItem.status == 1 ? "Sim" : "Não",
                        playerItem.delay,
                        '',
                        '',
                        defaultItem.user_level
                        ]);
                    }
                }

            }

            if ($.fn.DataTable.isDataTable("#commandlist_table")) {
                $('#commandlist_table').DataTable().clear().draw();
                $('#commandlist_table').DataTable().destroy();
            }

            var table = $('#commandlist_table').DataTable( {
                destroy: true,
                initComplete: function () {
                    this.api()
                        .columns()
                        .every(function () {
                            var that = this;
         
                            $('input', this.footer()).on('keyup change clear', function () {
                                if (that.search() !== this.value) {
                                    that.search(this.value).draw();
                                }
                            });
                        });
                },
                scrollX: true,
                paging: true,
                ordering:  true,
                retrieve : false,
                processing: true,
                responsive: false,
                lengthMenu: [
                    [10, 25, 50, -1],
                    [10, 25, 50, 'All'],
                ],
                language: {
                    url: 'https://cdn.datatables.net/plug-ins/1.13.1/i18n/pt-BR.json'
                },
                columns: [
                    { title: 'Comando' },
                    { title: 'Tipo' },
                    { title: 'Último uso' },
                    { title: 'Status' },
                    { title: 'Delay' },
                    { title: 'Recompensa' },
                    {
                        title: 'Resposta',
                        render: function (data, type, row) {
                          if (type === "display" && data.length > 20) {
                            return '<span title="' + data + '">' + data.substring(0, 20) + '...</span>';
                          } else {
                            return data;
                          }
                        }
                      },
                    { title: 'Nível do usuário' }
                ]
            } );

            // adicionar as linhas à tabela
            for (var i = 0; i < dataTableData.length; i++) {
                table.row.add(dataTableData[i]).draw();
            }

        }
    }
}
