
eel.expose(modal_actions);
function modal_actions(modal_id) {
    $("#" + modal_id).modal("show");
}

async function getFolder() {
    var dosya_path = await eel.select_file_py()();
    if (dosya_path) {
        document.getElementById("file-select").value = dosya_path;
    }
}

function removeOptions(selectElement) {
    $("#" + selectElement).empty();

    var select = document.getElementById(selectElement);
    var el = document.createElement("option");

    el.textContent = "Selecione";
    el.attr = "selected";

    select.appendChild(el);
}

async function get_redeem_del_js(el_id, btn_id) {

    var btn_el = document.getElementById(btn_id);
    var list_redem = await eel.get_redeem_created()();

    if (list_redem) {
        btn_el.removeAttribute("disabled");
        $("#" + el_id).empty();

        var list_redem_parse = JSON.parse(list_redem);

        for (var i = 0; i < list_redem_parse.redeem.length; i++) {
            var optn = list_redem_parse.redeem[i];

            $("#" + el_id).append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
            $("#" + el_id).selectpicker("refresh");
        }
    }
}

async function get_redeem_js(el_id, btn_id) {

    var btn_el = document.getElementById(btn_id);
    var list_redem = await eel.get_redeem()();

    if (list_redem) {
        
        btn_el.removeAttribute("disabled");
        $("#" + el_id).empty();

        var list_redem_parse = JSON.parse(list_redem);

        for (var i = 0; i < list_redem_parse.redeem.length; i++) {
            var optn = list_redem_parse.redeem[i];

            $("#" + el_id).append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
            $("#" + el_id).selectpicker("refresh");
        }
    }
    $("#" + el_id + " option[value='Carregando']").remove();
}

function show_div(div_id, select_redeem, btn_id) {
    get_redeem_js(select_redeem, btn_id);
    document.getElementById("create-redeem").hidden = true;
    document.getElementById(div_id).hidden = false;
}

function show_div_del(div_id, select_redeem, btn_id) {
    get_redeem_del_js(select_redeem, btn_id);
    document.getElementById("create-redeem").hidden = true;
    document.getElementById(div_id).hidden = false;
}

function hide_create(div_id_hide, select_redeem, form, btn_id) {
    
    var btn_submit_el = document.getElementById(btn_id);
    btn_submit_el.setAttribute("disabled", "");

    removeOptions(select_redeem);
    $("#sucess-" + form).modal("hide");
    document.getElementById(form).reset();
    document.getElementById("create-redeem").hidden = false;
    document.getElementById(div_id_hide).hidden = true;
}

function get_key_mode() {
    var mode_selected = document.getElementById("key-mode-select").value;
    var buttom_keypress = document.getElementById("submit-keypress");
    var re_press_time_input = document.getElementById("re-press-time");
    var keep_press_time_input = document.getElementById("keep-press-time");
    var mult_press_time_input = document.getElementById("mult-press-times");
    var mult_press_interval_input = document.getElementById("mult-press-interval");

    if (mode_selected === "keep") {

        buttom_keypress.removeAttribute("disabled");

        keep_press_time_input.setAttribute("required", "");

        re_press_time_input.removeAttribute("required");
        mult_press_time_input.removeAttribute("required");
        mult_press_interval_input.removeAttribute("required");

        document.getElementById("re-press-div").hidden = true;
        document.getElementById("mult-press-div").hidden = true;
        document.getElementById("keep-press-div").hidden = false;

    } else if (mode_selected === "mult") {

        buttom_keypress.removeAttribute("disabled");

        keep_press_time_input.removeAttribute("required");
        re_press_time_input.removeAttribute("required");

        mult_press_time_input.setAttribute("required", "");
        mult_press_interval_input.setAttribute("required", "");

        document.getElementById("re-press-div").hidden = true;
        document.getElementById("mult-press-div").hidden = false;
        document.getElementById("keep-press-div").hidden = true;

    } else if (mode_selected === "re") {

        buttom_keypress.removeAttribute("disabled");

        re_press_time_input.setAttribute("required", "");

        keep_press_time_input.removeAttribute("required");
        mult_press_time_input.removeAttribute("required");
        mult_press_interval_input.removeAttribute("required");

        document.getElementById("re-press-div").hidden = false;
        document.getElementById("mult-press-div").hidden = true;
        document.getElementById("keep-press-div").hidden = true;

    } else if (mode_selected === "none") {
        buttom_keypress.setAttribute("disabled", "");

        document.getElementById("re-press-div").hidden = true;
        document.getElementById("mult-press-div").hidden = true;
        document.getElementById("keep-press-div").hidden = true;
    }
}

function create_audio_js(event) {
    event.preventDefault();

    var form = document.querySelector("#audio-create");
    var mod_value = form.querySelector('input[id="mod-switch-audio"]').checked;

    if (mod_value == true) {
        mod_value = 'mod';
    } else {
        mod_value = '';
    }

    data = {
        redeem_value: form.querySelector('select[id="redeem-select-audio"]').value,
        command_value: form.querySelector('input[id="command-text"]').value,
        chat_response: form.querySelector('input[id="chat-message"]').value,
        audio_path: form.querySelector('input[id="file-select"]').value,
        user_level_value: mod_value,
    };

    var formData = JSON.stringify(data);

    eel.create_audio(formData);
}

function create_tts_js(event) {
    event.preventDefault();

    var form = document.querySelector("#tts-create");
    var mod_value = form.querySelector('input[id="mod-switch-tts"]').checked;

    if (mod_value == true) {
        mod_value = 'mod';
    } else {
        mod_value = '';
    }

    data = {
        redeem_value: form.querySelector('select[id="redeem-select-tts"]').value,
        command_value: form.querySelector('input[id="command-text"]').value,
        chat_response: form.querySelector('input[id="chat-message"]').value,
        caracters: form.querySelector('input[id="caracters"]').value,
        user_level_value: mod_value,
    };

    var formData = JSON.stringify(data);

    eel.create_tts(formData);
}

function create_scene_js(event) {
    event.preventDefault();
    var form = document.querySelector("#scene-create");
    var mod_value = form.querySelector('input[id="mod-switch-scene"]').checked;
    var keep_scene = form.querySelector('input[id="keep-switch-scene"]').checked;

    if (mod_value == true) {
        mod_value = 'mod';
    } else {
        mod_value = '';
    }

    if (keep_scene == true) {
        keep_scene = 1;
    } else {
        keep_scene = 0;
    }

    data = {
        redeem_value: form.querySelector('select[id="redeem-select-scene"]').value,
        command_value: form.querySelector('input[id="command-text"]').value,
        chat_response: form.querySelector('input[id="chat-message"]').value,
        user_level_value: mod_value,
        scene_name: form.querySelector('select[id="scene_name"]').value,
        time: form.querySelector('input[id="time-to-return-scene"]').value,
        keep_scene_value: keep_scene,
    };

    var formData = JSON.stringify(data);

    eel.create_scene(formData);
}

function create_response_js(event) {
    event.preventDefault();
    var form = document.querySelector("#response-create");
    var mod_value = form.querySelector('input[id="mod-switch-response"]').checked;

    if (mod_value == true) {
        mod_value = 'mod';
    } else {
        mod_value = '';
    }

    data = {
        redeem_value: form.querySelector('select[id="redeem-select-response"]')
            .value,
        command_value: form.querySelector('input[id="command-text"]').value,
        chat_response: form.querySelector('input[id="chat-message"]').value,
        user_level_value: mod_value,
    };

    var formData = JSON.stringify(data);

    eel.create_response(formData);
}

function create_filter_js(event) {
    event.preventDefault();

    var form = document.querySelector("#filter-create");
    var mod_value = form.querySelector('input[id="mod-switch-filter"]').checked;
    var keep_filter = form.querySelector(
        'input[id="keep-filter-switch"]'
    ).checked;

    if (mod_value == true) {
        mod_value = 'mod';
    } else {
        mod_value = '';
    }

    if (keep_filter == true) {
        keep_filter = 1;
    } else {
        keep_filter = 0;
    }

    data = {
        redeem_value: form.querySelector('select[id="redeem-select-filter"]').value,
        command_value: form.querySelector('input[id="command-text"]').value,
        chat_response: form.querySelector('input[id="chat-message"]').value,
        user_level_value: mod_value,
        source_name: form.querySelector('select[id="source_name_filter"]').value,
        filter_name: form.querySelector('select[id="filter_name"]').value,
        time_showing: form.querySelector('input[id="time-filter-create"]').value,
        keep: keep_filter,
    };

    var formData = JSON.stringify(data);

    eel.create_filter(formData);
}

function create_source_js(event) {
    event.preventDefault();

    var form = document.querySelector("#source-create");
    var mod_value = form.querySelector('input[id="mod-switch-source"]').checked;
    var keep_source = form.querySelector('input[id="keep-source"]').checked;

    if (mod_value == true) {
        mod_value = 'mod';
    } else {
        mod_value = '';
    }

    if (keep_source == true) {
        keep_source = 1;
    } else {
        keep_source = 0;
    }

    data = {
        redeem_value: form.querySelector('select[id="redeem-select-source"]').value,
        command_value: form.querySelector('input[id="command-text"]').value,
        chat_response: form.querySelector('input[id="chat-message"]').value,
        user_level_value: mod_value,
        source_name: form.querySelector('select[id="source_name_source"]').value,
        time_showing: form.querySelector('input[id="time_showing-source"]').value,
        keep: keep_source,
    };

    var formData = JSON.stringify(data);

    eel.create_source(formData);
}

function create_keypress_js(event) {
    event.preventDefault();

    var form = document.querySelector("#keypress-create");
    var mode = form.querySelector('select[id="key-mode-select"]').value;
    var mod_value = form.querySelector('input[id="mod-switch-keypress"]').checked;

    if (mod_value == true) {
        mod_value = 'mod';
    } else {
        mod_value = '';
    }

    if (mode == "mult") {
        data = {
            redeem_value: form.querySelector('select[id="redeem-select-keypress"]')
                .value,
            command_value: form.querySelector('input[id="command-text"]').value,
            chat_response: form.querySelector('input[id="chat-message"]').value,
            user_level_value: mod_value,

            mode: form.querySelector('select[id="key-mode-select"]').value,

            mult_press_times: form.querySelector('input[id="mult-press-times"]')
                .value,
            mult_press_interval: form.querySelector('input[id="mult-press-interval"]')
                .value,

            key1: form.querySelector('select[id="key-1"]').value,
            key2: form.querySelector('select[id="key-2"]').value,
            key3: form.querySelector('select[id="key-3"]').value,
            key4: form.querySelector('select[id="key-4"]').value,
        };
    } else if (mode == "re") {
        data = {
            redeem_value: form.querySelector('select[id="redeem-select-keypress"]')
                .value,
            command_value: form.querySelector('input[id="command-text"]').value,
            chat_response: form.querySelector('input[id="chat-message"]').value,
            user_level_value: mod_value,
            mode: form.querySelector('select[id="key-mode-select"]').value,

            re_press_time: form.querySelector('input[id="re-press-time"]').value,

            key1: form.querySelector('select[id="key-1"]').value,
            key2: form.querySelector('select[id="key-2"]').value,
            key3: form.querySelector('select[id="key-3"]').value,
            key4: form.querySelector('select[id="key-4"]').value,
        };
    } else if (mode == "keep") {
        data = {
            redeem_value: form.querySelector('select[id="redeem-select-keypress"]')
                .value,
            command_value: form.querySelector('input[id="command-text"]').value,
            chat_response: form.querySelector('input[id="chat-message"]').value,
            user_level_value: mod_value,
            mode: form.querySelector('select[id="key-mode-select"]').value,

            keep_press_time: form.querySelector('input[id="keep-press-time"]').value,

            key1: form.querySelector('select[id="key-1"]').value,
            key2: form.querySelector('select[id="key-2"]').value,
            key3: form.querySelector('select[id="key-3"]').value,
            key4: form.querySelector('select[id="key-4"]').value,
        };
    }

    var formData = JSON.stringify(data);

    eel.create_keypress(formData);
}

function create_counter_js(event) {
    event.preventDefault();
    var form = document.querySelector("#counter-create");
    var mod_value = form.querySelector('input[id="mod-switch-counter"]').checked;

    if (mod_value == true) {
        mod_value = 'mod';
    } else {
        mod_value = '';
    }

    data = {
        redeem_value: form.querySelector('select[id="redeem-select-counter"]')
            .value,
        command_value: form.querySelector('input[id="command-text"]').value,
        chat_response: form.querySelector('input[id="chat-message"]').value,
        user_level_value: mod_value,
    };

    var formData = JSON.stringify(data);

    eel.create_counter(formData);
}

function create_clip_js(event) {
    event.preventDefault();
    var form = document.querySelector("#clip-create");
    var mod_value = form.querySelector('input[id="mod-switch-clip"]').checked;

    if (mod_value == true) {
        mod_value = 'mod';
    } else {
        mod_value = '';
    }

    data = {
        redeem_value: form.querySelector('select[id="redeem-select-clip"]').value,
        command_value: form.querySelector('input[id="command-text"]').value,
        user_level_value: mod_value,
    };

    var formData = JSON.stringify(data);

    eel.create_clip(formData);
}

function del_action(event) {
    
    event.preventDefault();
    var selec_del = document.getElementById("action-del-select").value;
    eel.del_action_py(selec_del);
    removeOptions("action-del-select");
    get_redeem_del_js("action-del-select", "submit-del");
}

async function get_scenes(id) {

    $("#" + id).empty();

    var list_scenes = await eel.update_scene_obs()();

    if (list_scenes) {
        var list_scenes_parse = JSON.parse(list_scenes);

        for (var i = 0; i < list_scenes_parse.scenes.length; i++) {
            var optn = list_scenes_parse.scenes[i];

            $("#" + id).append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
            $("#" + id).selectpicker("refresh");
        }
    }
}

async function get_sources(select_id) {

    $("#" + select_id).empty();

    var list_sources = await eel.get_sources_obs()();

    if (list_sources) {
        var list_sources_parse = JSON.parse(list_sources);

        for (var i = 0; i < list_sources_parse.source.length; i++) {
            var optn = list_sources_parse.source[i];

            $("#" + select_id).append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
            $("#" + select_id).selectpicker("refresh");
        }
    }
}

async function get_filters(id,id_sources) {

    var selected_sources_id = document.getElementById(id_sources);
    var value = selected_sources_id.value;

    $("#" + id).empty();

    var list_filters = await eel.get_filters_obs(value)();

    if (list_filters) {

        var list_filters_parse = JSON.parse(list_filters);

        for (var i = 0; i < list_filters_parse.filters.length; i++) {
            var optn = list_filters_parse.filters[i];

            $("#" + id).append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
            $("#" + id).selectpicker("refresh");
        }
    }
}

