var but, deptDiv, preBut, preDiv, deptButs;

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

var showClasses = function(event){
  var name = event.target.id + "div";
  if (document.getElementById(name).style.display == 'none'){
    document.getElementById(name).style.display = 'block';
  }
  else{
    document.getElementById(name).style.display = 'none';
  }
}

window.onload = function(){
  but = document.getElementById('showDepts');
  deptDiv = document.getElementById('theDepts');
  preBut = document.getElementById('prereqBut');
  preDiv = document.getElementById('prereqs');
  deptBut = document.getElementsByClassName('dept');

  but.addEventListener('click',showDepts);
  deptDiv.style.display = 'none';

  preBut.addEventListener('click',showPrereqs);
  preDiv.style.display = 'none';

  for (var j = 0; j < deptBut.length; j++){
    deptBut[j].addEventListener('click',showClasses);
    name = deptBut[j].id + "div";
    document.getElementById(name).style.display = 'none';
  }
}
