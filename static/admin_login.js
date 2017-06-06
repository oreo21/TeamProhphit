var click;

var secretPath = function(){
  if (click == 5){
    window.location = "/superman/";
  }
  else{
    click++;
  }
}

window.onload = function(){
  click = 0;
  document.getElementById('secret').addEventListener('click',secretPath);
}
