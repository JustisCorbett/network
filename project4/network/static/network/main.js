function likePost(button) {
    const post = button.parentNode;
    const postId = post.getAttribute('data-post');
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
            if(response.ok) {
                
            } else {
            return response.json();
            }
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
            if(response.ok) {
                
            } else {
            return response.json();
            }
        })
    }
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