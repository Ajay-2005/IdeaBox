document.addEventListener('DOMContentLoaded', function () {

	new Quill('#editor', {
		theme: 'snow',
		placeholder: 'Write your comment here...',
	});

	function initializeQuillEditor(editorId) {
		const editorContainer = document.querySelector(`#${editorId}`);
		if (editorContainer && !editorContainer.dataset.quillInitialized) {
			new Quill(editorContainer, {
				theme: 'snow',
				placeholder: 'Write your reply here...',
			});
			editorContainer.dataset.quillInitialized = true;
		}
	}

	document.querySelectorAll('[data-bs-toggle="collapse"]').forEach(button => {
		button.addEventListener('click', () => {
			const collapseId = button.getAttribute('href').replace('#', '');
			const editorId = `reply-editor-${collapseId.replace('reply', '')}`;
			initializeQuillEditor(editorId);
		});
	});
});


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
		.then(response => response.json()) // Parse as JSON
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

function getCSRFToken() {
	const cookieValue = document.cookie
		.split('; ')
		.find(row => row.startsWith('csrftoken='))
		?.split('=')[1];
	return cookieValue;
}


