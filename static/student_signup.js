var ap = document.getElementsByClassName('ap');

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

window.onload = function(){
  for (var i = 0; i < ap.length; i++){
    ap[i].addEventListener("change",clicked);
  };
};
