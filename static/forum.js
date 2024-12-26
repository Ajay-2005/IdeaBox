document.addEventListener('DOMContentLoaded', function () {

	new Quill('#editor', {
		theme: 'snow',
		placeholder: 'Write your comment here...',
	});
	function initializeQuillEditor(editorId) {
		const editorContainer = document.getElementById(editorId);
		if (editorContainer && !editorContainer.dataset.quillInitialized) {
			new Quill(editorContainer, {
				theme: 'snow',
				placeholder: 'Write your reply here...',
			});
			editorContainer.dataset.quillInitialized = true;
		}
	}

	// Initialize the main comment editor
	document.addEventListener('DOMContentLoaded', () => {
		initializeQuillEditor('editor');
	});

	document.querySelectorAll('[data-bs-toggle="collapse"]').forEach(button => {
		button.addEventListener('click', () => {
			const collapseId = button.getAttribute('data-bs-target').replace('#', '');
			const editorId = `reply-editor-${collapseId.replace('reply', '')}`;
			initializeQuillEditor(editorId);
		});
	});

	document.querySelectorAll('.upvote-btn').forEach(button => {
		button.addEventListener('click', function () {
			const commentId = this.dataset.commentId;
			voteComment(commentId, 'upvote', this);
		});
	});

	document.querySelectorAll('.downvote-btn').forEach(button => {
		button.addEventListener('click', function () {
			const commentId = this.dataset.commentId;
			voteComment(commentId, 'downvote', this);
		});
	});
});




function voteComment(commentId, voteType) {
	const csrfToken = getCSRFToken();

	fetch('/forum/vote-comment/', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csrfToken,
		},
		body: JSON.stringify({ comment_id: commentId, vote_type: voteType }),
	})
		.then(response => response.json())
		.then(data => {
			if (data.success) {
				const upvoteButton = document.querySelector(`.upvote-btn[data-comment-id="${commentId}"]`);
				const downvoteButton = document.querySelector(`.downvote-btn[data-comment-id="${commentId}"]`);

				upvoteButton.querySelector('.vote-count').textContent = data.upvotes;
				downvoteButton.querySelector('.vote-count').textContent = data.downvotes;

			} else {
				alert(`Error: ${data.message}`);
			}
		})
		.catch(error => {
			console.error('Error:', error);
			alert('Failed to record your vote. Please try again.');
		});
}

function postComment(postId) {
	const quillEditor = document.getElementById('editor');
	const quillInstance = new Quill(quillEditor);
	const content = quillInstance.getText();
	if (!content) {
		alert('Please enter a comment before submitting.');
		return;
	}

	const payload = {
		post_id: postId,
		content: content,
	};

	const csrfToken = getCSRFToken();
	fetch('/forum/add-comment/', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csrfToken,
		},
		body: JSON.stringify(payload),
	})
		.then(response => response.json())
		.then(data => {
			if (data.success) {
				alert('Comment added successfully!');
				location.reload();
			} else {
				alert(`Error: ${data.message}`);
			}
		})
		.catch(error => {
			console.error('Parsing error:', error);
			alert('Unexpected server response. Please try again.');
		});
}

function postReply(commentId) {
	
	const quillEditor = document.getElementById(`reply-editor-${commentId}`);
	const quillInstance = new Quill(quillEditor);
	const content = quillInstance.getText();
	if (!content) {
		alert('Please enter a reply before submitting.');
		return;
	}

	const payload = {
		comment_id: commentId,
		content: content,
	};

	const csrfToken = getCSRFToken();
	fetch('/forum/add-reply/', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csrfToken,
		},
		body: JSON.stringify(payload),
	})
		.then(response => response.json())
		.then(data => {
			
			if (data.success) {
				alert('Reply added successfully!');
				location.reload();
			} else {
				alert(`Error: ${data.message}`);
			}
		})
		.catch(error => {
			console.error('Parsing error:', error);
			alert('Unexpected server response. Please try again.');
		});
}

function getCSRFToken() {
	const cookieValue = document.cookie
		.split('; ')
		.find(row => row.startsWith('csrftoken='))
		?.split('=')[1];
	return cookieValue;
}


