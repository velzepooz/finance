// check_registration
$( "#login" ).change(function() {
    var login = $(this).val();
    if (login != '') {
      $.ajax({
      url: "/check",
      type: "get",
      data: { username: login },
      success: function(json) {
        if (json == false){
          $("#result").removeClass().addClass('form-text-result-invalid').text('Username already in use');
          document.getElementById("process_input").addEventListener("click", function(event){
          event.preventDefault();
          event.stopPropagation();
              });
        }
        else {
          $("#result").removeClass().addClass('form-text-result-valid').text('Username is free');
          document.getElementById("process_input").addEventListener("click", function(event){
              $("form").submit();
              });
            }
          }
      });
    }
  });


// check login
$( "#login_login" ).change(function() {
  var login = $(this).val();
  $( "#password_login" ).change(function(){
    var password = $(this).val();
    if (login != '' && password != '') {
      $.ajax({
      url: "/check_login",
      type: "get",
      data: { username: login, password: password },
      success: function(json) {
        if (json == false) {
          $("#result").removeClass().addClass('form-text-result-invalid').text('Wrong username and/or password');
          function reload() {
            window.location.reload();
          }
          setTimeout(reload, 5000);
          document.getElementById("process_input_login").addEventListener("click", function(event){
          event.preventDefault();
          event.stopPropagation();
              });
        }
        else if (json == true) {
          $("#result").empty();
          document.getElementById("process_input_login").addEventListener("click", function(event){
              $("form").submit();
              });
            }
          }
      });
    }
    });
  });


// check_buy_symbol
$( "#buy_symbol" ).change(function() {
    var symbol = $(this).val();
    if (symbol != '') {
      $.ajax({
      url: "/check_buy_symbol",
      type: "get",
      data: { symbol: symbol },
      success: function(json) {
        if (json == false){
          $("#result").removeClass().addClass('form-text-result-invalid').text('Invalid symbol');
          document.getElementById("buy-button").addEventListener("click", function(event){
          event.preventDefault();
          event.stopPropagation();
              });
        }
        else {
          $("#result").empty();
          document.getElementById("buy-button").addEventListener("click", function(event){
              $("form").submit();
              });
            }
          }
      });
    }


// check valid input - buy_shares
  $( "#buy_shares" ).change(function() {
      var shares = $(this).val();
      if (parseInt(shares))
      {
        $.ajax({
        url: "/check_buy_shares",
        type: "get",
        data: { symbol: symbol, shares: shares },
        success: function(json) {
          if (json == false){
            $("#result_shares").removeClass().addClass('form-text-result-invalid').text('You have not enough money on your balance');
            document.getElementById("buy-button").addEventListener("click", function(event){
            event.preventDefault();
            event.stopPropagation();
                });
          }
          else {
            $("#result_shares").empty();
            document.getElementById("buy-button").addEventListener("click", function(event){
                $("form").submit();
                });
              }
            }
        });
      }
      else {
        $("#result_shares").removeClass().addClass('form-text-result-invalid').text('Invalid symbol');
        document.getElementById("buy-button").addEventListener("click", function(event){
            event.preventDefault();
            event.stopPropagation();
                });
      }
    });
  });


//check valid input - sell_page
$( "#sell-field" ).change(function() {
    var amount = $(this).val();
    if (isNaN(parseInt(amount))) {
        $("#result").removeClass().addClass('form-text-result-invalid').text('Must be integers');
          document.getElementById("charge-button").addEventListener("click", function(event){
          event.preventDefault();
          event.stopPropagation();
              });
    }
    else
    {
        $("#result").empty();
            document.getElementById("charge-button").addEventListener("click", function(event){
                $("form").submit();
                });
    }
  });


//check valid symbols in charge balance
$( "#charge-field" ).change(function() {
    var charge_field = $(this).val();
    if (isNaN(parseInt(charge_field))) {
        $("#result").removeClass().addClass('form-text-result-invalid').text('Must be integers');
          document.getElementById("charge-button").addEventListener("click", function(event){
          event.preventDefault();
          event.stopPropagation();
              });
    }
    else
    {
        $("#result").empty();
            document.getElementById("charge-button").addEventListener("click", function(event){
                $("form").submit();
                });
    }
  });


//validate if forms are complete
(function() {
  window.addEventListener('load', function() {
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.getElementsByClassName('needs-validation');
    // Loop over them and prevent submission
    var validation = Array.prototype.filter.call(forms, function(form) {
      form.addEventListener('submit', function(event) {
        if (form.checkValidity() === false) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add('was-validated');
      }, false);
    });
  }, false);
})();


