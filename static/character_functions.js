$(document).ready(function(){
	$(".character").addClass("hidden");
	
	$("input[type='number']").change(function() {
		var input_id = $(this).attr('id');
		var input_value = $(this).val();
		
		var hp = "#" + input_id + "hp";
		var mp = "#" + input_id + "mp";
		
		var server_data = [
			{"id": input_id},
			{"xp": input_value}
		]
		
		$.ajax({
			type: "POST",
			url: "/update_hp_mp",
			data: JSON.stringify(server_data),
			contentType: "application/json",
			dataType: 'json',
			success: function(results) {
				$(hp).load("/new_hp_mp #hp", {"charid": input_id});
				$(mp).load("/new_hp_mp #mp", {"charid": input_id});
			}
		});
	});
});

function display(char_id) {
	var element_id = "#char_" + char_id;
	
	$(element_id).toggleClass("hidden");
}