const CLIENT_ID = "43280fdcc46c4665b6dd5bb3502a89e1";
const SPOTIFY_AUTHORIZE_ENDPOINT = "https://accounts.spotify.com/authorize";
const REDIRECT_URL_AFTER_LOGIN = "http://teamup-frontend.s3-website-us-east-1.amazonaws.com/";
const SPACE_DELIMITER = "%20";
const SCOPES = [
  "user-follow-read"
];
const SCOPES_URL_PARAM = SCOPES.join(SPACE_DELIMITER);
const BASE_URL = "http://teamup-frontend.s3-website-us-east-1.amazonaws.com/";

function log_in(){
    window.location = `${SPOTIFY_AUTHORIZE_ENDPOINT}?client_id=${CLIENT_ID}&redirect_uri=${REDIRECT_URL_AFTER_LOGIN}&scope=${SCOPES_URL_PARAM}&response_type=token&show_dialog=true`;
}

function getReturnedParamsFromSpotifyAuth(hash){
  const stringAfterHashtag = hash.substring(1);
  const paramsInUrl = stringAfterHashtag.split("&");
  return paramsInUrl.reduce((accumulater, currentValue) => {
    const [key, value] = currentValue.split("=");
    accumulater[key] = value;
    return accumulater;
  }, {});
}

if (window.location.hash) {
  const {access_token, expires_in, token_type} = getReturnedParamsFromSpotifyAuth(window.location.hash);
  localStorage.setItem('spotify_token', access_token);
    
  sdk.profileSpotifyGet ({'token': access_token}, {}, {}).then(
      response => {
        let data = response.data;
        console.log(data.id);
        let id = data.id;
        localStorage.setItem('user_id', id);
        window.location = `${BASE_URL}home.html`;
      }
  )
}

