var flip = 1; //variable that keeps track of if font has been enlarged

$(document).ready(function() {
  var resize = new Array("p", "html");
  resize = resize.join(",");

  $(".btnsize").click(function() {
    if (flip == 1) {
      $(resize).css("font-size", "200%");
      $("#zoom").attr("src", "../static/images/zoomout.png");
      flip = 0;
    } else {
      $(resize).css("font-size", "100%");
      $("#zoom").attr("src", "../static/images/zoomin.png");
      flip = 1;
    }
    return false;
  });
});
