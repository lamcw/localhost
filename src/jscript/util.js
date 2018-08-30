/**
 * @brief Set the search quote that appears in the main search box of the homepage
 */
function set_search_quote() {
    $.getJSON("assets/search_quotes.json", function(quotes) {
        const index = Math.floor(Math.random() * quotes["search_quotes"].length);
        const quote = quotes["search_quotes"][index];
        $("#search").attr("placeholder", quote);
    });
}

/**
 * @brief Set the wallpaper of the homepage
 */
function set_homepage_wallpaper() {
    $.getJSON("assets/wallpapers.json", function(wallpapers) {
        const index = Math.floor(Math.random() * wallpapers["wallpapers"].length);
        const wallpaper_object = wallpapers["wallpapers"][index];
        $("body").css("background-image", "url(" + wallpaper_object["link"] + ")");
    });
}
