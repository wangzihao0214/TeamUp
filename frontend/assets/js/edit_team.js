let team_id = "";
const BASE_URL = "http://teamup-frontend.s3-website-us-east-1.amazonaws.com/";

window.onload = function() {
    const param = new URLSearchParams(window.location.search);
    team_id = param.get("id");
    sdk.teamTeamIdGet({'team-id': team_id}, {}, {}).then(
        response => {
            let data = response.data;
            console.log(data);
            if ('description' in data)
                document.getElementById('description').value = data["description"];
        }
    )
}

function submit_form(form){
    console.log("submitting");
    let formData = new FormData(form);
    let description = formData.get("description");
    let data = {};
    if (description.length)
        data.description = description;
    console.log(data);
    let q_params = {
        'team-id': team_id,
        'data': JSON.stringify(data)
    };
    sdk.teamUpdatePost({}, {}, {'queryParams': q_params}).then(
        response => {
            team();
        }
    );
}

function team(){
    window.location = `${BASE_URL}team.html?id=${team_id}`;
}
