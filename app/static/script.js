
function send(form, event) {
    url = form.action
    data = {}
    for(let i=0; i<form.length; i++){
        if(form[i].name){
            data[form[i].name] = form[i].value;
        }
    }
    fetch(url, {
        method: form.method,
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(res=>getResponseToJSON(res))
    .then(json=>getJSON(json))
    .catch(err=>console.error('error:' + err));
    return false
}

function getResponseToJSON(res){
    return res.json()
}

function getJSON(json){
    showMsg(json.message)
    if(json.redirect){
        setTimeout(()=>{location.href = json.redirect}, 2000)
    }
    console.log(json)
}
function showMsg(msg){
    m = document.getElementById('message')
    m.innerHTML = msg
}
