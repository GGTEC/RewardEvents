
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

$(window).on("load",async function(){

    var disclosure = await eel.load_disclosure()();
    if (disclosure){
        document.getElementById('message-disclosure-send').value = disclosure
    }

    while (true){

        data_receive = await eel.get_spec()();

            if (data_receive){

                var spec_data = JSON.parse(data_receive);

                document.getElementById('text-counter').innerText = " " + spec_data.specs;
                document.getElementById('time-in-live').innerText = spec_data.time;
                document.getElementById('follow_name_text').innerHTML = spec_data.follow;
                document.getElementById('last_timer_text').innerHTML = spec_data.last_timer;

                if (spec_data.specs != 'Offline'){

                    document.getElementById('live-dot').style.color = 'red';
                    
                }
                
            }
        await sleep(600000)
    }

});


eel.profile_info()(async function(data_auth){

    const data_profile = JSON.parse(data_auth);

    var profile_image = document.getElementById("profile_image");
    var profile_image_new = profile_image.src;
    profile_image.src = profile_image_new; 

    document.getElementById('email').innerText = data_profile.email;;
    document.getElementById('user_id').innerText = data_profile.user_id;
    document.getElementById('ex_name').innerText = data_profile.display_name;
    document.getElementById('login_name').innerText = data_profile.login_name;
    
})


eel.expose(update_div_redeem);
function update_div_redeem(data_redeem) {

    var data_redem_parse = JSON.parse(data_redeem);

    var image_redeem = document.getElementById("image_redeem");
    var name_redeem = document.getElementById("name_redeem");
    var user_redeem = document.getElementById("user_redeem");

    var image_redeem_new = image_redeem.src;
    image_redeem.src = image_redeem_new; 

    name_redeem.innerText = data_redem_parse.redeem_name
    user_redeem.innerText = data_redem_parse.redeem_user
}

function pass_message(message_to){
    message_ret = message_to.replace("\x01ACTION", "<i>");
    message_ret = message_ret.replace("\x01", "<i>");
    return message_ret
}

eel.expose(append_message);
function append_message(message_data){

    var div_chat = document.getElementById('chat-block');
    var message_data_parse = JSON.parse(message_data);
    var type_message = message_data_parse.type

    if (type_message == 'PRIVMSG'){
    
        var message_rec = pass_message(message_data_parse.message)
        var user_rec = message_data_parse.display_name
        var mod_rec = message_data_parse.mod
        var sub_rec = message_data_parse.subscriber
        var color_rec = message_data_parse.color

        console.log(sub_rec)
        if (color_rec == ""){
            var color_rec = "#000000".replace(/0/g,function(){return (~~(Math.random()*16)).toString(16);});
        }

        if (mod_rec == 1){
            sword = '<i class="fa-solid fa-user-shield" id="usershield"></i>'
        } else {
            sword = ''
        }
        if (sub_rec == 1){
            star = '<i class="fa-solid fa-star" id="userstar"></i>'
        } else {
            star = ''
        }

        
        var message_div = star + sword + '<span id="user-chat" style=color:'+ color_rec +';>'+ user_rec +' </span><span id="message-chat"> : '+ message_rec +'</span>';
        var div = document.createElement("div");
        div.innerHTML = message_div;
        div.id = 'chat-message-block'

        div_chat.appendChild(div);
        div_chat.scrollTop = div_chat.scrollHeight;

    } else if (type_message == 'CONN'){

        toast_notifc('Bot desconectado, conectando ao chat...')

    } else if (type_message == 'CONNSUCESS'){

        toast_notifc('Bot conectado!')

    }

}


