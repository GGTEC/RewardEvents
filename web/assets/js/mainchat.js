
$(document).ready(function () {

    $('.toast').toast({
      autohide: true,
      delay: 5000
    });
    $("input, select, textarea").attr("autocomplete", "off");
    $("input, select, textarea").attr("spellcheck", "false");
    $('select').selectpicker({
      liveSearch: true,
      showSubtext: true,
      size: 5,
      width: '100%',
      style: 'btn-dark',
      noneResultsText: "Nenhum resultado para {0}",
      liveSearchPlaceholder: "Pesquise o item",
      noneSelectedText : 'Selecione um item'
    });
  
  });