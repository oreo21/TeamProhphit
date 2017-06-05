//--------uploading jscript--------
var error, courseUpload, courseForm, transcriptForm, fd;

window.onload = function(){

  error = document.getElementById('error');
  error.style.display = 'none';

  courseUpload = document.getElementById('course-upload');

  document.getElementById('but').addEventListener('click',validation);
  courseUpload.addEventListener('click',validateCourses);
  document.getElementById('student-upload').addEventListener('click',validateTranscript);
}

var validation = function(){
  $.ajax({
      url: '/checkMatch/',
      type: 'POST',
      data: {'email1':document.getElementById('email1').value, 'email2':document.getElementById('email2').value,'pass1':document.getElementById('pass1').value,'pass2':document.getElementById('pass2').value},
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

var validateCourses = function(){
  if (document.getElementById('course-file').value != ""){
    courseForm = document.getElementById('course-form');
    fd = new FormData(courseForm);
    $.ajax({
        url: '/validateCSV/',
        type: 'POST',
        data: fd,
        contentType: false,
        processData: false,
        success: function(data){
          console.log(data);
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
  else{
    error.style.display = 'block';
    error.innerHTML = "No file uploaded."
  }
}

var validateTranscript = function(){
  if (document.getElementById('transcript-file').value != ""){
    transcriptForm = document.getElementById('transcript-form');
    //console.log(courseForm);
    fd = new FormData(transcriptForm);
    //console.log(fd.entries());
    //console.log(formdata);
    $.ajax({
        url: '/validateTranscript/',
        type: 'POST',
        data: fd,
        contentType: false,
        processData: false,
        success: function(data){
          console.log(data);
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
  else{
    error.style.display = 'block';
    error.innerHTML = "No file uploaded."
  }
}

//-------- removing courses/cohorts jscript --------

  var course_button = document.getElementById('course_button');
  var cohort_button = document.getElementById('cohort_button');

  var course = document.getElementById('course');
  var cohort = document.getElementById('cohort');

  var course_shown = false;
  var cohort_shown = false;

  course.style.display = 'none';
  cohort.style.display = 'none';

  var display_course = function(){
    if (course_shown){
      course.style.display = 'none';
      course_shown = false;
    }

    else{
      course.style.display = 'block';
      course_shown = true;
    }
  }

  var display_cohort = function(){
    if (cohort_shown){
      cohort.style.display = 'none';
      cohort_shown = false;
    }

    else{
      cohort.style.display = 'block';
      cohort_shown = true;
    }
  }

  course_button.addEventListener('click',display_course);
  cohort_button.addEventListener('click',display_cohort);
