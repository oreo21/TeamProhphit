var error

window.onload = function(){

  error = document.getElementById('error');
  error.style.display = 'none';

  document.getElementById('but').addEventListener('click',validation);
}

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