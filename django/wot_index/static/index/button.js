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
        button.addClass("loading disabled");
        button.removeClass("positive negative");

        const always_action = function (value) {
            if (value.text) {
                button.html(value.text);
            }
            if (value.append_text) {
                button.html(button.html() + value.append_text);
            }
            button.removeClass("loading disabled");
        };

        const error_action = function (value) {
            console.log("ERROR", value);
            button.addClass("negative");
            always_action(value);
        };

        const success_action = function (value) {
            console.log("SUCCESS", value);
            if (value.status === "ok") {
                console.info("success", value);
                button.addClass("positive");
                always_action(value);
            } else if (value.status === "async") {
                async_action(value);
            } else {
                error_action(value);
            }
        };

        const async_action = function (value) {
            console.log("ASYNC", value);
            setTimeout(function () {
                $.ajax({method: "GET", url: value.link})
                    .done(success_action)
                    .fail(error_action);
            }, 1000);
        };

        let data = button.data();
        data.type = "button";
        $.ajax({
            method: "POST",
            url: url,
            data: data,
        }).done(success_action)
            .fail(error_action);
    });
});


