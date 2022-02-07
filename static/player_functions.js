$(document).ready(function(){
	$("#change_password").toggleClass("hidden");
	$("#legal_release").toggleClass("hidden");
	$("#phone_error").toggleClass("hidden");
	$("#update_complete").toggleClass("hidden");

});

function change_values() {
	var first = document.getElementById("first").value;
	var last = document.getElementById("last").value;
	var email = document.getElementById("email").value;
	var pn = document.getElementById("pronouns").value;
	var e_c_n = document.getElementById("e_c_n").value;
	var e_c_p = document.getElementById("e_c_p").value;
	
	var server_data = [
		{"first": first},
		{"last": last},
		{"email": email},
		{"pronouns": pn},
		{"e_c_n": e_c_n},
		{"e_c_p": e_c_p}
	];
	
	$.ajax({
		type: "POST",
		url: '/process_pc_data',
		data: JSON.stringify(server_data),
		contentType: "application/json",
		dataType: 'json',
		success: function(results) {
			if (results['processed'] == "true") {
				$("#update_complete").removeClass("hidden");
				$("#phone_error").addClass("hidden");
			} else {
				$("#phone_error").removeClass("hidden");
				$("#update_complete").addClass("hidden");
			}
		}
	});
}

function toggle_password() {
	$("#change_password").toggleClass("hidden");
	$("#password_button").toggleClass("hidden");
	if($("#password_button").attr("value") == "Hide Change Password") {
		$("#password_button").attr("value", "Show Change Password");
	} else {
		$("#password_button").attr("value", "Hide Change Password")
	}

}

function change_password() {
	var oldpw = document.getElementById("orgpw").value;
	var newpw1 = document.getElementById("newpw1").value;
	var newpw2 = document.getElementById("newpw2").value;
	
	var server_data = [
		{"oldpw": oldpw},
		{"newpw1": newpw1},
		{"newpw2": newpw2}
	]
	
	$.ajax({
		type: "POST",
		url: "/change_password",
		data: JSON.stringify(server_data),
		contentType: "application/json",
		dataType: 'json',
		success: function(results) {
			if (results['processed'] != "true") {
				alert(results[1]['error']);
			} else {
				alert("Password successfully changed. Please log in again.");
				window.location.href="/login";
			}
		}
	});
}

function update_lr() {
	var name = document.getElementById("lr_name").value;
	var today = new Date();
	var date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
	
	var server_data = [
		{"name": name},
		{"date": date}
	]
	
	$.ajax({
		type: "POST",
		url: "/update_legal_release",
		data: JSON.stringify(server_data),
		contentType: "application/json",
		dataType: 'json',
		success: function(results) {
			$("#date_signed").load("/get_lr_date #date");
		}
		
		/* success: function(results) {
			alert("Legal release updated successfully.");
			window.location.href="/player_info";
		} */
	});	
}

function toggle_lr() {
	$("#legal_release").toggleClass("hidden");
	$("#legal_release_button").toggleClass("hidden");
	if($("#legal_release_button").attr("value") == "Show Legal Release") {
		$("#legal_release_button").attr("value", "Hide Legal Release");
	} else {
		$("#legal_release_button").attr("value", "Show Legal Release");
	}
}