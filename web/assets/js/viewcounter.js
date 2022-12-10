
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



