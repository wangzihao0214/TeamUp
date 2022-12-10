let id = "";
const BASE_URL = "http://teamup-frontend.s3-website-us-east-1.amazonaws.com/";

window.onload = function() {
    const param = new URLSearchParams(window.location.search);
    id = localStorage.getItem('user_id');
    if (id == null || id.length == 0) {
        id = param.get("id");
    }
    sdk.profileUserIdGet({'user-id': id}, {}, {}).then(
        response => {
            let data = response.data;
            console.log(data);
            if ('email' in data)
                document.getElementById('email').value = data.email;
            if ('city' in data)
                document.getElementById('city').value = data.city;
            if ('age' in data)
                document.getElementById('age').value = data.age;
            if ('description' in data)
                document.getElementById('description').value = data.description;
        }
    )
}

function submit_form(form){
    console.log("submitting");
    let formData = new FormData(form);
    let email = formData.get("email");
    let city = formData.get("city");
    let age = formData.get("age");
    let description = formData.get("description");
    let data = {};
    if (email.length)
        data.email = email;
    if (city.length)
        data.city = city;
    if (age.length)
        data.age = age;
    if (description.length)
        data.description = description;
    console.log(data);
    sdk.profileUpdatePost({'user-id': id, 'data': JSON.stringify(data)}, {}, {}).then(
        response => {
            profile();
        }
    );
}

function profile(){
    window.location = `${BASE_URL}profile.html?id=${id}`;
}
