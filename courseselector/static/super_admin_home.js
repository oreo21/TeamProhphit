var error, passError;

var validation = function(){
  $.ajax({
    url: '/adddeptadmin/',
    type: 'POST',
    data: {'email1':document.getElementById('email1').value, 'email2':document.getElementById('email2').value},
    success: function(data){
      if (data){
        error.style.display = 'block';
        error.innerHTML = data;
      }
      else{
        window.location = '/';
      }
    }
  });
}

var passValidation = function(){
  $.ajax({
    url: '/changePass/',
    type: 'POST',
    data: {'pass':document.getElementById('pass1').value, 'pass2':document.getElementById('pass2').value},
    success: function(data){
      if (data){
        passError.style.display = 'block';
        passError.innerHTML = data;
      }
      else{
        window.location = '/';
      }
    }
  });
}

window.onload = function(){
  error = document.getElementById('error');
  error.style.display = 'none';

  passError = document.getElementById('passError');
  passError.style.display = 'none';

  document.getElementById('butt').addEventListener('click',validation);
  document.getElementById('passBut').addEventListener('click',passValidation);
}
