var but = document.getElementById('but');
var options= document.getElementById('options');
var del = document.getElementById('del');

options.style.display= 'none';
var vis = false;

var click = function(){
  if (vis){
    vis = false;
    options.style.display = 'none';
    but.innerHTML = 'show';
  }
  else{
    vis = true;
    options.style.display = 'block';
    but.innerHTML = 'hide';
  }
}

but.addEventListener('click',click);
