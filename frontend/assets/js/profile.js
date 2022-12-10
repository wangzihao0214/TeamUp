let team_start = 0;
let artist_start = 0;
let image_src = "";
let user_name = "";
let top_artists = [];
let teams = [];
let id = "";
let email = "";
let city = "";
let age = "";
let description = "";

const BASE_URL = "http://teamup-frontend.s3-website-us-east-1.amazonaws.com/";

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

    console.log(id)
    console.log(localStorage.getItem('user_id'));
    if(id === localStorage.getItem('user_id'))
        document.getElementById('header').innerHTML += `<div class="btn" id="edit">
                                                            <button onclick="edit()">
                                                              Edit
                                                            </button>
                                                        </div>`;
    
    sdk.profileUserIdGet({'user-id': id}, {}, {}).then(
        response => {
            let data = response.data;
            console.log(data)
            render_page(data);
        }
    )
}

function render_page(data){
    image_src = data.imageUrl;
    user_name = data.userName;
    top_artists = data.topArtists;
    if ('teams' in data)
        teams = data.teams;
    if ('topArtists' in data)
        top_artists = data.topArtists;
    if ('email' in data)
        email = data.email;
    if ('city' in data)
        city = data.city;
    if ('age' in data)
        age = data.age;
    if ('description' in data)
        description = data.description;

    if (!(image_src === ""))
        document.getElementById("profile-image").src = image_src;
    document.getElementById("name").innerHTML = user_name;
    if (!(description === ""))
        document.getElementById("description").innerHTML = `${description}`;
    if (!(email === ""))
        document.getElementById("email").innerHTML = `<b>Email: </b>${email}`;
    if (!(city === ""))
        document.getElementById("city").innerHTML = `City: ${city}`;
    if (!(age === ""))
        document.getElementById("age").innerHTML = `Age: ${age}`;
    if (teams.length)
        render_cards("team-cards", teams, 0);
    if (top_artists.length)
        render_cards("artist-cards", top_artists, 0);
}

function render_cards(element_id, cards, start){
    html = "";
    cards_slice = cards.slice(start, start + 3);
    for (let i = 0; i < cards_slice.length; i++) {
        html += `<div class="card-wrapper">
            <div class="card">
              <a href=${cards_slice[i].url}>
                <img src=${cards_slice[i].image} alt="">
              </a>
              <div class="card-info">
                <h4>${cards_slice[i].name}</h4>
                <p>${cards_slice[i].info}</p>
              </div>
            </div>
          </div>`
    }
    document.getElementById(element_id).innerHTML = html;
}

function turn_page(flag, element_id){
    if(element_id === "team-cards"){
        if (teams.length){
            team_start += (flag * 3);
            if(team_start >= teams.length)
                team_start -= 3;
            if(team_start < 0)
                team_start = 0;
            render_cards("team-cards", teams, team_start);
        }
    } else {
        if (top_artists.length) {
            artist_start += (flag * 3);
            if (artist_start >= top_artists.length)
                artist_start -= 3;
            if (artist_start < 0)
                artist_start = 0;
            render_cards("artist-cards", top_artists, artist_start);
        }
    }
}

function edit(){
    window.location = `${BASE_URL}edit.html?id=${id}`;
}

function home() {
    window.location = `${BASE_URL}home.html`;
}

