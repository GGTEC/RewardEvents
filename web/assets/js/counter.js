async function counter_js(fun_id,event) {
    event.preventDefault();

    if (fun_id == 'get_counter_config'){

        var counter_config = await eel.counter('get_counter_redeem','none','none','none')();

        if (counter_config) {

            var counter_parse = JSON.parse(counter_config);
            
            document.getElementById('command-check-counter').value = counter_parse.counter_command_check
            document.getElementById('command-reset-counter').value = counter_parse.counter_command_reset
            document.getElementById('command-apply-counter').value = counter_parse.counter_command_set

            document.getElementById('counter-atual-redeem').innerHTML = counter_parse.redeem
            document.getElementById('counter-value-atual').innerHTML = counter_parse.value_counter

        }

    } else if  (fun_id == 'save_counter_config') {

        var form_config_counter = document.querySelector('#counter-config-form')
        var redeem_save = form_config_counter.elements[0].value;

        eel.counter('save_counter_redeem',redeem_save,'none','none')

    } else if  (fun_id == 'save-counter-commands') {

        var form_commands = document.querySelector('#counter-config-commands-form')


        data  = {
            counter_command_check : form_commands.querySelector('#command-check-counter').value,
            vcounter_command_reset : form_commands.querySelector('#command-reset-counter').value,
            counter_command_apply : form_commands.querySelector('#command-apply-counter').value,
        }

        eel.counter('save-counter-commands','none',data,'none')

    } else if (fun_id == 'set-counter-value'){

        var form_counter_value = document.querySelector('#counter-set-value');
        var counter_value = form_counter_value.querySelector('#counter-value');


        eel.counter('set-counter-value','none','none',counter_value.value)
        
        document.getElementById('counter-value-atual').innerHTML = counter_value.value
    }
    

}