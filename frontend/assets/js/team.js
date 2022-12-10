let event_id = "";
let user_id = "";
let team_id = "";
let member_start = 0;
let members = [];

const BASE_URL = "http://teamup-frontend.s3-website-us-east-1.amazonaws.com/";

function join_team() {
   let q_params = {
        'team-id': team_id,
        'operation': 'join',
        'event-id': event_id,
        'user-id': user_id
    };
    
    sdk.teamJoinPost({}, {}, {'queryParams': q_params}).then(response => {
        location.reload();
    });
}

function render_members(start) {
    let html = '';
    if (members.length !== 0) {
        members_slice = members.slice(start, start + 6);
        for (let i = 0; i < members_slice.length; i++) {
            html += `<div class="card-wrapper">
                        <div class="card">
                          <a href="${BASE_URL}profile.html?id=${members_slice[i]["id"]}">
                            <img src=${members_slice[i].image} alt="">
                          </a>
                          <div class="card-info">
                            <h4>${members_slice[i].name}</h4>
                            <p>${members_slice[i].email}</p>
                          </div>
                        </div>
                      </div>`
        }
    }
    else{
        html = '<h3>No member.</h3>';
    }
    document.getElementById('member-cards').innerHTML = html;
}

function turn_page(flag) {
    if (members.length == 0) return;
    
    if (members.length){
        member_start += (flag * 6);
        if(member_start >= members.length)
            member_start -= 6;
        if(member_start < 0)
            member_start = 0;
        render_members(member_start);
    }
}

function render_team(data) {
    $('#team-name').html(data["team name"]);
    $('#team-desc').html(data["description"]);
    $('#event_name').html(data["event"]["name"]);
    $('#event_date').html(data["event"]["date"]);
    $('#event_location').html(data["event"]["location"]);
    members = data["members"];
    
    let html = ""
    if(data["member_ids"].includes(user_id)){
        html= `<div class="btn" id="edit">
                   <button onclick="edit()">
                       Edit
                   </button>
               </div>`;
    }
    else{
        html= `<div class="btn" id="edit">
                   <button onclick="join_team()">
                       Join
                   </button>
               </div>`;
    }
    document.getElementById('header').innerHTML += html
    render_members(0);
}

window.onload = function(){
    let param = new URLSearchParams(window.location.search);
    team_id = param.get("id");
    user_id = localStorage.getItem('user_id');

    console.log(team_id);
    console.log(user_id);
    
    sdk.teamTeamIdGet({'team-id': team_id}, {}, {}).then(response => {
        let data = response.data;
        console.log(data);
        event_id = data["event"]["id"]
        render_team(data);
    });
}

function back() {
    window.location = `${BASE_URL}event.html?id=${event_id}`;
}

function edit() {
    window.location = `${BASE_URL}edit_team.html?id=${team_id}`;
}

