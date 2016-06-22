$(function() {

  var hyperToken = readCookie('hyper-token');

  $.get('/users', function(data) {
    data.users.forEach(function(user) {
      $('<tr><td>' + user.username + '</td><td>' + user.ixUser + '</td></tr>').appendTo('table#users');
    });
  });
  
  $('button#log_out').click(function() {
    eraseCookie('hyper-token');
    window.location.href = '/';
  });
  
  $('form#add_user').submit(function(event) {
    event.preventDefault();
    var username = $('input#username').val();
    if (!/^[^\(\),]+$/.test(username)) {
      return;
    }
    var ixuser = parseInt($('input#ixuser').val());
    if (ixuser < 0) {
      return;
    }
    var url = "/users?" + $.param({user: username}) + "&" + $.param({ixuser: ixuser});
    $.post(url, function() {
      $('<tr><td>' + username + '</td><td>' + ixuser + '</td></tr>').appendTo('table#users');
      $('input#username').val('');
      $('input#ixuser').val('');
      $('input#username').focus();
    });
  });



});