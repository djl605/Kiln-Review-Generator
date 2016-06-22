-// client-side js
// run by the browser each time your view template is loaded

// protip: you can rename this to use .coffee if you prefer

// by default, you've got jQuery,
// add other scripts at the bottom of index.html

$(function() {
  console.log('hello world :o');
  

  $('form#register').submit(function(event) {
  event.preventDefault();
    if ($('input[name=password]').val() !== $('input[name=repeat]').val()) {
      $('h3#match').attr('hidden', false);
    } else {
      $('h3#match').attr('hidden', true);
      $.post('/register', $('form#register').serialize())
        .fail(function(jqXHR, textStatus, error) {
          if (jqXHR.status === 403) {
            if (jqXHR.responseJSON.error === "Bad Token") {
              $('h3#bad_token').attr('hidden', false);
            }
            else if (jqXHR.responseJSON.error === "Account Already Exists") {
              $('h3#already_exists').attr('hidden', false);
            }
          }
        })
        .done(function() {
          window.location.href = "registration_successful";
        });
    }
  });

  
  $('form#login').submit(function(event) {
    event.preventDefault();
    $.post('/login', $('form#login').serialize())
      .fail(function(e) {
        if (e.status === 401) {
          $('h3#incorrect_pw').attr('hidden', false);
          $('input[name=password]').val('');
        }
      })
      .done(function(data) {
        createCookie('hyper-token', data, 1);
        window.location.href = "myhome";
      });
  });

});
