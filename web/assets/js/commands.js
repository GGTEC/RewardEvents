//COMANDOS

function show_commands_div(div_id) {

    if (div_id == "del-commands-div") {
        commands_fun('event','get_list');
    } else if (div_id == "edit-commands-div") {
        commands_fun('event','get_list');
    } else if (div_id == "delay-commands-div") {
        commands_fun('event','get_delay');
    } else if (div_id == "duel-commands-div"){
        commands_fun('event','get_duel');
    } else if (div_id == "default-commands-div"){
        commands_fun('event','get_default');
    }

    document.getElementById("commands-div").hidden = true;
    document.getElementById(div_id).hidden = false;
}

function hide_commands_div(div_id, modal) {

    $("#" + modal).modal("hide");
    document.getElementById("commands-div").hidden = false;
    document.getElementById(div_id).hidden = true;

}

function exibirFormulario(valor) {
    const formularios = [
      '#form-cmd-command',
      '#form-dice-command',
      '#form-random-command',
      '#form-uptime-command',
      '#form-followage-command',
      '#form-game-command',
      '#form-msgcount-command',
      '#form-watchtime-command',
      '#form-interaction_1-command',
      '#form-interaction_2-command',
      '#form-interaction_3-command',
      '#form-interaction_4-command',
      '#form-interaction_5-command'
    ];
  
    for (const form of formularios) {
      document.querySelector(form).hidden = true;
    }
  
    document.querySelector(`#form-${valor}-command`).hidden = false;
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

        eel.commands_py('create',formData);

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

        eel.commands_py(type_id,formData);
        form.reset();


    } else if (type_id == 'delete'){

        event.preventDefault();

        var form = document.querySelector("#command-del-form");
        var command = form.querySelector('select[id="command-select-del"]').value;

        eel.commands_py(type_id,command);
        form.reset();
        $("#command-select-del option:selected").remove();
        $("#command-select-del").selectpicker("refresh");

    } else if (type_id == 'get_list'){

        var command_info = await eel.commands_py(type_id,'null')();

        if (command_info) {

            $("#command-select-del").empty();
            $("#command-select-del").selectpicker("refresh");
            $("#command-select-edit").empty();
            $("#command-select-edit").selectpicker("refresh");
    
            var list_command_parse = JSON.parse(command_info);
    
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
        var command_info = await eel.commands_py(type_id,command)();

        if (command_info) {

            var command_info_parse = JSON.parse(command_info);
            
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

        var duel_info = await eel.commands_py(type_id,'null')();

        if (duel_info){
            var duel_info_parse = JSON.parse(duel_info);

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
            var duel_rec = await eel.commands_py(type_id,select_battle.value)();

            if (duel_rec){
    
                
                var duel_battle_parse = JSON.parse(duel_rec);
    
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
        eel.commands_py(type_id,formData);

    
    } else if (type_id == 'get_default'){

        var cmd_val = document.getElementById('command-cmd');
        var cmd_status = document.getElementById('command-cmd-status');
        var cmd_delay = document.getElementById('cmd-delay');
        var cmd_respo = ""
        var cmd_perm = document.getElementById('command-cmd-perm');

        var dice_val = document.getElementById('command-dice');
        var dice_status = document.getElementById('command-dice-status');
        var dice_delay = document.getElementById('dice-delay');
        var dice_respo = document.getElementById('command-dice-response');
        var dice_perm = document.getElementById('command-dice-perm');

        var random_val = document.getElementById('command-random');
        var random_status = document.getElementById('command-random-status');
        var random_delay = document.getElementById('random-delay');
        var random_respo = document.getElementById('command-random-response');
        var random_perm = document.getElementById('command-random-perm');

        var uptime = document.getElementById('command-uptime');
        var uptime_status = document.getElementById('command-uptime-status');
        var uptime_delay = document.getElementById('uptime-delay');
        var uptime_respo = document.getElementById('command-uptime-response');
        var uptime_perm = document.getElementById('command-uptime-perm');

        var game = document.getElementById('command-game');
        var game_status = document.getElementById('command-game-status');
        var game_delay = document.getElementById('game-delay');
        var game_respo = document.getElementById('command-game-response');
        var game_perm = document.getElementById('command-game-perm');

        var msgcount = document.getElementById('command-msgcount');
        var msgcount_status = document.getElementById('command-msgcount-status');
        var msgcount_delay = document.getElementById('msgcount-delay');
        var msgcount_respo = document.getElementById('command-msgcount-response');
        var msgcount_perm = document.getElementById('command-msgcount-perm');

        var watchtime = document.getElementById('command-watchtime');
        var watchtime_status = document.getElementById('command-watchtime-status');
        var watchtime_delay = document.getElementById('watchtime-delay');
        var watchtime_respo = document.getElementById('command-watchtime-response');
        var watchtime_perm = document.getElementById('command-watchtime-perm');

        var followage = document.getElementById('command-followage');
        var followage_status = document.getElementById('command-followage-status');
        var followage_delay = document.getElementById('followage-delay');
        var followage_respo = document.getElementById('command-followage-response');
        var followage_perm = document.getElementById('command-followage-perm');

        var interaction_1_val = document.getElementById('command-interaction_1');
        var interaction_1_status = document.getElementById('command-interaction_1-status');
        var interaction_1_delay = document.getElementById('interaction_1-delay');
        var interaction_1_respo = document.getElementById('command-interaction_1-response');
        var interaction_1_perm = document.getElementById('command-interaction_1-perm');

        var interaction_2_val = document.getElementById('command-interaction_2');
        var interaction_2_status = document.getElementById('command-interaction_2-status');
        var interaction_2_delay = document.getElementById('interaction_2-delay');
        var interaction_2_respo = document.getElementById('command-interaction_2-response');
        var interaction_2_perm = document.getElementById('command-interaction_2-perm');

        var interaction_3_val = document.getElementById('command-interaction_3');
        var interaction_3_status = document.getElementById('command-interaction_3-status');
        var interaction_3_delay = document.getElementById('interaction_3-delay');
        var interaction_3_respo = document.getElementById('command-interaction_3-response');
        var interaction_3_perm = document.getElementById('command-interaction_3-perm');

        var interaction_4_val = document.getElementById('command-interaction_4');
        var interaction_4_status = document.getElementById('command-interaction_4-status');
        var interaction_4_delay = document.getElementById('interaction_4-delay');
        var interaction_4_respo = document.getElementById('command-interaction_4-response');
        var interaction_4_perm = document.getElementById('command-interaction_4-perm');

        var interaction_5_val = document.getElementById('command-interaction_5');
        var interaction_5_status = document.getElementById('command-interaction_5-status');
        var interaction_5_delay = document.getElementById('interaction_5-delay');
        var interaction_5_respo = document.getElementById('command-interaction_5-response');
        var interaction_5_perm = document.getElementById('command-interaction_5-perm');


        var resp_default = await eel.commands_py(type_id,'null')();

        if (resp_default) {


            var resp_default_parse = JSON.parse(resp_default);

            if (resp_default_parse.cmd_status == 1){
                cmd_status.checked = true;
            } else if (resp_default_parse.cmd_status = 0){
                cmd_status.checked = false;
            }
            
            if (resp_default_parse.dice_status == 1){
                dice_status.checked = true;
            } else if (resp_default_parse.dice_status = 0){
                dice_status.checked = false;
            }
            if (resp_default_parse.random_status == 1){
                random_status = true;
            } else if (resp_default_parse.random_status = 0){
                random_status = false;
            }
            if (resp_default_parse.uptime_status == 1){
                uptime_status = true;
            } else if (resp_default_parse.uptime_status = 0){
                uptime_status = false;
            }
            if (resp_default_parse.msgcount_status == 1){
                msgcount_status = true;
            } else if (resp_default_parse.msgcount_status = 0){
                msgcount_status = false;
            }
            if (resp_default_parse.watchtime_status == 1){
                watchtime_status = true;
            } else if (resp_default_parse.watchtime_status = 0){
                watchtime_status = false;
            }
            if (resp_default_parse.followage_status == 1){
                followage_status = true;
            } else if (resp_default_parse.followage_status = 0){
                followage_status = false;
            }
            if (resp_default_parse.interaction_1_status == 1){
                interaction_1_status = true;
            } else if (resp_default_parse.interaction_1_status = 0){
                interaction_1_status = false;
            }
            if (resp_default_parse.interaction_2_status == 1){
                interaction_2_status = true;
            } else if (resp_default_parse.interaction_2_status = 0){
                interaction_2_status = false;
            }
            if (resp_default_parse.interaction_3_status == 1){
                interaction_3_status = true;
            } else if (resp_default_parse.interaction_3_status = 0){
                interaction_3_status = false;
            }
            if (resp_default_parse.interaction_4_status == 1){
                interaction_4_status = true;
            } else if (resp_default_parse.interaction_4_status = 0){
                interaction_4_status = false;
            }
            if (resp_default_parse.interaction_5_status == 1){
                interaction_5_status = true;
            } else if (resp_default_parse.interaction_5_status = 0){
                interaction_5_status = false;
            }

            cmd_val.value = resp_default_parse.cmd;
            cmd_delay.value = resp_default_parse.cmd_delay;

            dice_val.value = resp_default_parse.dice;
            dice_delay.value = resp_default_parse.dice_delay;
            dice_respo.value = resp_default_parse.dice_resp;

            random_val.value = resp_default_parse.random;
            random_delay.value = resp_default_parse.random_delay;
            random_respo.value = resp_default_parse.random_resp;

            uptime.value = resp_default_parse.uptime;
            uptime_delay.value = resp_default_parse.uptime_delay;
            uptime_respo.value = resp_default_parse.uptime_resp;

            game.value = resp_default_parse.game;
            game_delay.value = resp_default_parse.game_delay;
            game_respo.value = resp_default_parse.game_resp;

            msgcount.value = resp_default_parse.msgcount;
            msgcount_delay.value = resp_default_parse.msgcount_delay;
            msgcount_respo.value = resp_default_parse.msgcount_resp;

            watchtime.value = resp_default_parse.watchtime;
            watchtime_delay.value = resp_default_parse.watchtime_delay;
            watchtime_respo.value = resp_default_parse.watchtime_resp;

            followage.value = resp_default_parse.followage;
            followage_delay.value = resp_default_parse.followage_delay;
            followage_respo.value = resp_default_parse.followage_resp;

            interaction_1_val.value = resp_default_parse.interaction_1;
            interaction_1_delay.value = resp_default_parse.interaction_1_delay;
            interaction_1_respo.value = resp_default_parse.interaction_1_resp;
            interaction_2_val.value = resp_default_parse.interaction_2;
            interaction_2_delay.value = resp_default_parse.interaction_2_delay;
            interaction_2_respo.value = resp_default_parse.interaction_2_resp;
            interaction_3_val.value = resp_default_parse.interaction_3;
            interaction_3_delay.value = resp_default_parse.interaction_3_delay;
            interaction_3_respo.value = resp_default_parse.interaction_3_resp;
            interaction_4_val.value = resp_default_parse.interaction_4;
            interaction_4_delay.value = resp_default_parse.interaction_4_delay;
            interaction_4_respo.value = resp_default_parse.interaction_4_resp;
            interaction_5_val.value = resp_default_parse.interaction_5;
            interaction_5_delay.value = resp_default_parse.interaction_5_delay;
            interaction_5_respo.value = resp_default_parse.interaction_5_resp;

            $("#command-cmd-perm").selectpicker('val', resp_default_parse.cmd_perm)
            $("#command-dice-perm").selectpicker('val', resp_default_parse.dice_perm)
            $("#command-random-perm").selectpicker('val', resp_default_parse.random_perm)
            $("#command-uptime-perm").selectpicker('val', resp_default_parse.uptime_perm)
            $("#command-game-perm").selectpicker('val',resp_default_parse.game_perm)
            $("#command-msgcount-perm").selectpicker('val',resp_default_parse.msgcount_perm)
            $("#command-followage-perm").selectpicker('val',resp_default_parse.followage_perm)
            $("#command-watchtime-perm").selectpicker('val',resp_default_parse.watchtime_perm)


            $("#command-interaction_1-perm").selectpicker('val', resp_default_parse.interaction_1_perm)
            $("#command-interaction_2-perm").selectpicker('val', resp_default_parse.interaction_2_perm)
            $("#command-interaction_3-perm").selectpicker('val', resp_default_parse.interaction_3_perm)
            $("#command-interaction_4-perm").selectpicker('val', resp_default_parse.interaction_4_perm)
            $("#command-interaction_5-perm").selectpicker('val', resp_default_parse.interaction_5_perm)
        }


    } else if (type_id == 'save_default'){
        event.preventDefault();

        var dice_val = document.getElementById('command-dice');
        var dice_status = document.getElementById('command-dice-status');
        var dice_delay = document.getElementById('dice-delay');
        var dice_respo = document.getElementById('command-dice-response');
        var dice_perm = document.getElementById('command-dice-perm');

        var random_val = document.getElementById('command-random');
        var random_status = document.getElementById('command-random-status');
        var random_delay = document.getElementById('random-delay');
        var random_respo = document.getElementById('command-random-response');
        var random_perm = document.getElementById('command-random-perm');

        var uptime = document.getElementById('command-uptime');
        var uptime_status = document.getElementById('command-uptime-status');
        var uptime_delay = document.getElementById('uptime-delay');
        var uptime_respo = document.getElementById('command-uptime-response');
        var uptime_perm = document.getElementById('command-uptime-perm');

        var game = document.getElementById('command-game');
        var game_status = document.getElementById('command-game-status');
        var game_delay = document.getElementById('game-delay');
        var game_respo = document.getElementById('command-game-response');
        var game_perm = document.getElementById('command-game-perm');

        var followage = document.getElementById('command-followage');
        var followage_status = document.getElementById('command-followage-status');
        var followage_delay = document.getElementById('followage-delay');
        var followage_respo = document.getElementById('command-followage-response');
        var followage_perm = document.getElementById('command-followage-perm');

        var interaction_1_val = document.getElementById('command-interaction_1');
        var interaction_1_status = document.getElementById('command-interaction_1-status');
        var interaction_1_delay = document.getElementById('interaction_1-delay');
        var interaction_1_respo = document.getElementById('command-interaction_1-response');
        var interaction_1_perm = document.getElementById('command-interaction_1-perm');

        var interaction_2_val = document.getElementById('command-interaction_2');
        var interaction_2_status = document.getElementById('command-interaction_2-status');
        var interaction_2_delay = document.getElementById('interaction_2-delay');
        var interaction_2_respo = document.getElementById('command-interaction_2-response');
        var interaction_2_perm = document.getElementById('command-interaction_2-perm');

        var interaction_3_val = document.getElementById('command-interaction_3');
        var interaction_3_status = document.getElementById('command-interaction_3-status');
        var interaction_3_delay = document.getElementById('interaction_3-delay');
        var interaction_3_respo = document.getElementById('command-interaction_3-response');
        var interaction_3_perm = document.getElementById('command-interaction_3-perm');

        var interaction_4_val = document.getElementById('command-interaction_4');
        var interaction_4_status = document.getElementById('command-interaction_4-status');
        var interaction_4_delay = document.getElementById('interaction_4-delay');
        var interaction_4_respo = document.getElementById('command-interaction_4-response');
        var interaction_4_perm = document.getElementById('command-interaction_4-perm');

        var interaction_5_val = document.getElementById('command-interaction_5');
        var interaction_5_status = document.getElementById('command-interaction_5-status');
        var interaction_5_delay = document.getElementById('interaction_5-delay');
        var interaction_5_respo = document.getElementById('command-interaction_5-response');
        var interaction_5_perm = document.getElementById('command-interaction_5-perm');


        if (dice_status.checked == true) {
            dice_status = 1
        } else {
            dice_status = 0
        }
        if (random_status.checked == true){
            random_status = 1
        } else {
            random_status = 0
        }
        if (uptime_status.checked == true){
            uptime_status = 1
        } else {
            uptime_status = 0
        }
        if (game_status.checked == true){
            game_status = 1
        } else {
            game_status = 0
        }
        if (followage_status.checked == true){
            followage_status = 1
        } else {
            followage_status = 0
        }
        if (interaction_1_status.checked == true){
            interaction_1_status = 1
        } else {
            interaction_1_status = 0
        }
        if (interaction_2_status.checked == true){
            interaction_2_status = 1
        } else {
            interaction_2_status = 0
        }
        if (interaction_3_status.checked == true){
            interaction_3_status = 1
        } else {
            interaction_3_status = 0
        }        
        if (interaction_3_status.checked == true){
            interaction_3_status = 1
        } else {
            interaction_3_status = 0
        }
        if (interaction_4_status.checked == true){
            interaction_4_status = 1
        } else {
            interaction_4_status = 0
        }
        if (interaction_5_status.checked == true){
            interaction_5_status = 1
        } else {
            interaction_5_status = 0
        }


        data = {
            dice : dice_val.value,
            dice_status: dice_status,
            dice_delay: dice_delay.value,
            dice_respo : dice_respo.value,
            dice_perm : dice_perm.value,
            random : random_val.value,
            random_status: random_status,
            random_delay: random_delay.value,
            random_respo : random_respo.value,
            random_perm : random_perm.value,
            uptime : uptime.value,
            uptime_status: uptime_status,
            uptime_delay: uptime_delay.value,
            uptime_respo : uptime_respo.value,
            uptime_perm : uptime_perm.value,
            game : game.value,
            game_status: game_status,
            game_delay: game_delay.value,
            game_respo : game_respo.value,
            game_perm : game_perm.value,
            followage : followage.value,
            followage_status: followage_status,
            followage_delay : followage_delay.value,
            followage_respo : followage_respo.value,
            followage_perm : followage_perm.value,
            interaction_1 : interaction_1_val.value,
            interaction_1_status : interaction_1_status,
            interaction_1_delay : interaction_1_delay.value,
            interaction_1_respo : interaction_1_respo.value,
            interaction_1_perm : interaction_1_perm.value,
            interaction_2 : interaction_2_val.value,
            interaction_2_status: interaction_2_status,
            interaction_2_delay: interaction_2_delay.value,
            interaction_2_respo : interaction_2_respo.value,
            interaction_2_perm : interaction_2_perm.value,
            interaction_3 : interaction_3_val.value,
            interaction_3_status: interaction_3_status,
            interaction_3_delay : interaction_3_delay.value,
            interaction_3_respo : interaction_3_respo.value,
            interaction_3_perm : interaction_3_perm.value,
            interaction_4 : interaction_4_val.value,
            interaction_4_status: interaction_4_status,
            interaction_4_delay : interaction_4_delay.value,
            interaction_4_respo : interaction_4_respo.value,
            interaction_4_perm : interaction_4_perm.value,
            interaction_5 : interaction_5_val.value,
            interaction_5_status : interaction_5_status,
            interaction_5_delay : interaction_5_delay.value,
            interaction_5_respo : interaction_5_respo.value,
            interaction_5_perm : interaction_5_perm.value
        }

        var formData = JSON.stringify(data);
        eel.commands_py(type_id,formData);
    } else if (type_id == 'save_default-cmd'){
        
        event.preventDefault();

        var cmd_val = document.getElementById('command-cmd');
        var cmd_status = document.getElementById('command-cmd-status');
        var cmd_delay = document.getElementById('cmd-delay');
        var cmd_respo = "";
        var cmd_perm = document.getElementById('command-cmd-perm');


        if (cmd_status.checked == true) {
            cmd_status = 1
        } else {
            cmd_status = 0
        }

        data = {
            cmd : cmd_val.value,
            cmd_status: cmd_status,
            cmd_delay: cmd_delay.value,
            cmd_respo : cmd_respo.value,
            cmd_perm : cmd_perm.value,
        }

        var formData = JSON.stringify(data);
        eel.commands_py(type_id,formData);

    } else if (type_id == 'save_default-dice'){
        
        event.preventDefault();

        var dice_val = document.getElementById('command-dice');
        var dice_status = document.getElementById('command-dice-status');
        var dice_delay = document.getElementById('dice-delay');
        var dice_respo = document.getElementById('command-dice-response');
        var dice_perm = document.getElementById('command-dice-perm');


        if (dice_status.checked == true) {
            dice_status = 1
        } else {
            dice_status = 0
        }


        data = {
            dice : dice_val.value,
            dice_status: dice_status,
            dice_delay: dice_delay.value,
            dice_respo : dice_respo.value,
            dice_perm : dice_perm.value,
        }

        var formData = JSON.stringify(data);
        eel.commands_py(type_id,formData);

    } else if (type_id == 'save_default-random'){
        
        event.preventDefault();

        var random_val = document.getElementById('command-random');
        var random_status = document.getElementById('command-random-status');
        var random_delay = document.getElementById('random-delay');
        var random_respo = document.getElementById('command-random-response');
        var random_perm = document.getElementById('command-random-perm');

        
        if (random_status.checked == true){
            random_status = 1
        } else {
            random_status = 0
        }

        data = {
            random : random_val.value,
            random_status: random_status,
            random_delay: random_delay.value,
            random_respo : random_respo.value,
            random_perm : random_perm.value,
        }

        var formData = JSON.stringify(data);
        eel.commands_py(type_id,formData);
    } else if (type_id == 'save_default-uptime'){
        
        event.preventDefault();


        var uptime = document.getElementById('command-uptime');
        var uptime_status = document.getElementById('command-uptime-status');
        var uptime_delay = document.getElementById('uptime-delay');
        var uptime_respo = document.getElementById('command-uptime-response');
        var uptime_perm = document.getElementById('command-uptime-perm');

        
        if (uptime_status.checked == true){
            uptime_status = 1
        } else {
            uptime_status = 0
        }


        data = {
            uptime : uptime.value,
            uptime_status: uptime_status,
            uptime_delay: uptime_delay.value,
            uptime_respo : uptime_respo.value,
            uptime_perm : uptime_perm.value,
        }

        var formData = JSON.stringify(data);
        eel.commands_py(type_id,formData);
    } else if (type_id == 'save_default-game'){
        
        event.preventDefault();

        var game = document.getElementById('command-game');
        var game_status = document.getElementById('command-game-status');
        var game_delay = document.getElementById('game-delay');
        var game_respo = document.getElementById('command-game-response');
        var game_perm = document.getElementById('command-game-perm');


        if (game_status.checked == true){
            game_status = 1
        } else {
            game_status = 0
        }

        data = {
            game : game.value,
            game_status: game_status,
            game_delay: game_delay.value,
            game_respo : game_respo.value,
            game_perm : game_perm.value,
        }

        var formData = JSON.stringify(data);
        eel.commands_py(type_id,formData);
    } else if (type_id == 'save_default-followage'){
        
        event.preventDefault();

        var followage = document.getElementById('command-followage');
        var followage_status = document.getElementById('command-followage-status');
        var followage_delay = document.getElementById('followage-delay');
        var followage_respo = document.getElementById('command-followage-response');
        var followage_perm = document.getElementById('command-followage-perm');

        if (followage_status.checked == true){
            followage_status = 1
        } else {
            followage_status = 0
        }


        data = {
            followage : followage.value,
            followage_status: followage_status,
            followage_delay : followage_delay.value,
            followage_respo : followage_respo.value,
            followage_perm : followage_perm.value,
        }

        var formData = JSON.stringify(data);
        eel.commands_py(type_id,formData);
    } else if (type_id == 'save_default-msgcount'){
        
        event.preventDefault();

        var msgcount = document.getElementById('command-msgcount');
        var msgcount_status = document.getElementById('command-msgcount-status');
        var msgcount_delay = document.getElementById('msgcount-delay');
        var msgcount_respo = document.getElementById('command-msgcount-response');
        var msgcount_perm = document.getElementById('command-msgcount-perm');

        if (msgcount_status.checked == true){
            msgcount_status = 1
        } else {
            msgcount_status = 0
        }

        data = {
            msgcount : msgcount.value,
            msgcount_status: msgcount_status,
            msgcount_delay : msgcount_delay.value,
            msgcount_respo : msgcount_respo.value,
            msgcount_perm : msgcount_perm.value,
        }

        var formData = JSON.stringify(data);
        eel.commands_py(type_id,formData);

    } else if (type_id == 'save_default-watchtime'){
        
        event.preventDefault();

        var watchtime = document.getElementById('command-watchtime');
        var watchtime_status = document.getElementById('command-watchtime-status');
        var watchtime_delay = document.getElementById('watchtime-delay');
        var watchtime_respo = document.getElementById('command-watchtime-response');
        var watchtime_perm = document.getElementById('command-watchtime-perm');

        if (watchtime_status.checked == true){
            watchtime_status = 1
        } else {
            watchtime_status = 0
        }

        data = {
            watchtime : watchtime.value,
            watchtime_status: watchtime_status,
            watchtime_delay : watchtime_delay.value,
            watchtime_respo : watchtime_respo.value,
            watchtime_perm : watchtime_perm.value,
        }

        var formData = JSON.stringify(data);
        eel.commands_py(type_id,formData);

    } else if (type_id == 'save_default-interaction_1'){
        
        event.preventDefault();

        var interaction_1_val = document.getElementById('command-interaction_1');
        var interaction_1_status = document.getElementById('command-interaction_1-status');
        var interaction_1_delay = document.getElementById('interaction_1-delay');
        var interaction_1_respo = document.getElementById('command-interaction_1-response');
        var interaction_1_perm = document.getElementById('command-interaction_1-perm');


        if (interaction_1_status.checked == true){
            interaction_1_status = 1
        } else {
            interaction_1_status = 0
        }

        data = {
            dice : dice_val.value,
            dice_status: dice_status,
            dice_delay: dice_delay.value,
            dice_respo : dice_respo.value,
            dice_perm : dice_perm.value,
            random : random_val.value,
            random_status: random_status,
            random_delay: random_delay.value,
            random_respo : random_respo.value,
            random_perm : random_perm.value,
            uptime : uptime.value,
            uptime_status: uptime_status,
            uptime_delay: uptime_delay.value,
            uptime_respo : uptime_respo.value,
            uptime_perm : uptime_perm.value,
            game : game.value,
            game_status: game_status,
            game_delay: game_delay.value,
            game_respo : game_respo.value,
            game_perm : game_perm.value,
            followage : followage.value,
            followage_status: followage_status,
            followage_delay : followage_delay.value,
            followage_respo : followage_respo.value,
            followage_perm : followage_perm.value,
            interaction_1 : interaction_1_val.value,
            interaction_1_status : interaction_1_status,
            interaction_1_delay : interaction_1_delay.value,
            interaction_1_respo : interaction_1_respo.value,
            interaction_1_perm : interaction_1_perm.value,
            interaction_2 : interaction_2_val.value,
            interaction_2_status: interaction_2_status,
            interaction_2_delay: interaction_2_delay.value,
            interaction_2_respo : interaction_2_respo.value,
            interaction_2_perm : interaction_2_perm.value,
            interaction_3 : interaction_3_val.value,
            interaction_3_status: interaction_3_status,
            interaction_3_delay : interaction_3_delay.value,
            interaction_3_respo : interaction_3_respo.value,
            interaction_3_perm : interaction_3_perm.value,
            interaction_4 : interaction_4_val.value,
            interaction_4_status: interaction_4_status,
            interaction_4_delay : interaction_4_delay.value,
            interaction_4_respo : interaction_4_respo.value,
            interaction_4_perm : interaction_4_perm.value,
            interaction_5 : interaction_5_val.value,
            interaction_5_status : interaction_5_status,
            interaction_5_delay : interaction_5_delay.value,
            interaction_5_respo : interaction_5_respo.value,
            interaction_5_perm : interaction_5_perm.value
        }

        var formData = JSON.stringify(data);
        eel.commands_py(type_id,formData);
    } else if (type_id == 'save_default-interaction_2'){
        
        event.preventDefault();

        var interaction_2_val = document.getElementById('command-interaction_2');
        var interaction_2_status = document.getElementById('command-interaction_2-status');
        var interaction_2_delay = document.getElementById('interaction_2-delay');
        var interaction_2_respo = document.getElementById('command-interaction_2-response');
        var interaction_2_perm = document.getElementById('command-interaction_2-perm');

        
        if (interaction_2_status.checked == true){
            interaction_2_status = 1
        } else {
            interaction_2_status = 0
        }


        data = {
            interaction_2 : interaction_2_val.value,
            interaction_2_status: interaction_2_status,
            interaction_2_delay: interaction_2_delay.value,
            interaction_2_respo : interaction_2_respo.value,
            interaction_2_perm : interaction_2_perm.value,
        }

        var formData = JSON.stringify(data);
        eel.commands_py(type_id,formData);
    } else if (type_id == 'save_default-interaction_3'){
        
        event.preventDefault();

        var interaction_3_val = document.getElementById('command-interaction_3');
        var interaction_3_status = document.getElementById('command-interaction_3-status');
        var interaction_3_delay = document.getElementById('interaction_3-delay');
        var interaction_3_respo = document.getElementById('command-interaction_3-response');
        var interaction_3_perm = document.getElementById('command-interaction_3-perm');

        if (interaction_3_status.checked == true){
            interaction_3_status = 1
        } else {
            interaction_3_status = 0
        }        


        data = {
            interaction_3 : interaction_3_val.value,
            interaction_3_status: interaction_3_status,
            interaction_3_delay : interaction_3_delay.value,
            interaction_3_respo : interaction_3_respo.value,
            interaction_3_perm : interaction_3_perm.value,
        }

        var formData = JSON.stringify(data);
        eel.commands_py(type_id,formData);
    } else if (type_id == 'save_default-interaction_4'){
        
        event.preventDefault();

        var interaction_4_val = document.getElementById('command-interaction_4');
        var interaction_4_status = document.getElementById('command-interaction_4-status');
        var interaction_4_delay = document.getElementById('interaction_4-delay');
        var interaction_4_respo = document.getElementById('command-interaction_4-response');
        var interaction_4_perm = document.getElementById('command-interaction_4-perm');

        if (interaction_4_status.checked == true){
            interaction_4_status = 1
        } else {
            interaction_4_status = 0
        }



        data = {
            
            interaction_4 : interaction_4_val.value,
            interaction_4_status: interaction_4_status,
            interaction_4_delay : interaction_4_delay.value,
            interaction_4_respo : interaction_4_respo.value,
            interaction_4_perm : interaction_4_perm.value,
        }

        var formData = JSON.stringify(data);
        eel.commands_py(type_id,formData);
    } else if (type_id == 'save_default-interaction_5'){
        
        event.preventDefault();

        var interaction_5_val = document.getElementById('command-interaction_5');
        var interaction_5_status = document.getElementById('command-interaction_5-status');
        var interaction_5_delay = document.getElementById('interaction_5-delay');
        var interaction_5_respo = document.getElementById('command-interaction_5-response');
        var interaction_5_perm = document.getElementById('command-interaction_5-perm');

        if (interaction_5_status.checked == true){
            interaction_5_status = 1
        } else {
            interaction_5_status = 0
        }


        data = {
            interaction_5 : interaction_5_val.value,
            interaction_5_status : interaction_5_status,
            interaction_5_delay : interaction_5_delay.value,
            interaction_5_respo : interaction_5_respo.value,
            interaction_5_perm : interaction_5_perm.value
        }

        var formData = JSON.stringify(data);
        eel.commands_py(type_id,formData);
        
    } else if (type_id == 'select_edit'){

        var select_editor = document.querySelector('#command-default-edit');
        exibirFormulario(select_editor.value);
    }
}