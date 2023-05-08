
async function timer_js(event,type_id) {

    if (type_id == "get" ){

        document.getElementById("timer-add-form").reset();
        document.getElementById("timer-edit-form").reset();
        document.getElementById("timer-del-form").reset();
        document.getElementById("timer-delay-form").reset();
        
        $("#timer-select-edit").empty();
        $("#timer-select-del").empty();
    
        var timer_enable_check = document.getElementById("timer-enable");
    
        var timer_inp_delay_min = document.getElementById("timer-delay-min");
        var timer_inp_delay_max = document.getElementById("timer-delay-max");
    
        var list_messages = await window.pywebview.api.timer_py(type_id,'null');
    
        if (list_messages) {
            
            var list_messages_parse = JSON.parse(list_messages);
            var delay_min_info = list_messages_parse.delay_min;
            var delay_max_info = list_messages_parse.delay_max;
            
            timer_inp_delay_min.value = delay_min_info;
            timer_inp_delay_max.value = delay_max_info;
         
            if (list_messages_parse.status == 1){
                timer_enable_check.checked = true;
            }
        
            var data = list_messages_parse.messages;
            var $timerSelectEdit = $("#timer-select-edit");
            var $timerSelectDel = $("#timer-select-del");
        
            for (var key in data) {
                var value = data[key]['message'];
                var value_slice = value.slice(0,60);
                $timerSelectEdit.append('<option class="timer-wrap" style="background: #000; color: #fff;" value="'+ key +'">'+ value_slice +'</option>');
                $timerSelectDel.append('<option class="timer-wrap" style="background: #000; color: #fff;" value="'+ key +'">'+ value_slice +'</option>');
            }
        
            $timerSelectEdit.add($timerSelectDel).selectpicker("refresh");
        }


    } else if (type_id == "get_message") {

        var timer_select_edit_value = document.getElementById("timer-select-edit").value;
        var timer_edit_inp = document.getElementById("timer-edit-message");
        var timer_type = document.getElementById("message-type-edit");
    
        var message_edit_to = await window.pywebview.api.timer_py(type_id,timer_select_edit_value);
        
        if (message_edit_to){

            var message_parse = JSON.parse(message_edit_to);
        
            timer_edit_inp.value = message_parse.message;
    
            var type_message = message_parse.type_timer;
            var message_color = message_parse.color
    
            if (type_message == 1){
    
                var annonce_color = document.querySelector("#message-color-select-edit");
                annonce_color.style.display = "block";
                $("#message-color-select-edit").selectpicker('val', message_color)
                timer_type.checked = true
    
            } else {
                var annonce_color = document.querySelector("#message-color-select-edit");
                annonce_color.style.display = "none";
                timer_type.checked = false
            }

        }

    } else if (type_id == "edit"){
        event.preventDefault();

        $("#timer-ger-internal").hide();

        var timer_select_edit_value = document.getElementById("timer-select-edit").value;
        var timer_edit_new = document.getElementById("timer-edit-message").value;
    
        var timer_type = document.getElementById("message-type-edit");
        var timer_color = document.getElementById("message-color-edit").value;
    
        if (timer_type.checked == true){
            message_type = 1
        } else {
            message_type = 0
        }
    
        data = {
            key: timer_select_edit_value,
            message: timer_edit_new,
            type_timer : message_type,
            color: timer_color
        }
    
        var formData = JSON.stringify(data);
    
        window.pywebview.api.timer_py(type_id,formData);

        $("#timer-ger-internal").fadeIn(500);
        
    } else if (type_id == "add"){

        event.preventDefault();

        $("#timer-ger-internal").hide();
        $("#timer-loader").fadeIn();

        var form = document.querySelector("#timer-add-form");
        var new_timer_message = form.querySelector('#add-message-timer').value;
        var message_annouce = form.querySelector('#message-type');
        var message_color = form.querySelector('#message-color').value;
    
        if (message_annouce.checked == true){
            message_type = 1
        } else {
            message_type = 0
        }
    
        data = {
            message : new_timer_message,
            type_timer : message_type,
            color : message_color
        }
    
        var formData = JSON.stringify(data);
    
        window.pywebview.api.timer_py(type_id,formData);

        $("#timer-select-edit").empty();
        $("#timer-select-del").empty();
        
        var list_messages = await window.pywebview.api.timer_py('get','null');

        if (list_messages) {
    
            var list_messages_parse = JSON.parse(list_messages);
 
            data = list_messages_parse.messages;
    
            for (var key in data) {
                
                var value = data[key]['message'];
                var value_slice = value.slice(0,70)
    
                $("#timer-select-edit").append('<option class="timer-wrap" style="background: #000; color: #fff;" value="'+ key +'">'+ value_slice +'</option>');
                $("#timer-select-edit").selectpicker("refresh");
    
            }
    
            for (var key in data) {
    
                var value = data[key]['message'];
                var value_slice = value.slice(0,80)
        
                $("#timer-select-del").append('<option class="timer-wrap" style="background: #000; color: #fff;" value="'+ key +'">'+ value_slice +'</option>');
                $("#timer-select-del").selectpicker("refresh");
            }
    
            $("select").selectpicker("refresh");

            $("#timer-loader").hide();
            $("#timer-ger-internal").fadeIn(500);
            
        }

    } else if (type_id == "del"){
        event.preventDefault();

        $("#timer-ger-internal").hide();

        var timer_select_del_value = document.getElementById("timer-select-del").value;
    
        window.pywebview.api.timer_py(type_id,timer_select_del_value);

        $("#timer-select-edit").empty();
        $("#timer-select-del").empty();

        var list_messages_parse = await window.pywebview.api.timer_py('get','null');

        if (list_messages_parse) {
                
            data = list_messages_parse.messages;
    
            for (var key in data) {
                
                var value = data[key]['message'];
                var value_slice = value.slice(0,70)
    
                $("#timer-select-edit").append('<option class="timer-wrap" style="background: #000; color: #fff;" value="'+ key +'">'+ value_slice +'</option>');
                $("#timer-select-edit").selectpicker("refresh");
    
            }
    
            for (var key in data) {
    
                var value = data[key]['message'];
                var value_slice = value.slice(0,80)
        
                $("#timer-select-del").append('<option class="timer-wrap" style="background: #000; color: #fff;" value="'+ key +'">'+ value_slice +'</option>');
                $("#timer-select-del").selectpicker("refresh");
            }
    
            $("select").selectpicker("refresh");


        }

        $("#timer-ger-internal").fadeIn(500);


    } else if (type_id == "delay"){
        event.preventDefault();

        data = {
            min_time : document.getElementById("timer-delay-min").value,
            max_time : document.getElementById("timer-delay-max").value
        }
    
        var formData = JSON.stringify(data);
    
        window.pywebview.api.timer_py(type_id, formData);

    } else if (type_id == "status") {

        var check_seletor = document.getElementById('timer-enable');

        if (check_seletor.checked == true){
            window.pywebview.api.timer_py(type_id,1)
        } else if (check_seletor.checked == false) {
            window.pywebview.api.timer_py(type_id,0)
        }

    } else if (type_id == "hide") {

        var timer_edit_inp = document.getElementById("timer-edit-message");
        var timer_type = document.getElementById("message-type-edit");
        var annonce_color = document.querySelector("#message-color-select-edit");
        timer_edit_inp.value = "";
        timer_type.checked = false;
        annonce_color.style.display = "none";

    } else if (type_id == "ann_create"){

        var check_type = document.querySelector("#message-type");
        var annonce_color = document.querySelector("#message-color-select");
    
        if (check_type.checked == true) {
            annonce_color.style.display = "block";
        } else {
            annonce_color.style.display = "none";
        }

    } else if (type_id == "ann_edit"){

        var check_type = document.querySelector("#message-type-edit");
        var annonce_color = document.querySelector("#message-color-select-edit");
    
        if (check_type.checked == true) {
            annonce_color.style.display = "block";
        } else {
            annonce_color.style.display = "none";
        }

    }
}