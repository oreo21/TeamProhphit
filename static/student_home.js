var ap, selected, options,but1;

var clicked = function(event){

  //go through all ap options
  for (var i = 0; i < ap.length; i++){
    //if not the one you just clicked
    if (ap[i] != event.target){

      //find the matching AP and remove it (can't pick twice)
      for (var j = 0; j < ap[i].options.length; j++){
        if (ap[i].options[j].value == event.target.value){
          ap[i].remove(ap[i].options[j]);
          //only one will match
          break;
        }
      }

      //if old exists (we need to add it back in as an option)
      if(event.target.old){
        var opt = document.createElement("option");
        opt.text = event.target.old;
        ap[i].add(opt);
      }

    }
  }
  event.target.old = event.target.value;
}

var viewSelected = function(){
  //if viewing what you selected (not your options)
  if (options.style.display == 'none'){
    options.style.display = 'block';
    selected.style.display = 'none';
  }
  else{
    options.style.display = 'none';
    selected.style.display = 'block';
  }
}

window.onload = function(){
  ap = document.getElementsByClassName('ap');
  selected = document.getElementById('selected');
  options = document.getElementById('options');
  but1 = document.getElementById('but1');
  but2 = document.getElementById('but2');

  options.style.display = 'none';

  for (var i = 0; i < ap.length; i++){
    ap[i].addEventListener("change",clicked);
  };
  but1.addEventListener('click',viewSelected);
  but2.addEventListener('click',viewSelected);
};
