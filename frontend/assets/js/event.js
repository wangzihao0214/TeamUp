let event_id = "";
let user_id = "";
let buy_url = "";
let team_start = 0;
let teams = [];

const BASE_URL = "http://teamup-frontend.s3-website-us-east-1.amazonaws.com/";

function buy_tickets() {
    // open in new tab
    window.open(buy_url, '_blank');
}

function create_team() {
    let team_name = $('#input-team-name').val().trim();
    if (team_name.length === 0) {
        $('#create-err-box').html('<span style="color: red">Team name cannot be empty.</span>');
        return;
    }

    let q_params = {
        'team-name': team_name,
        'event-id': event_id,
        'user-id': user_id,
        'operation': 'create'
    };

    sdk.teamJoinPost({}, {}, {'queryParams': q_params}).then(response => {
        document.getElementById('team-cards').innerHTML = '';
        sdk.eventEventIdGet({'event-id': event_id}, {}, {}).then(response => {
            let data = response.data;
            teams = data["teams"];
            render_teams(team_start);
        });
    });
}

function search_team(){
   let team_name = $('#input-search-name').val().trim();
   if (team_name.length !== 0){
       let q_params = {
            'team-name': team_name,
            'event-id': event_id,
        };
       sdk.teamSearchPost({}, {}, {'queryParams': q_params}).then(response => {
            document.getElementById('team-cards').innerHTML = '';
            teams = response.data;
            if (teams.length !== 0)
                render_teams(0);
            else
                document.getElementById('team-cards').innerHTML = '<h3>No such team.</h3>';
        });
   }
   else{
        document.getElementById('team-cards').innerHTML = '';
        sdk.eventEventIdGet({'event-id': event_id}, {}, {}).then(response => {
            let data = response.data;
            teams = data["teams"];
            render_teams(0);
        });
   }
}

function render_teams(start) {
    let html = '';
    if (teams.length !== 0) {
        html = `<table class="table">
                <thead>
                    <tr>
                        <th scope = "col" id="table-num">#</th>
                        <th scope = "col" id="table-name">Name</th>
                        <th scope = "col" id="table-num_member"># of Members</th>
                        <th scope = "col" id="table-description">Description</th>
                    </tr>
                </thead>
                <tbody>`;
        teams_slice = teams.slice(start, start + 4);
        for (let i = 0; i < teams_slice.length; i++) {
            html += `<tr>
                    <th scope="row">${start + 1 + i}</th>
                    <td>
                        <a href="${BASE_URL}team.html?id=${teams_slice[i]["team-id"]}">
                            ${teams_slice[i]["team name"]}
                        </a>
                    </td>
                    <td>${teams_slice[i]["members"].length}</td>
                    <td id="description">${teams_slice[i]["description"]}</td>
                 </tr>`;
        }
        html += `    </tbody>
            </table>`;
    }
    else{
        html = '<h3>No teams. Create one!</h3>';
    }
    document.getElementById('team-cards').innerHTML = html;
}

function turn_page(flag) {
    if (teams.length == 0) return;
    
    if (teams.length){
        team_start += (flag * 4);
        if(team_start >= teams.length)
            team_start -= 4;
        if(team_start < 0)
            team_start = 0;
        render_teams(team_start);
    }
}

function render_event(data) {
    $('#event-image').attr('src', data["image_url"]);
    $('#num').html(`${data["teams"].length} teams`);
    $('#name').html(data["name"]);
    $('#place').html(data["location"]);
    $('#time').html(data["datetime"]);
    buy_url = data["url"];
    $('#purchase').attr('onclick', 'buy_tickets()');

    teams = data["teams"];
    render_teams(0);
}

window.onload = function(){
    let param = new URLSearchParams(window.location.search);
    event_id = param.get("id");
    user_id = localStorage.getItem('user_id');

    console.log(event_id);
    console.log(user_id);
    
    sdk.eventEventIdGet({'event-id': event_id}, {}, {}).then(response => {
        let data = response.data;
        console.log(data);
        render_event(data);
    });
}


function profile() {
    window.location = `${BASE_URL}profile.html?id=${user_id}`;
}

function home() {
    window.location = `${BASE_URL}home.html`;
}

