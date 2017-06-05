var but, deptDiv, preBut, preDiv;

var showDepts = function(){
  if (deptDiv.style.display == 'none'){
    deptDiv.style.display = 'block';
    but.innerHTML = 'Hide';
  }
  else{
    deptDiv.style.display = 'none';
    but.innerHTML = 'Show';
  }
}

var showPrereqs = function(){
  if (preDiv.style.display == 'none'){
    preDiv.style.display = 'block';
    preBut.innerHTML = 'Hide';
  }
  else{
    preDiv.style.display = 'none';
    preBut.innerHTML = 'Show';
  }
}

window.onload = function(){
  but = document.getElementById('showDepts');
  deptDiv = document.getElementById('theDepts');
  preBut = document.getElementById('prereqBut');
  preDiv = document.getElementById('prereqs');

  but.addEventListener('click',showDepts);
  deptDiv.style.display = 'none';

  preBut.addEventListener('click',showPrereqs);
  preDiv.style.display = 'none';
}
