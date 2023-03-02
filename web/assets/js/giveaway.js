async function giveaway_js(event,type_id) {
    if (type_id == 'get_config') {

        var giveaway_name_inp = document.getElementById("giveaway-name");
        var giveaway_user_level = document.getElementById("user-level-giveaway");
        var giveaway_clear = document.getElementById("giveaway-clear-names-end");
        var giveaway_enable = document.getElementById('giveaway-enable');
        var giveaway_mult = document.getElementById('giveaway-mult');

        var execute_giveaway = document.getElementById("command-execute-giveaway");
        var execute_delay = document.getElementById("command-execute-delay");
        var check_user_giveaway = document.getElementById("command-check-user-giveaway");
        var check_user_delay = document.getElementById("command-check-user-delay");
        var clear_giveaway = document.getElementById("command-clear-giveaway");
        var clear_delay = document.getElementById("command-clear-delay");
        var add_user_giveaway = document.getElementById('command-add-user-giveaway');
        var add_user_delay = document.getElementById('command-add-user-delay');
        var self_check_giveaway = document.getElementById('command-self-check-giveaway');
        var self_check_delay = document.getElementById('command-self-check-delay');

        var el_id = "redeem-select-giveaway";

    
        var giveaway_info = await eel.giveaway_py(type_id,'null')();
    
        if (giveaway_info) {
            
            var giveaway_info_parse = JSON.parse(giveaway_info);
    
            var list_redem = await eel.get_redeem('giveaway')();
    
            if (list_redem) {
    
                $("#" + el_id).empty();
    
                var list_redem_parse = JSON.parse(list_redem);
    
                $("#" + el_id).append('<option class="bg-dark" style="color: #fff;" value="None">Sem recompensa</option>');
                $("#" + el_id).selectpicker("refresh");
    
                for (var i = 0; i < list_redem_parse.redeem.length; i++) {
                    var optn = list_redem_parse.redeem[i];
    
                    $("#" + el_id).append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
                    $("#" + el_id).selectpicker("refresh");
                }
            }
    
            $("#" + el_id).selectpicker('val',giveaway_info_parse.giveaway_redeem)
    
            giveaway_clear_receive = giveaway_info_parse.giveaway_clear
            giveaway_enable_receive = giveaway_info_parse.giveaway_enable
            giveaway_mult_receive = giveaway_info_parse.giveaway_mult
            
    
            if (giveaway_clear_receive == 1) {
                giveaway_clear.checked = true
            } else if (giveaway_clear_receive == 0) {
                giveaway_clear.checked = false
            }
    
            if (giveaway_enable_receive == 1) {
                giveaway_enable.checked = true
            } else if (giveaway_enable_receive == 0) {
                giveaway_enable.checked = false
            }
    
            if (giveaway_mult_receive == 1) {
                giveaway_mult.checked = true
            } else if (giveaway_mult_receive == 0) {
                giveaway_mult.checked = false
            }
    
            giveaway_name_inp.value = giveaway_info_parse.giveaway_name;
            giveaway_user_level.value = giveaway_info_parse.giveaway_level;

            execute_giveaway.value = giveaway_info_parse.execute_giveaway;
            execute_delay.value = giveaway_info_parse.execute_delay;
            check_user_giveaway.value = giveaway_info_parse.user_check_giveaway;
            check_user_delay.value = giveaway_info_parse.user_check_delay;
            clear_giveaway.value = giveaway_info_parse.clear_giveaway;
            clear_delay.value = giveaway_info_parse.clear_delay;
            add_user_giveaway.value = giveaway_info_parse.add_user_giveaway;
            add_user_delay.value = giveaway_info_parse.add_user_delay;
            self_check_giveaway.value = giveaway_info_parse.self_check_giveaway;
            self_check_delay.value = giveaway_info_parse.self_check_delay;
    
        }

    } else if (type_id == 'show_names'){

        var name_list = await eel.giveaway_py(type_id,'null')();

        if (name_list) {
    
            name_list_parse = JSON.parse(name_list);
    
            $("#giveaway-modal").modal("show");
    
            var tbody_give = document.getElementById('giveaway-list-body');
    
            tbody_give.innerHTML = ''
    
            Object.entries(name_list_parse).forEach(([k,v]) => {
    
                tbody_give.innerHTML += '<tr><td style="width: 10px">' + k + '</td><td>' + v + '</td></tr>';
    
            })
            
    
        }

    } else if (type_id == 'save_config'){
        
        event.preventDefault();

        var form = document.querySelector("#giveaway-config-form");
        giveaway_clear_check_inp = form.querySelector('input[id="giveaway-clear-names-end"]').checked;
        giveaway_enable_inp = form.querySelector('input[id="giveaway-enable"]').checked;
        giveaway_mult_inp = form.querySelector('input[id="giveaway-mult"]').checked;
    
        if (giveaway_clear_check_inp == true) {
            giveaway_clear_check_value = 1;
        } else {
            giveaway_clear_check_value = 0;
        }
    
        if (giveaway_enable_inp == true) {
            giveaway_enable_value = 1;
        } else {
            giveaway_enable_value = 0;
        }
    
        if (giveaway_mult_inp == true) {
            giveaway_mult_value = 1;
        } else {
            giveaway_mult_value = 0;
        }
    
        data = {
            giveaway_name: form.querySelector('input[id="giveaway-name"]').value,
            giveaway_redeem: form.querySelector('select[id="redeem-select-giveaway"]').value,
            giveaway_user_level: form.querySelector('select[id="user-level-giveaway"]').value,
            giveaway_clear_check: giveaway_clear_check_value,
            giveaway_enable: giveaway_enable_value,
            giveaway_mult: giveaway_mult_value,
        };
    
        var formData = JSON.stringify(data);
    
        eel.giveaway_py(type_id,formData);


    } else if (type_id == 'save_commands'){
        event.preventDefault();

        var form = document.querySelector("#giveaway-config-commands-form");
    
        data = {
            
            execute_giveaway: form.querySelector("#command-execute-giveaway").value,
            execute_delay : form.querySelector("#command-execute-delay").value,
            self_check_giveaway: form.querySelector("#command-self-check-giveaway").value,
            self_check_delay: form.querySelector("#command-self-check-delay").value,
            check_user_giveaway: form.querySelector("#command-check-user-giveaway").value,
            check_user_delay: form.querySelector("#command-check-user-delay").value,
            clear_giveaway: form.querySelector("#command-clear-giveaway").value,
            clear_delay: form.querySelector("#command-clear-delay").value,
            add_user_giveaway: form.querySelector("#command-add-user-giveaway").value,
            add_user_delay: form.querySelector("#command-add-user-delay").value
        }

        console.log(data)
    
        var formData = JSON.stringify(data);
        eel.giveaway_py(type_id,formData);

    } else if (type_id == 'add_user'){

        event.preventDefault();

        var form = document.querySelector("#giveaway-add-user-form");
        var add_name = form.elements[0].value;
        
        data = {
            new_name: add_name,
            user_level: 'mod'
        }

        var formData = JSON.stringify(data);
        eel.giveaway_py(type_id,formData);


    } else if (type_id == 'execute'){
        eel.giveaway_py(type_id,'null');
    } else if (type_id == 'clear_list'){
        eel.giveaway_py(type_id,'null');
    }
}



