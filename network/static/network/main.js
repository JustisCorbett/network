function likePost(button) {
    const post = button.parentNode;
    const postId = post.parentNode.getAttribute('data-post');
    const isLiked = button.getAttribute('data-liked');
    const csrftoken = getCookie('csrftoken');
    const likeNumEl = post.getElementsByClassName('num-likes')[0];
    let likeNum = likeNumEl.innerText;

    if (isLiked === 'false') {
        
        likeNum++;
        likeNumEl.innerText = likeNum;
        button.classList.remove('btn-success');
        button.classList.add('btn-secondary');
        button.setAttribute('data-liked', 'true');
        button.setAttribute('disabled', 'true');
        button.innerText = 'Unlike';

        fetch('like_post', {
            method: 'PUT',
            credentials: 'include',
            headers: new Headers ({
                "X-CSRFToken": csrftoken,
                'content-type': 'application/json'
            }),
            body: JSON.stringify({
                post_id: postId,
            })
        }).then(response => {
            button.removeAttribute('disabled');
            return response.json();
        }).then(message => {
            console.log(message)
        })
    } 
    else {
        likeNum--;
        likeNumEl.innerText = likeNum;
        button.classList.remove('btn-secondary');
        button.classList.add('btn-success');
        button.setAttribute('data-liked', 'false');
        button.setAttribute('disabled', 'true');
        button.innerText = 'Like';

        fetch('like_post', {
            method: 'DELETE',
            credentials: 'include',
            headers: new Headers ({
                "X-CSRFToken": csrftoken,
                'content-type': 'application/json'
            }),
            body: JSON.stringify({
                post_id: postId,
            })
        }).then(response => {
            button.removeAttribute('disabled');
            return response.json();
        }).then(message => {
            console.log(message)
        })
    }
}


function editPost(button) {
    const btnVal = button.value;
    const postCont = button.parentNode.parentNode;
    const postDiv = postCont.getElementsByClassName('post')[0];
    const editDiv = postCont.getElementsByClassName('post-edit')[0];
    const postText = postDiv.getElementsByClassName('post-text')[0].innerText;
    const editForm = editDiv.getElementsByClassName('edit-form')[0];

    if (btnVal === 'open') {
        postDiv.classList.add('hidden');
        editDiv.classList.remove('hidden');
        editForm.value = postText;
    } else if (btnVal === 'close') {
        postDiv.classList.remove('hidden');
        editDiv.classList.add('hidden');
    }
}


function saveEdit(button) {
    const editDiv = button.parentNode;
    const editForm = editDiv.getElementsByClassName('edit-form')[0];
    const text = editForm.value;
    const postDiv = editDiv.parentNode.getElementsByClassName('post')[0];
    const postId = editDiv.parentNode.getAttribute('data-post');
    const postText = editDiv.parentNode.getElementsByClassName('post-text')[0];
    const csrftoken = getCookie('csrftoken');
    button.setAttribute('disabled', 'true');

    fetch('edit_post', {
        method: 'PUT',
        credentials: 'include',
        headers: new Headers ({
            "X-CSRFToken": csrftoken,
            'content-type': 'application/json'
        }),
        body: JSON.stringify({
            post_id: postId,
            text: text
        })
    }).then(response => {
        button.removeAttribute('disabled');
        if (response.ok) {
            postText.innerText = text;
            postDiv.classList.remove('hidden');
            editDiv.classList.add('hidden');
            return response.json();
        } else {
            return response.json();
        }
    }).then(message => {
        console.log(message);
        alert(message["message"]);
    })

}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}