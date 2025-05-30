let autocomplete;

function initAutoComplete() {
    autocomplete = new google.maps.places.Autocomplete(
        document.getElementById('id_address'),
        {
            types: ['geocode', 'establishment'],
            componentRestrictions: { country: ['in'] },
        }
    );

    autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged() {
    const place = autocomplete.getPlace();

    if (!place.geometry) {
        document.getElementById('id_address').placeholder = "Start typing...";
        return;
    }

    const geocoder = new google.maps.Geocoder();
    const address = document.getElementById('id_address').value;

    geocoder.geocode({ address: address }, function(results, status) {
        if (status === google.maps.GeocoderStatus.OK) {
            const latitude = results[0].geometry.location.lat();
            const longitude = results[0].geometry.location.lng();

            $('#id_latitude').val(latitude);
            $('#id_longitude').val(longitude);
            $('#id_address').val(address);
        }
    });

    place.address_components.forEach(component => {
        component.types.forEach(type => {
            const value = component.long_name;
            if (type === 'country') $('#id_country').val(value);
            if (type === 'administrative_area_level_1') $('#id_state').val(value);
            if (type === 'locality') $('#id_city').val(value);
            if (type === 'postal_code') $('#id_pin_code').val(value);
        });
    });
}

$(document).ready(function () {
    console.log("custom.js is loaded and ready");

    //add to cart


    // Add to cart functionality
    $('.add_to_cart').on('click', function (e) {
        e.preventDefault();

        const food_id = $(this).attr('data-id');
        const url = $(this).attr('data_url');

        $.ajax({
            type: 'GET',
            url: url,
            data: {food_id: food_id},
            headers: {
                'X-Requested-With': 'XMLHttpRequest' // needed for Django to treat as AJAX
            },
            success: function (response) {
                console.log(response);
                console.log(response.card_counter['cart_count']);

                // Optionally update cart UI here
                $('#card_counter').html(response.card_counter['cart_count']);
                $('#qty-'+food_id).html(response.qty);
                applyCartAmounts(
                    response.cart_amount['subtotal'],
                    response.cart_amount['tax_dict'],
                    response.cart_amount['grand_total'])
            }
        });
    });


    $('.decrease_cart').on('click', function (e) {
        e.preventDefault();

        const food_id = $(this).attr('data-id');
        const url = $(this).attr('data_url');
        const cart_id = $(this).attr('id');

        $.ajax({
            type: 'GET',
            url: url,
            headers: {
                'X-Requested-With': 'XMLHttpRequest' // needed for Django to treat as AJAX
            },
            success: function (response) {
                console.log(response);
                if(response.status =='Failed'){
                    console.log(response);
                }
                else
                {
                    $('#card_counter').html(response.card_counter['cart_count']);
                    $('#qty-'+food_id).html(response.qty);
                    applyCartAmounts(
                        response.cart_amount['subtotal'],response.cart_amount['tax_dict'],response.cart_amount['grand_total'])
                    if(window.location.pathname=='/cart/') {
                        removeCartItems(response.qty, cart_id);
                        checkEmptyCart();
                    }
                }
            }
        });
    });


    // Display cart item quantities on load
    $('.item_qty').each(function () {
        var the_id = $(this).attr('id');
        const qty = $(this).attr('data-qty');
        $('#' + the_id).html(qty);

    });

    $('.delete_cart').on('click', function (e) {
        e.preventDefault();

        const cart_id = $(this).attr('data-id');
        const url = $(this).attr('data_url');

        $.ajax({
            type: 'GET',
            url: url,
            headers: {
                'X-Requested-With': 'XMLHttpRequest' // needed for Django to treat as AJAX
            },
            success: function (response) {
                console.log(response);
                applyCartAmounts(
                    response.cart_amount['subtotal'],response.cart_amount['tax_dict'],response.cart_amount['grand_total'])
                if(response.status =='Failed'){
                    console.log(response);
                }
                else
                {
                    $('#card_counter').html(response.card_counter['cart_count']);
                    removeCartItems(0,cart_id);
                    checkEmptyCart();

                }
            }
        });
    });

    function removeCartItems(cartItemQty,cart_id)
    {

            if (cartItemQty <= 0) {
                document.getElementById("cart-item-" + cart_id).remove()

            }

    }

    function checkEmptyCart() {
        var cart_counter = document.getElementById('card_counter').innerHTML
        if (cart_counter == 0)
        {
            document.getElementById("empty-cart").style.display ="block";
        }
    }

    function applyCartAmounts(subtotal,tax_dict,grand_total)
    {
        console.log("mai chala")
        if(window.location.pathname == '/cart/') {
            $('#subtotal').html(subtotal)
            $('#total').html(grand_total)

            for(key1 in tax_dict )
            {
                console.log(tax_dict[key1])
                for (key2 in tax_dict[key1])
                {
                    console.log(tax_dict[key1][key2])
                    $('#tax-'+key1).html(tax_dict[key1][key2])
                }
            }
        }
    }

});

