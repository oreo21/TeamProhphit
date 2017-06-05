var but;
var deptDiv;

var showDepts = function(){
  if (deptDiv.style.display == 'none'){
    deptDiv.style.display = 'block';
  }
  else{
    deptDiv.style.display = 'none';
  }
}

window.onload = function(){
  but = document.getElementById('showDepts');
  deptDiv = document.getElementById('theDepts');
  but.addEventListener('click',showDepts);
  deptDiv.style.display = 'none';
}
