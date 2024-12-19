
var quill1 = new Quill('#editor1', {
    theme: 'snow',
    placeholder: 'Write a comment...',
    modules: {
        toolbar: [
            [{ 'header': '1' }, { 'header': '2' }, { 'font': [] }],
            [{ 'list': 'ordered' }, { 'list': 'bullet' }],
            [{ 'align': [] }],
            ['bold', 'italic', 'underline'],
            ['link'],
            [{ 'indent': '-1' }, { 'indent': '+1' }],
            ['blockquote', 'code-block'],
            ['clean']
        ]
    }
});
var quill1 = new Quill('#editor2', {
    theme: 'snow',
    placeholder: 'Write a comment...',
    modules: {
        toolbar: [
            [{ 'header': '1' }, { 'header': '2' }, { 'font': [] }],
            [{ 'list': 'ordered' }, { 'list': 'bullet' }],
            [{ 'align': [] }],
            ['bold', 'italic', 'underline'],
            ['link'],
            [{ 'indent': '-1' }, { 'indent': '+1' }],
            ['blockquote', 'code-block'],
            ['clean']
        ]
    }
});

let replyform = document.getElementById('reply-comment');

document.getElementById('reply-btn').addEventListener('click', function () {
    replyform.style.display = 'block';
})

document.getElementById('searchBox').addEventListener('input', function () {
    let searchQuery = document.getElementById('searchBox').value.toLowerCase();
    let posts = document.querySelectorAll('.list-group-item');
    posts.forEach(function (post) {
        let title = post.querySelector('h5').textContent.toLowerCase();
        if (title.includes(searchQuery)) {
            post.style.display = 'block';
        } else {
            post.style.display = 'none';
        }
    });
});

