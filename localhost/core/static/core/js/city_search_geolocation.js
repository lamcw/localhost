function activatePlacesSearch() {
  var input = document.getElementById('city_search_geolocation');
  var options = {
    types: ['(cities)'],
    componentRestrictions: {country: 'au'}
  };
  var autocomplete = new google.maps.places.Autocomplete(input, options);
  autocomplete.addListener('place_changed', function() {
    var place = autocomplete.getPlace();
    /* If the request is submitted without clicking an entry in the search
     * place.geometry will be undefined */
    if (place.geometry !== undefined) {
      $('#lat').val(place.geometry.location.lat());
      $('#lng').val(place.geometry.location.lng());
    }
  });
}
