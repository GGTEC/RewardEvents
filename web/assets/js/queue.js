async function queue_js(type_id){
    
    if (type_id == "get"){

        var response_status = document.getElementById('response-queue-status');
        var response_queue = document.getElementById('queue-response');
        var response_add_queue = document.getElementById('queue-add-response');

        var queue_parse = await window.pywebview.api.queue(type_id,'none');

        if (queue_parse) {
            
            var list_redem_parse = await window.pywebview.api.get_redeem('queue');

            if (list_redem_parse) {

                var el_id = "redeem-select-queue";

                $("#" + el_id).empty();

                $("#" + el_id).append('<option class="bg-dark" style="color: #fff;" value="None">Sem recompensa</option>');
                $("#" + el_id).selectpicker("refresh");

                for (var i = 0; i < list_redem_parse.redeem.length; i++) {
                    var optn = list_redem_parse.redeem[i];

                    $("#" + el_id).append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
                    $("#" + el_id).selectpicker("refresh");
                }
            }
        

        response_status.checked = queue_parse.response == 1 ? true : false;

        response_queue.value = queue_parse.response_chat
        response_add_queue.value = queue_parse.response_add_chat

        $("#" + el_id).selectpicker('val',queue_parse.redeem)

        var queue_list = queue_parse.queue

        var dataTableData = [];

        for (var key in queue_list) {
            if (queue_list.hasOwnProperty(key)) {
              var queueItem = queue_list[key];
              dataTableData.push([
                queueItem,
              ]);
            }
        }

        if ($.fn.DataTable.isDataTable("#queuelist_table")) {

            $('#queuelist_table').DataTable().clear().draw();
            $('#queuelist_table').DataTable().destroy();
        }

        var table = $('#queuelist_table').DataTable( {
            destroy: true,
            scrollX: true,
            paging: false,
            ordering:  false,
            retrieve : false,
            processing: true,
            responsive: false,
            language: {
                url: 'https://cdn.datatables.net/plug-ins/1.13.1/i18n/pt-BR.json'
            },
            columns: [
                { title: 'Usuário' },
            ]
        } );

        // adicionar as linhas à tabela
        for (var i = 0; i < dataTableData.length; i++) {
            table.row.add(dataTableData[i]).draw();
        }

    }

    } else if (type_id == "save_config"){

        var redeem_save = document.getElementById('redeem-select-queue').value;
        var response_status = document.getElementById('response-queue-status');
        var response_queue = document.getElementById('queue-response');
        var response_add_queue = document.getElementById('queue-add-response');

        response_status = response_status.checked ? 1 : 0

        data = {
            redeem : redeem_save,
            response : response_status,
            response_chat : response_queue.value,
            response_add_chat : response_add_queue.value
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.queue(type_id,formData)

    } else if (type_id == "queue_add"){

        var add_queue = document.getElementById('add_queue').value;

        var queue_list = await window.pywebview.api.queue(type_id,add_queue);

        if (queue_list) {
            
        var dataTableData = [];

        for (var key in queue_list) {
            if (queue_list.hasOwnProperty(key)) {
              var queueItem = queue_list[key];
              dataTableData.push([
                queueItem,
              ]);
            }
        }

        if ($.fn.DataTable.isDataTable("#queuelist_table")) {
            $('#queuelist_table').DataTable().clear().draw();
            $('#queuelist_table').DataTable().destroy();
        }

        var table = $('#queuelist_table').DataTable( {
            destroy: true,
            scrollX: true,
            paging: false,
            ordering:  false,
            retrieve : false,
            processing: true,
            responsive: false,
            language: {
                url: 'https://cdn.datatables.net/plug-ins/1.13.1/i18n/pt-BR.json'
            },
            columns: [
                { title: 'Usuário' },
            ]
        } );

        // adicionar as linhas à tabela
        for (var i = 0; i < dataTableData.length; i++) {
            table.row.add(dataTableData[i]).draw();
        }

    }

    } else if (type_id == "queue_rem"){

        var add_queue = document.getElementById('add_queue').value;

        var queue_list = await window.pywebview.api.queue(type_id,add_queue);

        if (queue_list) {
            

        var dataTableData = [];

        for (var key in queue_list) {
            if (queue_list.hasOwnProperty(key)) {
              var queueItem = queue_list[key];
              dataTableData.push([
                queueItem,
              ]);
            }
        }

        if ($.fn.DataTable.isDataTable("#queuelist_table")) {
            $('#queuelist_table').DataTable().clear().draw();
            $('#queuelist_table').DataTable().destroy();
        }

        var table = $('#queuelist_table').DataTable( {
            destroy: true,
            scrollX: true,
            paging: false,
            ordering:  false,
            retrieve : false,
            processing: true,
            responsive: false,
            language: {
                url: 'https://cdn.datatables.net/plug-ins/1.13.1/i18n/pt-BR.json'
            },
            columns: [
                { title: 'Usuário' },
            ]
        } );

        // adicionar as linhas à tabela
        for (var i = 0; i < dataTableData.length; i++) {
            table.row.add(dataTableData[i]).draw();
        }

    }

    } else if (type_id == 'get_commands') {

        var command_queue_select = document.getElementById('command-queue-select');

        var command_queue_status = document.getElementById('command-queue-status');
        var command_queue_command = document.getElementById('command-queue-command');
        var command_queue_delay = document.getElementById('command-queue-delay');
        var command_queue_perm = document.getElementById('command-queue-perm');

        var queue_command_edit = document.getElementById('command_queue_form');

        var queue_parse = await window.pywebview.api.queue(type_id,command_queue_select.value);

        if (queue_parse){

            queue_command_edit.hidden = false

            command_queue_status.checked = queue_parse.status == 1 ? true : false;
            command_queue_command.value = queue_parse.command
            command_queue_delay.value = queue_parse.delay

            $("#command-queue-perm").selectpicker('val',queue_parse.user_level)

        }

    } else if (type_id == 'save_commands') {

        var command_queue_select = document.getElementById('command-queue-select');

        var command_queue_status = document.getElementById('command-queue-status');
        var command_queue_command = document.getElementById('command-queue-command');
        var command_queue_delay = document.getElementById('command-queue-delay');
        var command_queue_perm = document.getElementById('command-queue-perm');

        var command_status = command_queue_status.checked ? 1 : 0;

        data  = {
            type_command: command_queue_select.value,
            command: command_queue_command.value,
            status: command_status,
            delay: command_queue_delay.value,
            user_level: command_queue_perm.value
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.queue(type_id,formData)

    }
}