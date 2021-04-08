$(document).ready(function(){

$(#ajax).bind('click', function() {
	$.getJSON('/_get_data_by_ein', {
		
    ein: $('input[name="ein"]').val()
    
    	
}, function(data) {
$("#result").text(data.result);
});
return false;
)};
)};

