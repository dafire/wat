function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

$(function () {
    $("button[data-task]").click(function (/*event*/) {
        const button = $(this);
        const url = button.closest("[data-task-url]").data("task-url");
        if (!url) {
            alert("task url missing");
            return;
        }
        button.addClass("loading");
        button.removeClass("positive negative");

        const success_action = function (value) {
            console.info("success", value);
            button.addClass("positive");
        };

        const error_action = function () {
            console.info("error");
            button.addClass("negative");
        };
        let data = button.data();
        data.type = "button";
        $.ajax({
            method: "POST",
            url: url,
            data: data,
        }).done(function (value) {
            if (value.status === "ok") {
                success_action(value);
            } else {
                error_action();
            }
        }).fail(function () {
            error_action();
        }).always(function (value) {
            if (value.text) {
                button.html(value.text);
            }
            if (value.append_text) {
                button.html(button.html() + value.append_text);
            }
            button.removeClass("loading");
        });
    });
});


