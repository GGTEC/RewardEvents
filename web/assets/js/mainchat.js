window.addEventListener('pywebviewready', function() {

  start_update_time_chat()
    $("input, select, textarea").attr("autocomplete", "off");
    $("input, select, textarea").attr("spellcheck", "false");
    
  });


function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}