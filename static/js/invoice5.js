$(document).ready(function() {

$('#checker').click(function(){
 if($('input[name="checker"]').is(':checked')){
                 $('#businessname_shipping').val($('#businessname').val());  
                 
                 $('#email_shipping').val($('#email').val());
                 $('#ein_shipping').val($('#ein').val());
                 $('#address_shipping').val($('#address').val());
                 $('#address2_shipping').val($('#address2').val());     
                 $('#city_shipping').val($('#city').val());
                 $('#state_shipping').val($('#state').val());
                 $('#zip_shipping').val($('#zip').val());
                
                 
                
                 
                }else{
                $('#businessname_shipping').val("");
                $('#address_shipping').val("");
                $('#address2_shipping').val("");
                $('#email_shipping').val("");
                $('#ein_shipping').val("");
                $('#city_shipping').val("");
                $('#state_shipping').val("");
                $('#zip_shipping').val("");
                
            
                
                
                
                }
            });
            
            


$('form').on('keyup', 'input[name="item_price[]"], input[name="item_quant[]"]', function() {
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
   
    //çalert (totaltaxes);
    //$('.amount').val(amount.toFixed(2));
    
     
    
})
	
});