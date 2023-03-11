
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

$(window).on("load",async function(){

    var disclosure = await eel.disclosure_py('get','null')();
    if (disclosure){
        document.getElementById('message-disclosure-send').value = disclosure
    }

});

eel.expose(receive_live_info)
function receive_live_info(data){

    const spec_data = JSON.parse(data);

    document.getElementById('text-counter').innerText = " " + spec_data.specs;
    document.getElementById('time-in-live').innerText = spec_data.time;

    if (spec_data.specs != 'Offline'){
        document.getElementById('live-dot').style.color = 'red';
    }
}

eel.expose(receive_follow_info)
function  receive_follow_info(data){

    const follow_data = JSON.parse(data);
    document.getElementById('follow_name_text').innerHTML = follow_data.follow;

}

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





