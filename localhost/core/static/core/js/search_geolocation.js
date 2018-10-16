/**
 * @brief Activates a location search autocomplete and stores the location
 *        of selected entries
 *
 * @param id_search The id of the search input field to inject the
 *                  autocomplete dropdown
 * @param id_lat    The id of the input where the latitude of a selection is
 *                  stored
 * @param id_lng    The id of the input where the longitude of a selection is
 *                  stored
 * @param id_addr   The id of the input where the address of a selection is
 *                  stored
 * @param form      The form to submit on completion
 * */
function activateSearch(id_search, id_lat, id_lng, id_addr, form) {
  var search_input = document.getElementById(id_search);

  var search_options = {
    componentRestrictions: {country: 'au'}
  };

  var autocomplete = new google.maps.places.Autocomplete(search_input, search_options);
  autocomplete.addListener('place_changed', function() {
    var place = autocomplete.getPlace();
    /* If the request is submitted without clicking an entry in the search
     * place.geometry will be undefined */
    if (place.geometry !== undefined) {
      $('#' + id_lat).val(place.geometry.location.lat());
      $('#' + id_lng).val(place.geometry.location.lng());
      $('#' + id_addr).val($('#' + id_search).val());
      $('#' + form).submit();
    }
  });
}

/**
 * @brief Gets the URL, the GET parameters in the URL and sets the respective search
 *        input fields in the form
 * */
var url = new URL(window.location.href);
var guests = url.searchParams.get('guests');
var biddingActive = url.searchParams.get('bidding-active');

$('#suburb_search').val(url.searchParams.get('addr'));
$('#full_addr').val(url.searchParams.get('addr'));
$('#suburb_search_lat').val(url.searchParams.get('lat'));
$('#suburb_search_lng').val(url.searchParams.get('lng'));

if (guests != null) {
  $('#guests').val(guests);
}

if (biddingActive != null) {
  $('#bidding-active').parent().addClass('active');
  $('#bidding-active').prop('checked', true);
}