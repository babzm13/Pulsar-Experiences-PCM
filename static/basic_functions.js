var slide_index = 0;
var max_slides;

$(document).ready(function(){
	var slides = document.getElementsByClassName("slideshow_element");
	var dots = document.getElementsByClassName("dot");

	max_slides = slides.length;

	hide_all_slides(slides);
		
	$(slides[slide_index]).show();
	$(dots[slide_index]).toggleClass("active");
});

function verify_index() {
	if(slide_index > max_slides - 1) {
		slide_index = 0;
	}
	if (slide_index < 0) {
		slide_index = max_slides - 1;
	}
}

function scroll_slides(scroll_num){
	slide_index += scroll_num
	verify_index();
	show_slides();
}

function to_slide(slide_num) {
	slide_index = slide_num - 1;
	verify_index();
	show_slides();
}

function clear_all_dots(dots) {
	console.log($(dots[0]));
	for(index = 0; index < max_slides; index++) {
		if($(dots[index]).hasClass("active")) {
			$(dots[index]).toggleClass("active");
		}
	}
}

function hide_all_slides(slides) {
	for (index = 0; index < max_slides; index++) {
		$(slides[index]).hide();
	}
}

function show_slides() {
	var slides = document.getElementsByClassName("slideshow_element");
	var dots = document.getElementsByClassName("dot");

	verify_index();
	
	hide_all_slides(slides);
	clear_all_dots(dots);

	$(slides[slide_index]).show();
	$(dots[slide_index]).toggleClass("active");
}

function next_slide() {
	slide_index++;

	setTimeout(show_slides, 2000);
}