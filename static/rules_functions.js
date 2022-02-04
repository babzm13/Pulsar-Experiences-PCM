var slide_index = 0;
var max_slides;

$(document).ready(function(){
	var slides = document.getElementsByClassName("slideshow_element");
	var dots = document.getElementsByClassName("dot");

	max_slides = slides.length;

	hide_all_slides(slides);
		
	$(slides[slide_index]).show();

	next_slide();
});

function verify_index() {
	if(slide_index > max_slides - 1) {
		slide_index = 0;
	}
	if (slide_index < 0) {
		slide_index = max_slides - 1;
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

	$(slides[slide_index]).show();

	next_slide();
}

function next_slide() {
	slide_index++;

	setTimeout(show_slides, 2000);
}