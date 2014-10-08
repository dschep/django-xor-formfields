$(document).ready(function () {
    $('.mutually-exclusive-widget input[type=radio]').change(function () {
        $(this).next().removeAttr('disabled');
        $(this).parent().siblings().find('[name=' + $(this).attr('name') + ']').each(function () {
                $(this).next().attr('disabled', '');
        });
    });
    $('.mutually-exclusive-widget input[type=radio]:checked').change();
});
