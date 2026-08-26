const groupId = $("body").attr("data-group-id");

function fail(xhr) {
    alert(xhr.responseJSON?.error || "요청에 실패했습니다.");
}

$("#btn-group-rename").on("click", function () {
    const name = $("#input-group-name").val().trim();
    if (!name) {
        alert("그룹 이름을 입력하세요.");
        return;
    }

    $.ajax({
        type: "PUT",
        url: `/api/group/edit?id=${groupId}&change=${encodeURIComponent(name)}`,
        success: function () {
            location.reload();
        },
        error: fail
    });
});

$("#btn-group-delete").on("click", function () {
    if (!confirm("그룹을 삭제하면 되돌릴 수 없습니다. 삭제할까요?")) return;

    $.ajax({
        type: "DELETE",
        url: `/api/group/delete?id=${groupId}`,
        success: function () {
            location.href = "/main";
        },
        error: fail
    });
});

$("#btn-group-leave").on("click", function () {
    if (!confirm("이 그룹에서 나갈까요?")) return;

    $.ajax({
        type: "DELETE",
        url: `/api/group/leave?id=${groupId}`,
        success: function () {
            location.href = "/main";
        },
        error: fail
    });
});

$("#btn-member-invite").on("click", function () {
    const userId = (prompt("초대할 사용자의 로그인 ID") || "").trim();
    if (!userId) return;

    $.ajax({
        type: "POST",
        url: `/api/group/invite?id=${groupId}`,
        data: { userId: userId },
        success: function () {
            location.reload();
        },
        error: fail
    });
});

$(".code-list").on("click", "button.member-kick", function () {
    if (!confirm("이 멤버를 추방할까요?")) return;

    const userId = $(this).attr("data-user-id");
    $.ajax({
        type: "DELETE",
        url: `/api/group/kick?id=${groupId}&userId=${encodeURIComponent(userId)}`,
        success: function () {
            location.reload();
        },
        error: fail
    });
});
