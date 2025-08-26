function removeEmpty(obj) {
    Object.keys(obj).forEach(key => {
        if (obj[key] && typeof obj[key] === 'object') {
        removeEmpty(obj[key]);
        } else if (obj[key] == null || obj[key] === '') {
        delete obj[key];
        }
    });
    return obj;
}

function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith('csrftoken=')) {
        return cookie.substring('csrftoken='.length, cookie.length);
        }
    }
    return null;
}

async function makeRequest (url, method, data={}, dataType=null, access_token=null) {
    let BASE_API_URL
    if (window.location.href.includes("localhost")) {
        BASE_API_URL = 'http://localhost:8000/en';
    }
    else {
        BASE_API_URL = 'http://mugisa.tech/en';
    }

    let requestData = {
        method: method,
        mode: "cors",
        cache: "no-cache",
        redirect: 'follow',
        referrerPolicy: 'no-referrer',
        // "headers" : {
        //     Authorization: "JWT " + localStorage.getItem("ext_access_token"),
        // }
    };

    if (method == "POST" || method == "PUT" || method == "PATCH" || method == "DELETE") {
        if (dataType == "media") {
            requestData["body"] = data;
            requestData["headers"] = {
                'X-CSRFToken': getCookie()
            }
        }
        else {
            requestData["body"] = JSON.stringify(removeEmpty(data));
            requestData["headers"] = {
                Accept: "application/json",
                "Content-Type": "application/json",
                'X-CSRFToken': getCookie()
            }
        }
    }

    let response = await fetch(`${BASE_API_URL}${url}`, requestData);
    if (!response.ok) {
        let resp = await response.json();
        throw new Error(resp);
    }
    return await response.json();
}