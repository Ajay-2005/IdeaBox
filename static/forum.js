document.addEventListener('DOMContentLoaded', function () {

	new Quill('#editor', {
		theme: 'snow',
		placeholder: 'Write your comment here...',
	});
	document.querySelectorAll('[data-bs-toggle="collapse"]').forEach(button => {
		button.addEventListener('click', () => {
			const collapseId = button.getAttribute('data-bs-target').replace('#', '');
			const editorId = `reply-editor-${collapseId.replace('reply', '')}`;

			// Check if the button is an "edit" button
			if (button.classList.contains('edit-btn')) {
				const editEditorId = `editor-${collapseId.replace('edit', '')}`;

				// Wait for the collapse animation to complete before initializing Quill
				document.getElementById(collapseId).addEventListener('shown.bs.collapse', () => {
					if (!document.getElementById(editEditorId).classList.contains('ql-container')) {
						initializeQuillEditor(editEditorId);
					}
				}, { once: true });
			}

			// Wait for the collapse animation to complete before initializing Quill for reply
			document.getElementById(collapseId).addEventListener('shown.bs.collapse', () => {
				if (!document.getElementById(editorId).classList.contains('ql-container')) {
					initializeQuillEditor(editorId);
				}
			}, { once: true });
		});
	});

	// Example Quill initialization function
	function initializeQuillEditor(editorId) {
		const editorElement = document.getElementById(editorId);
		if (editorElement && !editorElement.classList.contains('ql-container')) {
			new Quill(`#${editorId}`, {
				theme: 'snow',
			});
		}
	}

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

function deleteComment(commentId) {
	if (confirm('Are you sure you want to delete this comment?')) {
		// Send an AJAX request to delete the comment
		fetch(`/comment/delete/${commentId}/`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': getCSRFToken() // Replace with your method to get CSRF token
			}
		})
			.then(response => {
				if (response.ok) {
					alert('Comment deleted successfully!');
					location.reload()

				} else {

					throw new Error('Failed to delete comment.');
				}
			})
			.catch(error => {
				console.error('Error deleting comment:', error);
				alert('Failed to delete comment. Please try again.');
			});
	}
}

function updateComment(commentId) {
	const editorId = `editor-${commentId}`;
	const quillEditor = Quill.find(document.getElementById(editorId)); // Retrieve the Quill editor instance
	const updatedContent = quillEditor.root.innerHTML; // Get the updated content
	console.log(updatedContent);
	// Send an AJAX request to update the comment
	fetch(`/comment/edit/${commentId}/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': getCSRFToken() // Replace with your method to get CSRF token
		},
		body: JSON.stringify({ content: updatedContent })
	})
		.then(response => {
			if (response.ok) {
				return response.json();
			}
			throw new Error('Failed to update comment.');
		})
		.then(data => {
			console.log(data)
			alert('Comment updated successfully!');
		})
		.catch(error => {
			console.error('Error updating comment:', error);
			alert('Failed to update comment. Please try again.');
		});
}


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


