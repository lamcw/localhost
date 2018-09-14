function activatePlacesSearch() {
  var input = document.getElementById('address_search');
  var options = {
    types: ['address'],
    componentRestrictions: {country: 'au'}
  };
  var autocomplete = new google.maps.places.Autocomplete(input, options);
}
