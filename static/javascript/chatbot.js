$(document).ready(function () {
    $("#messageArea").on("submit", function (event) {
        const date = new Date();
        const options = { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric', hour: 'numeric', minute: 'numeric' };
        const str_time = date.toLocaleString('en-US', options);

        const rawText = $("#text").val();
        const language = $("#language").val();
        const advancedMode = $("#flexSwitchCheckReverse").is(":checked");

        let userHtml = '<div class="d-flex justify-content-end mb-4"><div class="msg_cotainer_send">' + rawText + '<span class="msg_time_send">' + str_time + '</span></div><div class="img_cont_msg"><img src="https://i.ibb.co/d5b84Xw/Untitled-design.png" class="rounded-circle user_img_msg"></div></div>';

        $("#text").val("");
        $("#messageFormeight").append(userHtml);

        $.ajax({
            data: {
                msg: rawText,
                language_data: language,
                advanced_mode: advancedMode
            },
            type: "POST",
            url: "/chatbot",
        }).done(function (data) {
            let botHtml = '<div class="d-flex justify-content-start mb-4"><div class="img_cont_msg"><img src="/static/images/logo_white.png" class="rounded-circle user_img_msg"></div><div class="msg_cotainer">' + data + '<span class="msg_time">' + str_time + '</span></div></div>';
            $("#messageFormeight").append($.parseHTML(botHtml));

            $("#messageFormeight").animate({ scrollTop: $("#messageFormeight")[0].scrollHeight }, "slow");
        });
        event.preventDefault();
        $("#messageFormeight").animate({ scrollTop: $("#messageFormeight")[0].scrollHeight }, "slow");
    });
});

document.addEventListener('DOMContentLoaded', function () {
    $("#messageFormeight").animate({ scrollTop: $("#messageFormeight")[0].scrollHeight }, "slow");
});