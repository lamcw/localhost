function activatePlacesSearch() {
  var input = document.getElementById('id_address');
  var options = {
    types: ['address'],
    componentRestrictions: {country: 'au'}
  };
  var autocomplete = new google.maps.places.Autocomplete(input, options);
}