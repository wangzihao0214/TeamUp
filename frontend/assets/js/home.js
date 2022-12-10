let id = "";
let data = {};
let artists = [];
let latitude = 0.0;
let longitude = 0.0;
let artist_recs = [];
let location_recs = [];
let other_recs = [];
let artist_recs_start = 0;
let location_recs_start = 0;
let other_recs_start = 0;


const BASE_URL = "http://teamup-frontend.s3-website-us-east-1.amazonaws.com/";

function generate_card(data)
{
    let image = data["image"];
    let name = data["name"];
    let datetime = data["datetime"];
    let location = data["location"];
    let event_id = data["id"];

    return `<div class="card-wrapper">
                       <div class="card">
                         <a href="${BASE_URL + 'event.html?id=' + event_id}">
                           <img src="${image}">
                         </a>
                         <div class="card-info">
                           <h4>${name}</h4>
                           <p>${location}</p> 
                           <p>${datetime}</p>
                         </div>
                       </div>
                     </div>`;
}

function render_cards(element_id, cards, start){
    html = "";
    cards_slice = cards.slice(start, start + 4);
    for (let i = 0; i < cards_slice.length; i++) {
        html += generate_card(cards_slice[i]);
    }
    document.getElementById(element_id).innerHTML = html;
}

function render_recommendations(data)
{
    artist_recs = data["artist_recommendations"];
    location_recs = data["location_recommendations"];
    other_recs = data["other_recommendations"];

    render_cards('artist-cards', artist_recs, 0);
    render_cards('near-cards', location_recs, 0);
    render_cards('other-cards', other_recs, 0);
}

function turn_page(flag, element_id){
    if(element_id === "artist-cards"){
        if (artist_recs.length){
            artist_recs_start += (flag * 4);
            if(artist_recs_start >= artist_recs.length)
                artist_recs_start -= 4;
            if(artist_recs_start < 0)
                artist_recs_start = 0;
            render_cards("artist-cards", artist_recs, artist_recs_start);
        }
    }
    else if(element_id === "near-cards"){
        if (location_recs.length) {
            location_recs_start += (flag * 4);
            if (location_recs_start >= location_recs.length)
                location_recs_start -= 4;
            if (location_recs_start < 0)
                location_recs_start = 0;
            render_cards("near-cards", location_recs, location_recs_start);
        }
    }
    else{
        if (other_recs.length) {
            other_recs_start += (flag * 4);
            if (other_recs_start >= other_recs.length)
                other_recs_start -= 4;
            if (other_recs_start < 0)
                other_recs_start = 0;
            render_cards("other-cards", other_recs, other_recs_start);
        }
    }
}

function do_and_render_search(position)
{
    latitude = position.coords.latitude;
    longitude = position.coords.longitude;
    console.log(latitude + ", " + longitude);

    cleaned_artists = artists.map((artist) => {return artist["name"]});
    let body = {
        'artists': cleaned_artists,
        'latitude': latitude,
        'longitude': longitude
    };

    // this is a hack: we use a POST api because it lets us send a JSON list in the request body,
    // which you can't do with a GET request
    sdk.searchPost({}, body, {}).then(response => {
        data = response.data;
        console.log(data);

        render_recommendations(data);
        $('#loading-suggestions').html('');
    });
}

window.onload = function(){
    let param = new URLSearchParams(window.location.search);
    id = param.get("id");
    if (id == null || id.length === 0) {
        id = localStorage.getItem('user_id');
    }

    // if it's still null, force the user to login again
    if (id == null || id.length === 0) {
        window.location = `${BASE_URL}index.html`;
    }
    
    console.log(id);
    sdk.profileUserIdGet({'user-id': id}, {}, {}).then(
        response => {
            data = response.data;
            console.log(data)
            artists = data["topArtists"]
            console.log(artists);

            navigator.geolocation.getCurrentPosition(do_and_render_search);
        }
    )
}

function profile() {
    window.location = `${BASE_URL}profile.html?id=${id}`;
}
