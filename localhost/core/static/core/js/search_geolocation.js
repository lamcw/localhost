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
 * @param form      The form to submit on completion
 * */
function activateSearch(id_search, id_lat, id_lng, form) {
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
      $('#' + form).submit();
    }
  });
}
