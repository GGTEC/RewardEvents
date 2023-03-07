async function counter_js(fun_id,event) {
    event.preventDefault();

    var el_id = "redeem-select-counter";
    var counter_value = document.getElementById('counter-value-atual');
    var command_applycounter_status = document.getElementById('command-applycounter-status');
    var command_resetcounter_status = document.getElementById('command-resetcounter-status');
    var command_checkcounter_status = document.getElementById('command-checkcounter-status');
    
    var response_status = document.getElementById('response-counter-status');
    var response_counter = document.getElementById('counter-response');

    var command_check_counter = document.getElementById('command-check-counter');
    var command_check_delay = document.getElementById('command-check-delay');
    var command_reset_counter = document.getElementById('command-reset-counter');
    var command_reset_delay = document.getElementById('command-reset-delay');
    var command_apply_counter = document.getElementById('command-apply-counter');
    var command_apply_delay = document.getElementById('command-apply-delay');

    if (fun_id == 'get_counter_config'){

        var counter_config = await eel.counter(fun_id,'none','none','none')();

        if (counter_config) {
            
            var list_redem = await eel.get_redeem('counter')();

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

            var counter_parse = JSON.parse(counter_config);

            counter_value.innerHTML = counter_parse.value_counter;

            command_applycounter_status.checked = counter_parse.counter_status_apply == 1 ? true : false;
            command_resetcounter_status.checked = counter_parse.counter_status_reset == 1 ? true : false;
            command_checkcounter_status.checked = counter_parse.counter_status_check == 1 ? true : false;
            response_status.checked = counter_parse.response == 1 ? true : false;

            response_counter.value = counter_parse.response_chat

            command_check_counter.value = counter_parse.counter_command_check;
            command_check_delay.value = counter_parse.counter_delay_check;
            command_reset_counter.value = counter_parse.counter_command_reset;
            command_reset_delay.value = counter_parse.counter_delay_reset;
            command_apply_counter.value = counter_parse.counter_command_set;
            command_apply_delay.value = counter_parse.counter_delay_set;
            
            

            $("#" + el_id).selectpicker('val',counter_parse.redeem)

        }

    } else if  (fun_id == 'save_counter_config') {

        var redeem_save = document.getElementById('redeem-select-counter').value;
        var response_status = document.getElementById('response-counter-status');

        response_status = response_status.checked ? 1 : 0

        data = {
            redeem : redeem_save,
            response : response_status,
            response_chat : response_counter.value
        }

        var formData = JSON.stringify(data);
        eel.counter(fun_id,formData,'none','none')

    } else if  (fun_id == 'save-counter-commands') {

        var form_commands = document.querySelector('#counter-config-commands-form')

        if (form_commands.querySelector('#command-checkcounter-status').checked == true) {
            counter_check_status = 1
        } else {
            counter_check_status = 0
        }

        if (form_commands.querySelector('#command-resetcounter-status').checked == true) {
            counter_reset_status = 1
        } else {
            counter_reset_status = 0
        }

        if (form_commands.querySelector('#command-applycounter-status').checked == true) {
            counter_apply_status = 1
        } else {
            counter_apply_status = 0
        }

        data  = {
            counter_command_check : form_commands.querySelector('#command-check-counter').value,
            counter_check_delay : form_commands.querySelector('#command-check-delay').value,
            counter_status_check : counter_check_status,
            counter_command_reset : form_commands.querySelector('#command-reset-counter').value,
            counter_reset_delay : form_commands.querySelector('#command-reset-delay').value,
            counter_status_reset : counter_reset_status,
            counter_command_apply : form_commands.querySelector('#command-apply-counter').value,
            counter_apply_delay : form_commands.querySelector('#command-apply-delay').value,
            counter_status_apply : counter_apply_status
            
        }

        var formData = JSON.stringify(data);

        eel.counter(fun_id,'none',formData,'none')

    } else if (fun_id == 'set-counter-value'){

        var form_counter_value = document.querySelector('#counter-set-value');
        var counter_value = form_counter_value.querySelector('#counter-value');


        eel.counter(fun_id,'none','none',counter_value.value)
        
        document.getElementById('counter-value-atual').innerHTML = counter_value.value
    }
    

}

eel.expose(update_counter_value);
function update_counter_value(value){
    var counter_value = document.getElementById('counter-value-atual');
    counter_value.innerHTML = value
}