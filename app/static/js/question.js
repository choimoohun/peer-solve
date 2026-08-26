const questionId = document.body.dataset.questionId;

document.addEventListener("DOMContentLoaded", function () {
    loadComments();
});

function formatDate(dateString) {
    const date = new Date(dateString);

    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");

    return `${year}-${month}-${day}`;
}

function ask_delete() {
    if (!confirm("정말 삭제하시겠습니까?")) {
        return;
    }

    $.ajax({
        type: "DELETE",
        url: `/api/question/${questionId}`,
        success: function (response) {
            alert("삭제되었습니다.");
            location.href = "/main";
        },
        error: function (xhr) {
            alert(xhr.responseJSON?.message || "삭제에 실패했습니다.");
        }
    });
}

function loadComments() {
    $.ajax({
        type: "GET",
        url: `/api/comment/${questionId}`,
        success: function (response) {
            $("#total").text(`댓글 ${response.count}개`);
            $("#comment-list").empty();

            response.comments.forEach(function (comment) {
                $("#comment-list").append(`
                    <div class="mb-3">
                        <strong>${comment.nickname}</strong>
                        <span>${formatDate(comment.at_create)}</span>
                        <p>${comment.text}</p>
                    </div>
                `);
            });
        },
        error: function (xhr) {
            alert(xhr.responseJSON?.message || "댓글을 불러오지 못했습니다.");
        }
    });
}

function add_comment() {
    $.ajax({
        type: "POST",
        url: `/api/comment/${questionId}`,
        data: {
            text: $("#text").val()
        },
        success: function (response) {
            alert("댓글을 성공적으로 작성했습니다!");
            $("#text").val("");
            loadComments();
        },
        error: function (xhr) {
            alert(xhr.responseJSON?.message || "댓글 작성에 실패했습니다.");
        }
    })
}