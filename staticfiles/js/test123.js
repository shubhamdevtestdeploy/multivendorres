let autocomplete;

function initAutoComplete(){
    autocomplete = new google.maps.places.Autocomplete(
        document.getElementById('id_address'),
        {
            types: ['geocode', 'establishment'],
            componentRestrictions: {'country': ['in']},
        }
    );
    autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged (){
    var place = autocomplete.getPlace();

    if (!place.geometry){
        document.getElementById('id_address').placeholder = "Start typing...";
    }

    var geocoder = new google.maps.Geocoder();
    var address = document.getElementById('id_address').value;

    geocoder.geocode({'address': address}, function(results, status){
        if(status == google.maps.GeocoderStatus.OK){
            var latitude = results[0].geometry.location.lat();
            var longitude = results[0].geometry.location.lng();

            $('#id_latitude').val(latitude);
            $('#id_longitude').val(longitude);
            $('#id_address').val(address);
        }
    });

    for(var i=0; i<place.address_components.length; i++){
        for(var j=0; j<place.address_components[i].types.length; j++){
            var type = place.address_components[i].types[j];
            var value = place.address_components[i].long_name;
            if(type == 'country') $('#id_country').val(value);
            if(type == 'administrative_area_level_1') $('#id_state').val(value);
            if(type == 'locality') $('#id_city').val(value);
            if(type == 'postal_code') $('#id_pin_code').val(value);
        }
    }
}

$(document).ready(function () {
    console.log("custom.js is loaded and ready");

    $('.add_to_cart').on('click', function(e) {
        e.preventDefault();  // Prevent default link behavior

        let food_id = $(this).attr('data-id');
        let url = $(this).attr('data_url');
        data={
            food_id:food_id,
        }
        $.ajax({
            type: 'GET',
            url: url,
            data:data,
            success: function (response)
            {
                console.log(response);
            }
        })

        console.log(`🛒 Clicked add_to_cart: food_id = ${food_id}, url = ${url}`);
        alert(`Adding food ID: ${food_id}\nURL: ${url}`);
    })
});
