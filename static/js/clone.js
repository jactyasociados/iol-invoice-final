$(document).ready(function () {
$("#remove").attr("disabled", true);


$("#clone").click(function() {
    var $new = $(".cloned-row:first").clone().insertAfter(".cloned-row:last");
    $new.find('input[type=text]').val('');
    
    var y = $(window).scrollTop();  //your current y position on the page
    $(window).scrollTop(y+150);
    
    
    $("#remove").attr("disabled", false);
});


    $("#remove").click(function () {
    var num = $(".cloned-row").length;
    
    //jAlert("num", num);
    $(".cloned-row:last").remove();     
    
    var subtotal = 0;
    var tax = 0;
    var taxes = 0;
    var totaltaxes = 0;
    
    $('form').find('.row').each(function() {
        var $this = $(this);
        var amount = (parseFloat($this.find('input[name="item_price[]"]').val(), 10) || 0)
        * (parseFloat($this.find('input[name="item_quant[]"]').val(), 10) || 0);
        subtotal += amount;
        
        $this.find('input[name="amount[]"]').val(amount.toFixed(2));
       
        tax = $('input[name="taxes"]').val();
        taxes = tax/100;
        totaltaxes = taxes*subtotal;
         $('#subtotal').val(subtotal.toFixed(2));
        $('#totaltax').val(totaltaxes.toFixed(2));
        $('#grandtotal').val((subtotal + totaltaxes).toFixed(2));
      
      
       
    }) 
    
    
    if (num - 1 === 1) $("#remove").attr("disabled", true);        //Remove section.
    });
});
