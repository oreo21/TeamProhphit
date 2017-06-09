var click;

var secretPath = function(){
  if (click == 5){
    $.ajax({
      url: '/redirectToSuperman/',
      type: 'POST',
      data: {'click':true},
      success: function(data){
        if (data == 'yes'){
          window.location = "/superman/";
        }
      }
    });
  }
  else{
    click++;
  }
}

window.onload = function(){
  click = 0;
  document.getElementById('secret').addEventListener('click',secretPath);
}
